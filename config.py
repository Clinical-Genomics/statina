# encoding: utf-8
import os

# if you running with docker set DB_HOST = 'mongo' otherwise 'localhost'
DB_HOST = 'mongo'
DB_URI = f"mongodb://{DB_HOST}:27017"
DB_NAME = 'nipt-stage'
DEBUG = 0
DEBUG_TB_INTERCEPT_REDIRECTS=False
SECRET_KEY='hej'
LOGIN_DISABLED=True
TESTING=True
