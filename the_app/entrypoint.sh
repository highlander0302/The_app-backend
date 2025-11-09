#!/bin/bash
set -e

MAX_ATTEMPTS=30  # number of times to check
SLEEP_TIME=1     # seconds between attempts

echo "Waiting for PostgreSQL to start..."

attempt=1
until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  if [ "$attempt" -ge "$MAX_ATTEMPTS" ]; then
    echo "❌ PostgreSQL did not start after $MAX_ATTEMPTS attempts. Exiting."
    exit 1
  fi
  echo "Attempt $attempt/$MAX_ATTEMPTS: PostgreSQL not ready yet..."
  attempt=$((attempt + 1))
  sleep "$SLEEP_TIME"
done
echo "PostgreSQL is up ✅"

if python manage.py showmigrations --plan | grep -q '\[X\]'; then
  echo "✅ DB already initialized"
  python manage.py migrate
else
  echo "📦 Running initial setup..."
  python manage.py migrate
  python manage.py loaddata db_data.json
fi

# Start Django app
echo "Django is running at http://localhost:8000"
exec python manage.py runserver 0.0.0.0:8000
