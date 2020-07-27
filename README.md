# freedb
An easy to use cloud database



# deploy 
## docker 
Put a prod_settings.py at the current folder.

    import os
    from freedb_site.settings import *

    SECRET_KEY = 'YOURSECRETCODEHERE'

    DEBUG = False

    ALLOWED_HOSTS = [
        '*'
    ]

    MONGODB_URL = os.environ.get('MONGODB_URL')

    STATIC_ROOT = 'staticfiles'

    import dj_database_url 
    prod_db  =  dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(prod_db)

docker-compose.yml

    volumes:
        - ./prod_settings.py:/app/prod_settings.py:Z
    environment:
        DJANGO_SETTINGS_MODULE: prod_settings