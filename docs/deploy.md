# 🚢 Deployment Guide — put the platform on the Internet

This guide takes the app from your PC to a public server reachable from any
country, using **Docker Compose** on a small cloud VM.

```
                        ┌──────────────────────── VM (Ubuntu) ────────────────────────┐
                        │                                                              │
Internet ──► :80/:443 ──► host nginx (+certbot HTTPS, optional)                        │
                        │      │                                                       │
                        │      ▼ :8080                                                 │
                        │   frontend container  (nginx: serves Vue build,              │
                        │                        proxies /api and /uploads)            │
                        │      │ /api, /uploads                                       │
                        │      ▼ :8000                                                 │
                        │   backend container   (waitress WSGI + Flask)                │
                        │      │                                                       │
                        │      ▼ :3306                                                 │
                        │   db container        (MySQL 8, data on a named volume)      │
                        └──────────────────────────────────────────────────────────────┘
```

All three services run from one `docker compose up` command; secrets live in a
gitignored `.env` file.

---

## Step 1 — Buy the server (~24–34 元/month, payable with Alipay)

1. Go to Aliyun (aliyun.com) → **轻量应用服务器 (Lightweight App Server)** or
   Tencent Cloud → **轻量应用服务器 (Lighthouse)**.
2. Pick region **Hong Kong** or **Singapore** (tested from other countries;
   mainland regions require ICP filing — these do not).
3. Smallest plan is enough: **2 GB RAM / 2-core / 40 GB SSD**.
4. System image: **Ubuntu 22.04 LTS** (or 24.04).
5. Set a **root password** (or an SSH key pair) when creating it.
6. In the cloud console firewall (安全组/防火墙), open ports: **22** (SSH),
   **80** (HTTP), **443** (HTTPS). Keep everything else closed.

You get a public IP like `47.242.xx.xx` — that's your server address.

## Step 2 — Connect over SSH

On your PC (Windows PowerShell has `ssh` built in):

```
ssh root@47.242.xx.xx
```

Type the root password you set in the console. You're now on the server.

## Step 3 — Install Docker

On the server, run:

```
curl -fsSL https://get.docker.com | sh
```

Then verify:

```
docker --version && docker compose version
```

## Step 4 — Get the code onto the server

From your public GitHub repo:

```
cd /opt
git clone https://github.com/<your-username>/<your-repo>.git health-platform
cd health-platform
```

(Later, after code changes: `git pull` inside this folder and re-run step 6.)

## Step 5 — Configure secrets

```
cp .env.example .env
nano .env
```

Change **every** value. Generate a strong JWT secret on any machine with:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

Set strong MySQL passwords (never reuse the local dev password
`tzc_app_2026` — it is public in the repo and only meant for localhost).

## Step 6 — Start the stack

```
docker compose up -d --build
```

First boot takes 1–3 minutes (images are downloaded, MySQL initializes, the
backend seeds the reference data). The frontend is prebuilt and committed as
`frontend/dist/` (build it on a dev machine with `npm run build`), so the
server build never runs npm install / vite build. Watch progress with:

```
docker compose logs -f backend
```

Ready when you see waitress listening on 8000. Verify:

```
curl http://localhost/api/health
# -> {"service":"health-platform-api","status":"ok"}
```

Now open **http://47.242.xx.xx** in your browser from any device/country.
Demo login: `demo` / `demo1234`.

## Step 7 — Run the test suite against production

```
docker compose exec backend python smoke_test.py http://127.0.0.1:8000
```

(The base URL argument is required in the container — the API listens on
8000 there, not the dev server's 5000.)

Expected: `42 passed, 0 failed`.

## Step 8 — Domain + HTTPS (recommended for the defense)

Plain `http://IP` works but browsers label it "Not secure". For HTTPS you need
a domain name (~30–50 元/year on Aliyun, e.g. `health-demo.top`):

1. Buy the domain in the same cloud console, add an **A record** pointing
   `@` (and `www`) to your server IP. (Overseas-region servers don't need
   备案 for the server; a mainland-registered domain pointing at an overseas
   server is fine for a demo.)
2. Tell Docker to keep the frontend off port 80 — in `.env` add:
   `FRONTEND_PORT=8080`, then `docker compose up -d`.
3. Install certbot on the host:
   ```
   apt update && apt install -y nginx certbot python3-certbot-nginx
   ```
   (Disable the host nginx service until configured: `systemctl stop nginx`.)
4. Copy the repo's `deploy/nginx-host.conf` to `/etc/nginx/sites-available/health`,
   replace `health.example.com` with your domain, enable it:
   ```
   cp deploy/nginx-host.conf /etc/nginx/sites-available/health
   sed -i 's/health.example.com/YOUR-DOMAIN/g' /etc/nginx/sites-available/health
   ln -s /etc/nginx/sites-available/health /etc/nginx/sites-enabled/health
   rm /etc/nginx/sites-enabled/default
   nginx -t && systemctl start nginx
   ```
5. Get the certificate (auto-configures HTTPS + redirect):
   ```
   certbot --nginx -d YOUR-DOMAIN -d www.YOUR-DOMAIN
   ```
6. Done — **https://YOUR-DOMAIN** is live with a valid certificate that
   auto-renews.

## Day-to-day operations

| Task | Command (run in `/opt/health-platform`) |
|---|---|
| View logs | `docker compose logs -f backend` |
| Update after `git pull` | `docker compose up -d --build` |
| Restart one service | `docker compose restart backend` |
| Backup the database | `docker compose exec db mysqldump -u tzc_app -p"$MYSQL_PASSWORD" health_platform > backup.sql` |
| See status | `docker compose ps` |

## Security checklist (mention these in the defense)

- [x] Secrets in `.env`, never in git (`JWT_SECRET_KEY`, DB passwords)
- [x] Default localhost password not reused in production
- [x] Firewall opens only 22 / 80 / 443
- [x] HTTPS via Let's Encrypt (auto-renew)
- [x] Backend runs behind waitress (production WSGI server), not Flask's dev server
- [x] Avatar uploads: type + 2 MB size limits, UUID filenames, path-traversal-safe serving

## Troubleshooting

| Problem | Fix |
|---|---|
| `docker compose` not found | Old Docker install — use `docker-compose` (hyphen) or reinstall with `get.docker.com` |
| MySQL container keeps restarting | Check `.env` has values, no spaces in passwords; `docker compose logs db` |
| Site works on server but not from outside | Cloud console firewall missing port 80; or frontend bound to localhost |
| `Access denied` from the app | `.env` changed after first boot — MySQL keeps the first password; `docker compose down -v` (erases data) or recreate the user |
| Uploads disappear after update | The `uploads_data` volume must stay attached (it does — don't use `-v` on rebuilds) |
