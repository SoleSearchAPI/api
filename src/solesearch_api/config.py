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

AWS_HEALTHCHECK_URL = os.environ.get("AWS_HEALTHCHECK_URL")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

if not AWS_HEALTHCHECK_URL:
    raise OSError("AWS_HEALTHCHECK_URL environment variable not set.")

if not AWS_ACCESS_KEY_ID:
    raise OSError("AWS_ACCESS_KEY_ID environment variable not set.")

if not AWS_SECRET_ACCESS_KEY:
    raise OSError("AWS_SECRET_ACCESS_KEY environment variable not set.")

DATA_DIR = "/var/data/solesearch"
HTML_DIR = os.path.join(DATA_DIR, "html")
JSON_DIR = os.path.join(DATA_DIR, "json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
