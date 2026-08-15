# Deploy Resume Builder on Render (free)

Step-by-step guide to host this Django app on [Render](https://render.com) using the **free** Web Service plan (and free Postgres).

> Free tier notes: services **sleep after inactivity**, cold starts take ~30–60s, and free Postgres may expire after 30/90 days depending on Render’s current free DB policy. Re-check [Render pricing](https://render.com/pricing) when you deploy.

## What you will create

1. A **PostgreSQL** database (free) — persistent data  
2. A **Web Service** that runs Gunicorn + Django  
3. Build step that installs Python + Node deps and builds Tailwind CSS  

## Prerequisites

- GitHub repo with this project (e.g. `NileshUrkude/Resume_Builder_site` or your fork)
- Free [Render](https://render.com) account (sign up with GitHub)
- This repo already includes production-friendly settings (`SECRET_KEY`, `DEBUG`, `DATABASE_URL`, WhiteNoise, Gunicorn)

## Architecture (free)

```text
Browser → Render Web Service (Gunicorn)
                ↓
         PostgreSQL (Render)
                ↓
         WhiteNoise serves /static/
```

Uploaded resume photos (`media/`) on the free disk **do not persist** across deploys. For a free demo, that is usually OK; for real users, use S3/R2 later.

---

## Step 1 — Push code to GitHub

Ensure `main` (or your deploy branch) is on GitHub and includes:

- `requirements.txt` (with `gunicorn`, `whitenoise`, `dj-database-url`, `psycopg2-binary`)
- `build.sh`
- Updated `Resume_Builder/settings.py` (env-based config)

```bash
git add -A
git status
git commit -m "Add Render deploy support and docs"
git push origin main
```

---

## Step 2 — Create a free Postgres database

1. Open [Render Dashboard](https://dashboard.render.com/)
2. **New +** → **PostgreSQL**
3. Settings:
   - **Name:** `resume-builder-db` (any name)
   - **Database:** leave default
   - **User:** leave default
   - **Region:** pick closest to you
   - **Plan:** **Free**
4. Click **Create Database**
5. Wait until status is **Available**
6. Open the DB → copy **Internal Database URL** (use this for the web service on Render)

---

## Step 3 — Create a free Web Service

1. **New +** → **Web Service**
2. Connect the GitHub repo `Resume_Builder_site`
3. Configure:

| Field | Value |
|-------|--------|
| **Name** | `resume-builder` (becomes `https://resume-builder.onrender.com`) |
| **Region** | Same as the database |
| **Branch** | `main` |
| **Runtime** | **Python 3** |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn Resume_Builder.wsgi:application` |
| **Instance type** | **Free** |

4. Under **Advanced** (or Environment):

### Environment variables

| Key | Value |
|-----|--------|
| `SECRET_KEY` | Generate a long random string (see below) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `resume-builder.onrender.com` (your real hostname; no `https://`) |
| `CSRF_TRUSTED_ORIGINS` | `https://resume-builder.onrender.com` |
| `DATABASE_URL` | Paste **Internal Database URL** from the Postgres service |
| `PYTHON_VERSION` | `3.12.8` (optional but recommended) |
| `NODE_VERSION` | `20` (**required** so `npm` works during build) |
| `DATABASE_SSL_REQUIRE` | `true` (for Render Postgres) |

Generate a secret key locally:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

5. Click **Create Web Service**
6. Watch the **Logs** tab until the build finishes and Gunicorn starts

First deploy often takes several minutes (npm + pip).

---

## Step 4 — Create an admin user (one time)

After the service is **Live**:

1. Open the web service → **Shell** (if available on your plan), **or** use a one-off from your laptop with `DATABASE_URL` set to the **External** DB URL temporarily.

**Option A — Render Shell** (if enabled):

```bash
python manage.py createsuperuser
```

**Option B — from your laptop** (use External Database URL from Render Postgres):

```bash
export DATABASE_URL="postgresql://..."   # External URL from Render
export SECRET_KEY="same-as-render"
export DEBUG="False"
export ALLOWED_HOSTS="localhost"
source venv/bin/activate   # if you have one
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

Then open:

`https://YOUR-SERVICE.onrender.com/admin/`

---

## Step 5 — Verify the live site

| Check | URL / action |
|-------|----------------|
| Landing | `https://YOUR-SERVICE.onrender.com/` |
| Signup | `/signup/` |
| Login | `/accounts/login/` |
| Editor | create a resume and edit |
| Templates | `/templates/` |
| PDF | Download PDF from dashboard |
| CSS/JS | page should look styled (WhiteNoise + build.sh) |

---

## How `build.sh` works

On each deploy Render runs:

```bash
#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
npm install
npm run build:css
# ensure vendor assets exist under static/vendor/
python manage.py collectstatic --no-input
python manage.py migrate
```

Start command:

```bash
gunicorn Resume_Builder.wsgi:application
```

---

## Updating the site later

```bash
git add -A
git commit -m "Your message"
git push origin main
```

Render auto-deploys from the connected branch (if Auto-Deploy is on).

---

## Free-tier limitations (important)

| Topic | Reality on free Render |
|-------|-------------------------|
| Sleep | App sleeps after ~15 min idle; first request is slow |
| Database | Free Postgres may be wiped/expired — back up if needed |
| Media uploads | Disk is ephemeral; photos can disappear on redeploy |
| Custom domain | Possible; set `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS` |
| SSL | HTTPS is provided by Render |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Build fails on `npm` | Ensure `build.sh` is executable (`chmod +x build.sh`) and committed; Render’s Python env includes Node for many blueprints — if npm missing, set env `NODE_VERSION=20` or use a native Node buildpack approach |
| `DisallowedHost` | Set `ALLOWED_HOSTS` to exact hostname (no `https://`) |
| CSRF verification failed | Set `CSRF_TRUSTED_ORIGINS=https://YOUR-SERVICE.onrender.com` |
| Static CSS missing | Confirm build ran `npm run build:css` and `collectstatic`; check `WHITENOISE` in settings |
| DB connection error | Use **Internal** Database URL on the web service; same region as DB |
| App crashes on boot | Open Logs; often bad `DATABASE_URL` or missing `SECRET_KEY` |
| 502 after sleep | Wait 30–60s for cold start, then refresh |

### Make `build.sh` executable (once, in git)

```bash
chmod +x build.sh
git add build.sh
git commit -m "Make build.sh executable"
git push
```

---

## Optional: `render.yaml` Blueprint

You can also deploy via **New → Blueprint** if `render.yaml` is in the repo. The included `render.yaml` defines a web service + Postgres and documents the same env vars (you still set `SECRET_KEY` in the dashboard).

---

## Local vs Render checklist

| Item | Local | Render free |
|------|-------|-------------|
| Command | `python manage.py runserver` | `gunicorn Resume_Builder.wsgi:application` |
| DB | SQLite `db.sqlite3` | Postgres via `DATABASE_URL` |
| Static | Django/dev + built Tailwind | WhiteNoise + `collectstatic` |
| Debug | `DEBUG=True` | `DEBUG=False` |
| Docs | See [LOCAL_SETUP.md](LOCAL_SETUP.md) | This file |
