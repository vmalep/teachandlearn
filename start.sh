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

# Always rebuild CSS — Tailwind scans templates for classes used, so a
# template-only change (new utility classes, no input.css edit) needs a
# rebuild too, not just when input.css itself is newer.
# Prefer the project-local binary; fall back to a global install (some
# dev machines have tailwindcss on PATH instead of a local bin/).
TAILWIND_BIN="./bin/tailwindcss"
[ -x "$TAILWIND_BIN" ] || TAILWIND_BIN="tailwindcss"
echo "Building CSS..."
"$TAILWIND_BIN" -i static/css/input.css -o static/css/main.css --minify

# Apply any pending migrations
python manage.py migrate --run-syncdb 2>/dev/null || python manage.py migrate

# Free port 8000 if already in use
fuser -k 8000/tcp 2>/dev/null || true

echo "Starting server at http://127.0.0.1:8000"
python manage.py runserver 0.0.0.0:8000
