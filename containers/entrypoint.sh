#!/usr/bin/env bash
set -e

echo "🔁 Apply database migrations..."
python manage.py migrate --noinput

echo "🧹 Collect static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Django with Gunicorn..."
# Gunicorn を worker=2にして安定稼働
# workerを1から2に変更(片方が重くなった場合、もう片方で処理)
exec gunicorn sample.wsgi:application \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --forwarded-allow-ips="*"