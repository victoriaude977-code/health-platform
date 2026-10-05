# 📦 Git & GitHub Guide — get the code from your PC to the server

`deploy.md` step 4 assumes the code is already in a **public GitHub repo**.
This guide does that part. It covers exactly three machines:

```
PC (PowerShell)  ──git push──►  GitHub.com  ──git clone──►  Server (SSH, /opt/health-platform)
```

---

## Step 1 — Install Git on the PC (one time)

On **your PC**, in PowerShell:

```
winget install --id Git.Git -e --source winget
```

Then **close PowerShell and open a new window** (so `git` is found).
Verify:

```
git --version
```

The installer includes **Git Credential Manager**, which makes logging in to
GitHub just a browser pop-up — no tokens to copy by hand.

---

## Step 2 — Create the repo on GitHub

1. Go to [github.com](https://github.com) and log in.
2. Click **New repository**.
3. Name: `health-platform` (or anything you like).
4. **Public** — the server needs to clone it without a password, and
   deploy.md is written for a public repo.
5. **Do NOT** tick "Add a README" (an empty repo is easiest to push into).
6. Click **Create repository**. Copy the URL it shows you:
   `https://github.com/<your-username>/health-platform.git`

---

## Step 3 — Which folder do you push? The `coding` folder

Push **`coding`** — it is the *entire* project:

```
coding\
├── backend\            Flask API + tests + Dockerfile
├── frontend\           Vue 3 app + Dockerfile
├── database\           schema.sql
├── deploy\             nginx-host.conf (HTTPS setup)
├── docs\               api.md, deploy.md
├── docker-compose.yml  runs the whole stack on the server
├── .env.example        secret template (real .env stays out of git)
└── .gitignore
```

The repo root must be `coding` itself — `docker-compose.yml` and every path in
deploy.md assume it.

**Do NOT push** the Desktop folder (`TZC_Final_ Year_Project`) — that contains
your thesis documents, proposals and PPTs, which don't belong in the code repo.

**You don't need to worry about what's inside `coding`** — the `.gitignore`
already excludes everything that must not ship:

| Excluded | Why |
|---|---|
| `node_modules/`, `dist/` | ~15,000 dependency/build files; rebuilt by Docker |
| `.env` | real passwords — never in git |
| `backend/uploads/` | user avatars |
| `__pycache__/`, `.idea/` | junk |

So `git add .` is safe: git will only take the source files.

---

## Step 4 — First push (PowerShell, on your PC)

```powershell
cd "C:\Users\Princess\Desktop\TZC_Final_ Year_Project\coding"
git init -b main
git add .
git commit -m "Initial commit: full platform (backend, frontend, deploy)"
git remote add origin https://github.com/<your-username>/health-platform.git
git push -u origin main
```

The first push opens a browser window: log in to GitHub, click **Authorize**.
Check github.com — your files should be there.

---

## Step 5 — Back to the server (deploy.md step 4 now works)

In the **SSH window on the server**:

```
cd /opt
git clone https://github.com/<your-username>/health-platform.git health-platform
cd health-platform
```

Because the repo is public, no login is needed on the server. Continue with
deploy.md step 5 (configure `.env`).

---

## Everyday workflow after code changes

| Where | What |
|---|---|
| PC | `cd ...\coding` → `git add .` → `git commit -m "what changed"` → `git push` |
| Server | `cd /opt/health-platform` → `git pull` → `docker compose up -d --build` |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `git : The term 'git' is not recognized` | Close and reopen PowerShell after installing; install Git first |
| `remote: Permission denied` / push asks for password | Use the browser sign-in (Git Credential Manager); or create a **Personal Access Token** on GitHub → Settings → Developer settings, paste it as the password |
| `failed to push ... non-fast-forward` | The repo was created with a README — run `git pull --rebase origin main` then `git push` again |
| Server: `fatal: could not read Username` | The repo is private — set it to Public (Settings → General → Danger Zone → Change visibility) or use a token on the server |
| Pushed a file that should be private (e.g. `.env`) | Change the password **immediately**, then `git rm --cached .env`, commit, push |
