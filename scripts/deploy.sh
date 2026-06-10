#!/bin/bash
set -e
cd "$(dirname "$0")/.."

git pull

bin/tailwindcss -i static/css/input.css -o static/css/main.css --minify

.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py compilemessages

sudo systemctl restart gunicorn
echo "Deploy done."
