# REST API Documentation

Base URL (dev): `http://127.0.0.1:5000/api`
All endpoints return JSON. Protected endpoints require the header
`Authorization: Bearer <access_token>` (JWT, expires after 24 h).

## Health

| Method | Path         | Auth | Description            |
|--------|--------------|------|------------------------|
| GET    | /api/health  | —    | Liveness probe         |

## Auth

| Method | Path             | Auth | Body / Params                                    |
|--------|------------------|------|--------------------------------------------------|
| POST   | /api/auth/register | —  | `username, email, password` (+ optional `height, weight, age, gender`) → `{access_token, user}` |
| POST   | /api/auth/login  | —    | `username` or `email` + `password` → `{access_token, user}` |
| GET    | /api/auth/me     | JWT  | Current user (with active goal)                  |

## Profile

| Method | Path            | Auth | Body                                   |
|--------|-----------------|------|----------------------------------------|
| GET    | /api/profile    | JWT  | —                                      |
| PUT    | /api/profile    | JWT  | any of `height, weight, age, gender`   |

## Goals

| Method | Path                 | Auth | Body / Params                                              |
|--------|----------------------|------|------------------------------------------------------------|
| GET    | /api/goals           | JWT  | Active goal + last 10                                      |
| POST   | /api/goals           | JWT  | `goal_type` (lose/gain/maintain), optional `target_weight, daily_calorie_target, start_date, end_date`. If no calorie target, it is computed from the body profile (Mifflin-St Jeor). |
| PUT    | /api/goals/{id}      | JWT  | any goal field                                             |
| DELETE | /api/goals/{id}      | JWT  | —                                                          |

## Foods

| Method | Path                    | Auth | Params                                          |
|--------|-------------------------|------|-------------------------------------------------|
| GET    | /api/foods              | JWT  | `search` (name substring), `category`, `page`, `per_page` |
| GET    | /api/foods/{id}         | JWT  | —                                               |

## Exercises

| Method | Path                    | Auth | Params                          |
|--------|-------------------------|------|---------------------------------|
| GET    | /api/exercises          | JWT  | `search`, `category`            |
| GET    | /api/exercises/{id}     | JWT  | —                               |

## Meal Logs

| Method | Path                 | Auth | Body / Params                                                |
|--------|----------------------|------|--------------------------------------------------------------|
| POST   | /api/meals           | JWT  | `food_id, meal_type` (breakfast/lunch/dinner/snack), `quantity` (servings), optional `log_date` (YYYY-MM-DD, default today). Nutrition computed from the foods table. |
| GET    | /api/meals           | JWT  | `date` (YYYY-MM-DD, default today)                           |
| PUT    | /api/meals/{id}      | JWT  | `meal_type` and/or `quantity`                                |
| DELETE | /api/meals/{id}      | JWT  | —                                                            |

## Workout Logs

| Method | Path                   | Auth | Body / Params                                                |
|--------|------------------------|------|--------------------------------------------------------------|
| POST   | /api/workouts          | JWT  | `exercise_id, duration_min, intensity` (light/moderate/vigorous), optional `log_date`. Calories burned = MET × weight(kg) × hours × intensity factor. |
| GET    | /api/workouts          | JWT  | `date` (YYYY-MM-DD, default today)                           |
| DELETE | /api/workouts/{id}     | JWT  | —                                                            |

## Statistics (ECharts data)

| Method | Path             | Auth | Params                                                            |
|--------|------------------|------|-------------------------------------------------------------------|
| GET    | /api/stats/daily | JWT  | `date` → calories in/out, net, target, remaining, macros          |
| GET    | /api/stats/trends | JWT | `days` (default 30) → zero-filled per-day series                  |
| GET    | /api/stats/monthly | JWT | `months` (default 6) → per-month aggregates                       |

## Recommendations (hybrid engine)

| Method | Path                             | Auth | Params                                            |
|--------|----------------------------------|------|---------------------------------------------------|
| GET    | /api/recommendations             | JWT  | `type` (meal/workout), `limit` (default 5). Generates fresh recommendations (stored with a `reason`), returns `strategy` = `cf` (collaborative filtering) or `cb` (content-based cold-start fallback). |
| GET    | /api/recommendations/history     | JWT  | `type` (optional) — previously stored recommendations |

## Food Recognition (optional module)

| Method | Path               | Auth | Description                                        |
|--------|--------------------|------|----------------------------------------------------|
| POST   | /api/recognition   | JWT  | Returns 501 — optional ResNet module not enabled in the core build |

## Error format

All errors return `{"error": "<human-readable message>"}` with an
appropriate HTTP status (400 validation, 401 auth, 404 not found,
409 conflict, 501 not implemented).
