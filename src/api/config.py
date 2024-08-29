import os


DB_URL = os.environ.get("SOLESEARCH_DB_CONNECTION_STRING")

if not DB_URL:
    raise Exception("SOLESEARCH_DB_CONNECTION_STRING environment variable not set.")

REDIS_URL = os.environ.get("SOLESEARCH_REDIS_URL")

if not REDIS_URL:
    raise Exception("SOLESEARCH_REDIS_URL environment variable not set.")