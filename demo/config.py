# encoding: utf-8
import os

# mongo
DB_HOST = os.getenv("MONGODB_HOST") or "localhost"
DB_URI = f"mongodb://{DB_HOST}:27017"
DB_NAME = "statina-stage"
DEBUG = 0
DEBUG_TB_INTERCEPT_REDIRECTS = False
SECRET_KEY = "hej"
LOGIN_DISABLED = True
TESTING = True
