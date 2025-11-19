#!/usr/bin/env bash
set -e

echo "🔁 Apply database migrations..."
python manage.py migrate --noinput

echo "🧹 Collect static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django with Gunicorn..."
exec gunicorn sample.wsgi:application --bind 0.0.0.0:8000