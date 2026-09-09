# Resume Builder

A Django web app to create, preview, and download professional resumes in multiple templates.

## Features

- User signup and login
- Resume editor with education, experience, projects, skills, certificates, and achievements
- 6 resume templates (classic, modern, minimal, sidebar, timeline, compact)
- PDF export per template
- **Tailwind CSS** (npm build, not CDN)
- **Dark mode** toggle (saved in browser)
- **Print-friendly** resume preview (A4 layout)

## Requirements

- Python 3.10+
- Node.js 18+ (for Tailwind CSS build)
- pip

## Setup and run

```powershell
# 1. Go to project folder
cd d:\notes\Resume_Builder

# 2. Python virtual environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 3. Build Tailwind CSS (required before first run)
# Option A — with Node.js:
npm install
npm run build:css

# Option B — without npm (Windows standalone CLI):
# Invoke-WebRequest -Uri "https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.17/tailwindcss-windows-x64.exe" -OutFile tailwindcss.exe
# .\tailwindcss.exe -i ./static/src/input.css -o ./static/css/tailwind.css --minify

# 4. Database
python manage.py migrate

# 5. (Optional) Admin user
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

## Deploy to Render

This repository includes `render.yaml` for a Render web service named
`my_resume_builder` and a managed PostgreSQL database. From the Render
dashboard:

1. Push the project to GitHub or GitLab.
2. Select **New +** -> **Blueprint** and connect the repository.
3. Confirm the blueprint name `my_resume_builder`, then apply it.
4. After the first deploy, open **Environment** and set
  `CSRF_TRUSTED_ORIGINS` to the exact public URL, such as
  `https://my-resume-builder.onrender.com`.
5. Create an admin account from **Shell** with
  `python manage.py createsuperuser`.

The blueprint installs the Linux runtime dependencies from
`requirements-render.txt`, builds Tailwind CSS, collects static files, runs
migrations, and starts Gunicorn. `DATABASE_URL` and
`DJANGO_SECRET_KEY` are generated/configured by Render. Uploaded media files
are stored on the web service filesystem; configure a persistent disk or
object storage before relying on uploads in production.

### After editing HTML/CSS classes

```powershell
npm run build:css
# Or watch for changes:
npm run watch:css
```

## Dark mode

Click the **sun/moon** icon in the navbar. Your choice is stored in `localStorage` and respects system preference on first visit.

## Print resume

On **Dashboard** or **Template preview**:

1. Click **Print resume** / **Print preview**
2. Browser print dialog opens with nav/sidebar hidden
3. Resume is formatted for **A4** paper

You can also use **Download PDF** for a file export.

## Main URLs

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/signup/` | Register |
| `/accounts/login/` | Login |
| `/dashboard/` | Dashboard |
| `/create/` | Edit resume |
| `/view/t1/` … `/view/t6/` | Preview templates |
| `/download/t1/` … `/download/t6/` | Download PDF |

## Tech stack

- Django 5.2
- SQLite
- Tailwind CSS 3 (npm)
- xhtml2pdf

## Project layout (frontend)

```
static/
  src/input.css    # Tailwind source + print styles
  css/tailwind.css # Built output (run npm run build:css)
  js/theme.js      # Dark mode toggle
templates/         # Django HTML
```

## Author

Nilesh Urkude — nileshburkude@gmail.com
