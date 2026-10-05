# Intelligent Health Management Platform

**基于Vue.js和Flask的智能健康管理平台** — final-year project.
Track meals & workouts, visualize trends, and receive personalized,
explainable recommendations from a hybrid recommendation engine.

> 📖 **Just want to run it?** See [HOW_TO_RUN.md](HOW_TO_RUN.md).

| Layer | Tech |
|---|---|
| Frontend | Vue.js 3 (Vite), Element Plus, Vuex, Vue Router, Axios, ECharts |
| Backend | Python 3.14, Flask, Flask-JWT-Extended, SQLAlchemy, scikit-learn-compatible recommender (numpy) |
| Database | MySQL 8 (7 tables), PyMySQL driver |
| Engine | Switching hybrid: item-based collaborative filtering → content-based fallback on cold start, goal-constrained, with a `reason` per recommendation |

## Repository layout

```
coding/
├── backend/            Flask REST API
│   ├── app/
│   │   ├── models/     7 SQLAlchemy models (users, goals, meal_logs,
│   │   │                workout_logs, foods, exercises, recommendations)
│   │   ├── routes/     auth, profile, foods, exercises, meals, workouts,
│   │   │                goals, stats, recommendations, recognition
│   │   ├── services/   recommender.py (hybrid engine)
│   │   └── utils/      JWT helpers, validation, calorie math
│   ├── config.py       env-var-driven configuration
│   ├── run.py          entry point (dev server)
│   ├── seed.py         reference data + demo users
│   └── smoke_test.py   42-check API test suite (stdlib only)
├── frontend/           Vue.js SPA
│   └── src/
│       ├── api/        Axios clients        ├── store/  Vuex modules
│       ├── router/     route guards         ├── components/ NavBar
│       └── views/      Login, Register, Dashboard, Goal, Meals, Workouts,
│                       Charts, Recommendations, Profile
├── database/schema.sql reference MySQL DDL
├── docs/api.md         REST API documentation
├── docs/deploy.md      cloud deployment guide (Aliyun/Tencent VM + Docker)
├── docker-compose.yml  production stack: MySQL + Flask(waitress) + nginx
├── Dockerfile          one in backend/ and one in frontend/ (multi-stage)
├── .env.example        production secret template (copy to .env, never commit)
└── deploy/             host nginx config for the HTTPS step
```

## One-time setup

1. **MySQL** (running locally as service MySQL80). Create the database and
   app user once:
   ```
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS health_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'tzc_app'@'localhost' IDENTIFIED BY 'tzc_app_2026'; GRANT ALL PRIVILEGES ON health_platform.* TO 'tzc_app'@'localhost'; FLUSH PRIVILEGES;"
   ```
2. **Backend** (PyCharm → open the `backend` folder):
   ```
   python -m pip install -r requirements.txt
   python seed.py      # creates tables + reference data + demo users
   python run.py       # starts http://127.0.0.1:5000
   ```
3. **Frontend** (PyCharm terminal → open the `frontend` folder):
   ```
   npm install
   npm run dev         # starts http://localhost:5173 (proxies /api to Flask)
   ```
   Then open http://localhost:5173 in the browser.

## Demo accounts

| User | Password | Purpose |
|---|---|---|
| `demo` | `demo1234` | Cold-start demo — no history, recommendations use content-based fallback; after 5 meal logs the engine switches to collaborative filtering |
| `alice` `bob` `carol` `david` | `demo1234` | Seeded with 14 days of history (different diets/workouts) to populate the CF matrix |

## Tests

```bash
python smoke_test.py          # against the running backend
```

## Deployment (production)

The repo ships as a complete Docker Compose stack — MySQL 8, Flask behind
waitress, and nginx serving the Vue build with same-origin `/api` and
`/uploads` proxying. Full step-by-step (server purchase, Docker install,
`.env` secrets, HTTPS with certbot, backups, security checklist) lives in
**[docs/deploy.md](docs/deploy.md)**.

## Machine-specific notes (this PC)

* `SQLAlchemy==2.0.43` is pinned in `requirements.txt` because the 2.1.x
  C-extension `_util_cy.pyd` is blocked by the Windows Application Control
  policy; 2.0.43 is a pure-Python wheel.
* `frontend/package.json` declares `"allowScripts": { "esbuild": true }` so
  `npm install` works under the machine-wide npm script allowlist.
* All settings are overridable via environment variables / `backend/.env`
  (`DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ORIGINS`) — the same hook the
  Docker production stack uses (see [docs/deploy.md](docs/deploy.md)).
