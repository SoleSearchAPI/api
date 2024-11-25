from celery.app import Celery

from api.config import CELERY_BACKEND, CELERY_BROKER


class CeleryConfig:
    timezone = "America/New_York"


scheduler = Celery(
    "ingest",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    config_source=CeleryConfig,
)
