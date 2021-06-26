#!/bin/bash

set -e

# This will clean up old md5 digested files since they are volume persisted.
# If you want to persist older versions of any of these files to avoid breaking
# external links outside of your domain then feel free remove this line.
# rm -rf /app/public_collected/css /app/public_collected/js \
#        /app/public_collected/fonts /app/public_collected/images

# # Always keep this here as it ensures the built and digested assets get copied
# # into the correct location. This avoids them getting clobbered by any volumes.
# cp -a /public_collected /app
python manage.py collectstatic --noinput
python manage.py migrate

exec "$@"