#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load base env, then local overrides on top
set -a
[ -f .env ]       && source .env
[ -f .env.local ] && source .env.local
set +a

# Activate virtual environment
source .venv/bin/activate

# Build CSS if missing or if input.css is newer
if [ ! -f static/css/main.css ] || [ static/css/input.css -nt static/css/main.css ]; then
  echo "Building CSS..."
  tailwindcss -i static/css/input.css -o static/css/main.css --minify
fi

# Apply any pending migrations
python manage.py migrate --run-syncdb 2>/dev/null || python manage.py migrate

# Free port 8000 if already in use
fuser -k 8000/tcp 2>/dev/null || true

echo "Starting server at http://127.0.0.1:8000"
python manage.py runserver 0.0.0.0:8000
