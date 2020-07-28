import os
from freedb_site.settings import *

SECRET_KEY = 'YOURSECRETCODEHERE'

DEBUG = False

ALLOWED_HOSTS = [
    '*'
]

import pymysql
pymysql.install_as_MySQLdb()

MONGODB_URL = os.environ.get('MONGODB_URL')

STATIC_ROOT = 'staticfiles'

import dj_database_url 
prod_db  =  dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)
