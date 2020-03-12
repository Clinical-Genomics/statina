# encoding: utf-8
import os

# mongo
DB_URI = os.environ['NIPT_MONGO_URI']
DB_NAME = os.environ['NIPT_MONGO_DBNAME']

DEBUG = os.environ['NIPT_FLASK_DEBUG']
SECRET_KEY = os.environ['NIPT_SECRET_KEY']

# analysis
ANALYSIS_PATH = os.environ['NIPT_ANALYSIS_PATH']
