# 🚀 How to Run the App

A step-by-step guide to run the Intelligent Health Management Platform on your
PC. You will need **two terminals open at the same time**: one for the backend
(Flask) and one for the frontend (Vue).

> ⚠️ Your project folder name contains a space (`TZC_Final_ Year_Project`), so
> every path below is wrapped in **double quotes**. Copy the commands exactly.

---

## 0. What you need installed

| Tool | Version | Check with |
|---|---|---|
| Python | 3.14+ | `python --version` |
| Node.js + npm | 18+ | `node --version` |
| MySQL | 8.0 (service `MySQL80` running) | open Task Manager → Services |

---

## 1. One-time MySQL setup

Create the database and the app user (you only do this **once**).
You will be asked for your **MySQL root password**.

```
cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project"
& 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe' -u root -p -e "CREATE DATABASE IF NOT EXISTS health_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'tzc_app'@'localhost' IDENTIFIED BY 'tzc_app_2026'; GRANT ALL PRIVILEGES ON health_platform.* TO 'tzc_app'@'localhost'; FLUSH PRIVILEGES; SELECT 'DB READY' AS status;"
```

✅ Success = you see `DB READY` in the output.

---

## 2. Backend (Flask) — first time only

```
cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding\backend"
python -m pip install -r requirements.txt
python seed.py
```

`seed.py` creates the 7 tables, inserts the food/exercise reference data and
the demo users. Safe to run again — it never duplicates data.

---

## 3. Start the backend — Terminal 1

```
cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding\backend"
python run.py
```

✅ Success = you see `Running on http://127.0.0.1:5000`.
**Keep this terminal open.**

---

## 4. Frontend (Vue) — first time only

Open a **second** terminal:

```
cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding\frontend"
npm install
```

---

## 5. Start the frontend — Terminal 2

```
cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding\frontend"
npm run dev
```

✅ Success = you see `Local: http://localhost:5173/`.
**Keep this terminal open too.**

---

## 6. Open the app

Go to **http://localhost:5173** in your browser.

| Demo account | Password | What it demonstrates |
|---|---|---|
| `demo` | `demo1234` | **Cold start** — no history, so recommendations use the content-based fallback. Log 5 meals and the engine switches to collaborative filtering. |
| `alice` / `bob` / `carol` / `david` | `demo1234` | Seeded with 14 days of history (populates the CF matrix) |

## ✨ Features you can show in the demo

* **Registration flow** — after creating an account you land on the **Profile**
  page to pick an avatar (emoji icons **or** upload your own picture, max 2 MB)
  and complete your body profile.
* **Dark / light theme** — toggle with the 🌙/☀️ button in the top-right
  corner (your choice is remembered; charts switch to a validated dark palette).
* **Mobile friendly** — the whole app adapts to phone screens: the menu
  collapses into a hamburger drawer, cards stack into one column, and log
  forms wrap.

---

## 🔁 Running again later

Skip steps 1, 2, 4 — just:

1. Terminal 1 → `cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding\backend"` → `python run.py`
2. Terminal 2 → `cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding\frontend"` → `npm run dev`
3. Open http://localhost:5173

---

## 🐞 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` when running `run.py` | Run `python -m pip install -r requirements.txt` again (step 2) |
| `sqlalchemy.exc.OperationalError: Can't connect to MySQL` | MySQL service not running — start `MySQL80` in Windows Services; or you skipped step 1 |
| `Access denied for user 'tzc_app'` | Re-run step 1 to recreate the user |
| `npm: command not found` | Node.js is not installed / not on PATH |
| Port 5000 or 5173 already in use | Close the old terminal window still running the server |
| npm error `EALLOWSCRIPTS` | The project already fixes this via `allowScripts` in `package.json` — make sure you run `npm install` from **inside** the `frontend` folder |

---

## 🧪 Optional: run the API test suite

With the backend running (step 3), in a third terminal:

```
cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding\backend"
python smoke_test.py
```

Expected result: `42 passed, 0 failed`.
