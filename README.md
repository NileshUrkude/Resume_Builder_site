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

Full local instructions: **[LOCAL_SETUP.md](LOCAL_SETUP.md)**  
Free deploy on Render: **[RENDER_DEPLOY.md](RENDER_DEPLOY.md)**

```bash
# Quick local start (macOS/Linux)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install && npm run build:css
python manage.py migrate
python manage.py runserver
```

Open: **http://127.0.0.1:8000/**

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
