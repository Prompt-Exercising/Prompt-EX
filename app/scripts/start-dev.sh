set -e

python manage.py migrate
python manage.py collectstatic --no-input
daphne -b 0.0.0.0 -p 8001 config.asgi:application &

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 5 \
  --timeout 30