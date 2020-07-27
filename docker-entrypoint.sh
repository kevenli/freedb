#!/bin/sh
PYTHON="${PYTHON:-python}"
set -e
DATABASE_URL='' $PYTHON manage.py collectstatic --noinput
$PYTHON manage.py migrate --noinput
exec "$@"