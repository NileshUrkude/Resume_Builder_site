#!/usr/bin/env bash
# Render (and similar PaaS) build script for Resume Builder
set -o errexit

echo "==> Installing Python dependencies"
pip install -r requirements.txt

echo "==> Installing Node dependencies"
npm install

echo "==> Building Tailwind CSS"
npm run build:css

echo "==> Syncing frontend vendor assets into static/"
mkdir -p static/vendor/bootstrap-icons/fonts
cp -f node_modules/htmx.org/dist/htmx.min.js static/vendor/htmx.min.js
cp -f node_modules/alpinejs/dist/cdn.min.js static/vendor/alpine.min.js
cp -f node_modules/sortablejs/Sortable.min.js static/vendor/sortable.min.js
cp -f node_modules/bootstrap-icons/font/bootstrap-icons.min.css static/vendor/bootstrap-icons/
cp -f node_modules/bootstrap-icons/font/fonts/* static/vendor/bootstrap-icons/fonts/

echo "==> Collecting static files"
python manage.py collectstatic --no-input

echo "==> Running migrations"
python manage.py migrate --no-input

echo "==> Build finished"
