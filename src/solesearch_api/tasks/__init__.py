from celery.app import Celery

from solesearch_api.config import CELERY_BACKEND, CELERY_BROKER


class CeleryConfig:
    timezone = "America/New_York"


scheduler = Celery(
    "solesearch",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    config_source=CeleryConfig,
)
