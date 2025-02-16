import logfire
from celery import Celery
from celery.signals import beat_init, worker_init

from solesearch_api.config import CELERY_BACKEND, CELERY_BROKER


class CeleryConfig:
    timezone = "America/New_York"


@worker_init.connect()
def configure_logfire(*args, **kwargs):
    logfire.configure(service_name="worker")
    logfire.instrument_celery()


@beat_init.connect()
def init_beat(*args, **kwargs):
    logfire.configure(service_name="beat")
    logfire.instrument_celery()


app = Celery(
    "solesearch_api",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    config_source=CeleryConfig,
)

app.conf.update(
    imports=(
        "solesearch_api.tasks.ingest.retail.nike",
        "solesearch_api.tasks.ingest.retail.adidas",
    )
)
