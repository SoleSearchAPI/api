import os

DB_URL = os.environ.get("DB_CONNECTION_STRING")

if not DB_URL:
    raise OSError("DB_CONNECTION_STRING environment variable not set.")

CELERY_BROKER = os.environ.get("CELERY_BROKER_URL")

if not CELERY_BROKER:
    raise OSError("CELERY_BROKER_URL environment variable not set.")

CELERY_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

if not CELERY_BACKEND:
    raise OSError("CELERY_RESULT_BACKEND environment variable not set.")

ENVIRONMENT = os.environ.get("ENVIRONMENT")

if not ENVIRONMENT:
    raise OSError("ENVIRONMENT environment variable not set.")

DATA_DIR = "/var/data/solesearch"
HTML_DIR = os.path.join(DATA_DIR, "html")
JSON_DIR = os.path.join(DATA_DIR, "json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
