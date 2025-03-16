import os

REQUIRED_PROD_ENV_VARS = [
    "LOGFIRE_TOKEN",
    "DB_CONNECTION_STRING",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "AWS_HEALTHCHECK_URL",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
]

if not os.environ.get("ENVIRONMENT"):
    raise OSError("ENVIRONMENT environment variable not set.")

if os.environ.get("ENVIRONMENT") == "prod":
    for var in REQUIRED_PROD_ENV_VARS:
        if not os.environ.get(var):
            raise OSError(f"{var} environment variable not set.")

DB_URL = os.environ.get("DB_CONNECTION_STRING")
CELERY_BROKER = os.environ.get("CELERY_BROKER_URL")
CELERY_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
ENVIRONMENT = os.environ.get("ENVIRONMENT")

AWS_HEALTHCHECK_URL = os.environ.get("AWS_HEALTHCHECK_URL")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

DATA_DIR = "/var/data/solesearch"
HTML_DIR = os.path.join(DATA_DIR, "html")
JSON_DIR = os.path.join(DATA_DIR, "json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
