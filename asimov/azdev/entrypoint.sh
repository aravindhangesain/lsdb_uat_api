#!/bin/bash
#
# if [ "$DATABASE" = "postgres" ]
# then
#     echo "Waiting for postgres..."
#
#     while ! nc -z $DBHOST $DBPORT; do
#       sleep 0.1
#     done
#
#     echo "PostgreSQL started"
# fi
# python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --noinput

gunicorn -b 0.0.0.0:80 --timeout 1200 --workers=4 backend.wsgi:application --access-logfile '-' --error-logfile '-'

# exec "$@"
