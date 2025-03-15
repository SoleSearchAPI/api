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

app.conf.beat_schedule = {
    "adidas-new-releases-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.retail.adidas.new_releases",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "adidas-pdp-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.retail.adidas.pdp",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "nike-new-releases-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.retail.nike.new_releases",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "nike-in-stock-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.retail.nike.in_stock",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "healthcheck-every-minute": {
        "task": "solesearch_api.tasks.alerting.healthcheck",
        "schedule": 60 * 10,  # every 10 minutes
    },
}

import solesearch_api.tasks.scraping
import solesearch_api.tasks.alerting.healthcheck
