set -e

python manage.py migrate
python manage.py collectstatic --no-input
python manage.py runserver 0.0.0.0:8000

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 5 \
  --timeout 30