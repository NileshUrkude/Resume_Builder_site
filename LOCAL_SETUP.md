# Run Resume Builder locally

Complete steps to run this Django project on your machine (macOS, Linux, or Windows).

## Prerequisites

| Tool | Version | Why |
|------|---------|-----|
| Python | 3.10+ | Django app |
| pip | latest | Python packages |
| Node.js | 18+ | Tailwind CSS + vendor JS (Sortable, Alpine, HTMX, icons) |
| npm | comes with Node | `npm install` / `npm run build:css` |

Check versions:

```bash
python3 --version
node --version
npm --version
```

## 1. Clone and enter the project

```bash
git clone https://github.com/NileshUrkude/Resume_Builder_site.git
cd Resume_Builder_site
```

(Or use your fork / local copy.)

## 2. Create a Python virtual environment

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Install frontend packages and build CSS

Vendor JS/CSS (Alpine, HTMX, Sortable, Bootstrap Icons) and Tailwind must be built once:

```bash
npm install
npm run build:css
```

While developing CSS/HTML utilities, keep Tailwind watching:

```bash
npm run watch:css
```

If you skip `npm run build:css`, the UI will look broken (missing Tailwind classes).

## 4. Environment variables (optional for local)

Local defaults work out of the box (`DEBUG=True`, SQLite). Optional overrides:

```bash
# macOS / Linux
export SECRET_KEY="dev-only-change-me"
export DEBUG="True"
export ALLOWED_HOSTS="localhost,127.0.0.1"

# Windows PowerShell
$env:SECRET_KEY="dev-only-change-me"
$env:DEBUG="True"
$env:ALLOWED_HOSTS="localhost,127.0.0.1"
```

## 5. Database migrations

```bash
python manage.py migrate
```

This creates `db.sqlite3` in the project root.

## 6. (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

Admin UI: http://127.0.0.1:8000/admin/

## 7. Run the development server

```bash
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

| URL | Purpose |
|-----|---------|
| `/` | Landing |
| `/signup/` | Create account |
| `/accounts/login/` | Login |
| `/dashboard/` | Dashboard |
| `/create/` or `/resume/<id>/edit/` | Resume editor |
| `/templates/` | Template gallery |
| `/admin/` | Django admin |

## Quick start (copy-paste)

**macOS / Linux:**

```bash
cd Resume_Builder_site
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install && npm run build:css
python manage.py migrate
python manage.py runserver
```

**Windows (PowerShell):**

```powershell
cd Resume_Builder_site
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install; npm run build:css
python manage.py migrate
python manage.py runserver
```

## Common issues

| Problem | Fix |
|---------|-----|
| Styles look unstyled | Run `npm install && npm run build:css` |
| Icons missing | Ensure `static/vendor/bootstrap-icons/` exists after `npm install` (copy scripts in docs/deploy if needed) |
| `ModuleNotFoundError` | Activate `venv` and `pip install -r requirements.txt` |
| Port 8000 in use | `python manage.py runserver 8001` |
| PDF download fails | `xhtml2pdf` is required; reinstall from `requirements.txt` |
| Photo upload path | Files go to `media/`; create folder if missing: `mkdir -p media` |

## Project layout (useful paths)

```
Resume_Builder_site/
├── manage.py
├── requirements.txt
├── package.json
├── Resume_Builder/          # Django project settings
├── resumes/                 # App (models, views, forms)
├── templates/               # HTML templates
├── static/                  # CSS, JS, vendor assets
│   ├── css/
│   ├── js/
│   └── vendor/
├── media/                   # Uploaded photos (local)
└── db.sqlite3               # Local database (after migrate)
```

## Stopping

Press `Ctrl+C` in the terminal running `runserver`, then:

```bash
deactivate
```
