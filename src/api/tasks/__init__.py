from celery.app import Celery

from api.config import REDIS_URL


class CeleryConfig:
    timezone = "America/New_York"


scheduler = Celery(
    "ingest", broker=REDIS_URL, backend=REDIS_URL, config_source=CeleryConfig
)
