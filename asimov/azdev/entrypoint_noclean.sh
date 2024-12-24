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
# python manage.py migrate
# python manage.py collectstatic --noinput
#
# python manage.py loaddata lsdb/fixtures/init.json
# python manage.py loaddata lsdb/fixtures/auth.json
# python manage.py loaddata lsdb/fixtures/post-auth-init.json
# python manage.py loaddata lsdb/fixtures/definitions.json
# python manage.py loaddata lsdb/fixtures/test.json
# python manage.py loaddata fixtures/prod_backup.json
gunicorn -b 0.0.0.0:80 backend.wsgi:application

# exec "$@"
