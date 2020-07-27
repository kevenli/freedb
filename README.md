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

    # using pymysql
    import pymysql
    pymysql.install_as_MySQLdb()

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

example docker-compose

    version: '3'
    services:
      db:
        image: mariadb
        volumes:
        - database:/var/lib/mysql:rw
        restart: always
        ports:
          - 3306:3306
        environment:
          MYSQL_ROOT_PASSWORD: changeyourstrongpasswordhere
          MYSQL_DATABASE: freedb
          MYSQL_USER: freedb
          MYSQL_PASSWORD: freedb
          command: --default-authentication-plugin=mysql_native_password character-set-server=utf8 --collation-server=utf8_general_ci
      web:
        image: freedb
        ports:
        - "8000:8000"
        depends_on:
        - db
        volumes:
        - ./prod_settings.py:/app/prod_settings.py:Z
        environment:
          DJANGO_SETTINGS_MODULE: prod_settings
          DATABASE_URL: mysql://
          DB_HOST: db
          DB_PORT: 3306
          DB_NAME: imagebank
          DB_USER: imagebank
          DB_PASSWORD: imagebankpass
        command: uwsgi imagebank/uwsgi.ini
        networks:
        - host

    volumes:
      database:

