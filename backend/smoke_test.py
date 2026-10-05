"""
API smoke test: exercises every endpoint end-to-end against a running server.

    python smoke_test.py [base_url]

Uses only the standard library. Covers: auth (register/login/JWT), profile
(including preset & uploaded avatars), foods/exercises, goals (auto calorie
target), meal & workout logging (MET calculation), statistics, and the
recommendation engine's cold-start -> CF switch. Exit code 0 = all checks
passed.
"""
import json
import random
import string
import sys
import urllib.error
import urllib.request
from datetime import date

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000"

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {label}")
    else:
        failed += 1
        print(f"  FAIL  {label}  {detail}")


def call(method, path, token=None, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def call_upload(path, token, filename, filedata, content_type="image/png"):
    """Multipart file upload (stdlib only: hand-built multipart body)."""
    boundary = "----smoketestboundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + filedata + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + path, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def call_raw(path, token=None):
    """GET returning raw bytes (for static file serving checks)."""
    req = urllib.request.Request(BASE + path, method="GET")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, {}, b""


def main():
    today = date.today().isoformat()
    print(f"Smoke test against {BASE} ({today})\n")

    # ---- health -----------------------------------------------------------
    status, body = call("GET", "/api/health")
    check("health endpoint", status == 200 and body.get("status") == "ok", body)

    # ---- auth -------------------------------------------------------------
    # Unique per run (timestamp + random tail) so consecutive runs and leftover
    # users in MySQL never collide.
    uname = (f"smoke_{date.today().strftime('%H%M%S')}_"
             + "".join(random.choices(string.ascii_lowercase, k=4)))
    status, body = call("POST", "/api/auth/register", body={
        "username": uname, "email": f"{uname}@test.local", "password": "secret123",
        "height": 168, "weight": 60, "age": 23, "gender": "female",
    })
    check("register new user", status == 201, body)
    token = body.get("access_token")
    check("register returns JWT", bool(token))

    status, body = call("POST", "/api/auth/register", body={
        "username": uname, "email": f"{uname}@test.local", "password": "secret123"})
    check("duplicate register rejected (409)", status == 409, body)

    status, body = call("POST", "/api/auth/login",
                        body={"username": uname, "password": "wrong"})
    check("wrong password rejected (401)", status == 401, body)

    status, body = call("POST", "/api/auth/login",
                        body={"username": uname, "password": "secret123"})
    check("login returns token", status == 200 and body.get("access_token"), body)

    status, body = call("GET", "/api/auth/me", token=token)
    check("me endpoint (JWT protected)", status == 200 and body["user"]["username"] == uname, body)

    status, body = call("GET", "/api/auth/me")
    check("me without token rejected (401)", status == 401, body)

    # ---- profile ----------------------------------------------------------
    status, body = call("PUT", "/api/profile", token=token, body={"weight": 61.5})
    check("update profile weight", status == 200 and body["user"]["weight"] == 61.5, body)

    # ---- avatar: preset icon ----------------------------------------------
    status, body = call("PUT", "/api/profile", token=token, body={"avatar": "preset:fox"})
    check("set preset avatar", status == 200 and body["user"]["avatar"] == "preset:fox", body)

    status, body = call("PUT", "/api/profile", token=token, body={"avatar": "https://evil.example/x.png"})
    check("reject non-preset avatar value (400)", status == 400, body)

    # ---- avatar: picture upload -------------------------------------------
    png = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000d4944415478da63fccfc0500f000485018084a98c21"
        "0000000049454e44ae426082")
    status, body = call_upload("/api/profile/avatar", token, "me.png", png)
    check("upload avatar picture", status == 200, body)
    avatar_path = body.get("user", {}).get("avatar", "")
    check("avatar stored as upload path", avatar_path.startswith("/uploads/avatars/"), avatar_path)

    status, headers, data = call_raw(avatar_path)
    check("uploaded avatar is served", status == 200 and data == png, f"{status}, {len(data)} bytes")
    check("uploaded avatar content-type", headers.get("Content-Type", "").startswith("image/png"),
          headers.get("Content-Type"))

    status, body = call_upload("/api/profile/avatar", token, "me.txt", b"not an image",
                               content_type="text/plain")
    check("reject non-image upload (400)", status == 400, body)

    status, body = call("PUT", "/api/profile", token=token, body={"avatar": ""})
    check("clear avatar", status == 200 and body["user"]["avatar"] is None, body)

    # ---- reference data ---------------------------------------------------
    status, body = call("GET", "/api/foods?search=rice", token=token)
    check("food search returns items", status == 200 and len(body["items"]) >= 1, body)
    rice = next((f for f in body["items"] if "rice" in f["name"].lower()), None)
    check("rice in food database", rice is not None)

    status, body = call("GET", "/api/exercises?category=cardio", token=token)
    check("exercises by category", status == 200 and len(body["items"]) >= 1, body)
    running = next((e for e in body["items"] if "unning" in e["name"]), None)
    check("running in exercise database", running is not None)

    # ---- goals (auto calorie target via Mifflin-St Jeor) ------------------
    status, body = call("POST", "/api/goals", token=token, body={
        "goal_type": "lose", "target_weight": 55,
        "start_date": today,
        "end_date": "2027-01-01",
    })
    check("create goal (auto calorie target)", status == 201, body)
    goal = body.get("goal", {})
    check("auto target is plausible (1100-2500 kcal)",
          goal.get("daily_calorie_target", 0) >= 1100 and
          goal.get("daily_calorie_target", 0) <= 2500, goal)

    # ---- meal logging -----------------------------------------------------
    status, body = call("POST", "/api/meals", token=token, body={
        "food_id": rice["id"], "meal_type": "lunch", "quantity": 1.5})
    check("log meal", status == 201, body)
    meal = body.get("log", {})
    check("meal calories = food kcal x quantity",
          abs(meal.get("calories", 0) - rice["calories"] * 1.5) < 0.2, meal)

    status, body = call("POST", "/api/meals", token=token, body={
        "food_id": rice["id"], "meal_type": "brunch", "quantity": 1})
    check("invalid meal_type rejected (400)", status == 400, body)

    # ---- workout logging (MET formula) ------------------------------------
    status, body = call("POST", "/api/workouts", token=token, body={
        "exercise_id": running["id"], "duration_min": 30, "intensity": "moderate"})
    check("log workout", status == 201, body)
    workout = body.get("log", {})
    expected_burn = running["met_value"] * 61.5 * 0.5  # MET x kg x hours
    check("calories burned = MET x weight x hours",
          abs(workout.get("calories_burned", 0) - expected_burn) < 1.5,
          f"{workout.get('calories_burned')} vs {expected_burn}")

    # ---- statistics -------------------------------------------------------
    status, body = call("GET", f"/api/stats/daily?date={today}", token=token)
    check("daily stats", status == 200 and body["calories_in"] > 0 and body["calories_out"] > 0, body)
    check("daily stats include goal target", body.get("daily_target") == goal.get("daily_calorie_target"), body)

    status, body = call("GET", "/api/stats/trends?days=7", token=token)
    check("trends series (7 zero-filled days)",
          status == 200 and len(body["series"]) == 7, body)

    status, body = call("GET", "/api/stats/monthly?months=3", token=token)
    check("monthly series (3 months)", status == 200 and len(body["series"]) == 3, body)

    # ---- recommendations: cold start -> CF switch -------------------------
    status, body = call("GET", "/api/recommendations?type=meal&limit=5", token=token)
    check("meal recommendations (cold start)", status == 200 and len(body["items"]) >= 1, body)
    check("cold start uses content-based (cb)", body.get("strategy") == "cb", body.get("strategy"))
    check("every meal rec has a reason", all(r.get("reason") for r in body["items"]))

    status, body = call("GET", "/api/recommendations?type=workout&limit=5", token=token)
    check("workout recommendations (cold start)", status == 200 and len(body["items"]) >= 1, body)
    check("workout rec has a reason", all(r.get("reason") for r in body["items"]))

    # Log 4 more meals so the user has 5 total -> CF should switch on.
    foods_status, foods = call("GET", "/api/foods?search=egg", token=token)
    egg = next((f for f in foods["items"] if "egg" in f["name"].lower()), foods["items"][0])
    for i in range(4):
        status, _ = call("POST", "/api/meals", token=token, body={
            "food_id": egg["id"], "meal_type": "snack", "quantity": 1})
    check("logged 4 more meals", status == 201)

    status, body = call("GET", "/api/recommendations?type=meal&limit=5", token=token)
    check("with 5 meals engine switches to CF", body.get("strategy") == "cf",
          body.get("strategy", "") + f" / {body.get('explanation', '')}")
    check("CF recs still have reasons", all(r.get("reason") for r in body["items"]))

    status, body = call("GET", "/api/recommendations/history?type=meal", token=token)
    check("recommendation history stored", status == 200 and len(body["items"]) >= 1, body)

    # ---- cleanup: delete today's logs --------------------------------------
    status, meals = call("GET", f"/api/meals?date={today}", token=token)
    for m in meals["items"]:
        call("DELETE", f"/api/meals/{m['id']}", token=token)
    status, workouts = call("GET", f"/api/workouts?date={today}", token=token)
    for w in workouts["items"]:
        call("DELETE", f"/api/workouts/{w['id']}", token=token)
    check("cleanup deleted logs", True)

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
