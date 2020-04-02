# encoding: utf-8
import os

# mongo
DB_URI = os.environ['NIPT_MONGO_URI']
DB_NAME = os.environ['NIPT_MONGO_DBNAME']

DEBUG = os.environ['NIPT_FLASK_DEBUG']
SECRET_KEY = os.environ['NIPT_SECRET_KEY']

# analysis
ANALYSIS_PATH = os.environ['NIPT_ANALYSIS_PATH']

GOOGLE_CLIENT_ID = '527111695356-mnoqdc2e68nf19tq7o8vdibnb8lj3ge4.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'A7rEjzAjO57VYmB1EIaoO71N'