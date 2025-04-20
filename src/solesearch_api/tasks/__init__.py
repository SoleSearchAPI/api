import logfire
from celery import Celery
from celery.signals import worker_init

from solesearch_api.config import CELERY_BACKEND, CELERY_BROKER


class CeleryConfig:
    timezone = "America/New_York"


@worker_init.connect()
def configure_logfire(*args, **kwargs):
    logfire.instrument_celery()


app = Celery(
    "solesearch_api",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    config_source=CeleryConfig,
)

app.conf.beat_schedule = {
    "adidas-new-releases-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.AdidasNewReleasesScrapingTask",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "adidas-baby-and-toddler-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.AdidasBabyAndToddlerScrapingTask",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "adidas-children-and-little-kids-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.AdidasChildrenAndLittleKidsScrapingTask",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "adidas-youth-and-big-kids-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.AdidasYouthAndBigKidsScrapingTask",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "nike-new-releases-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.NikeNewReleasesScrapingTask",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "nike-in-stock-every-4-hours": {
        "task": "solesearch_api.tasks.scraping.NikeInStockScrapingTask",
        "schedule": 4 * 60 * 60,  # every 4 hours
    },
    "goat-recently-added-by-brand-every-24-hours": {
        "task": "solesearch_api.tasks.scraping.GoatRecentlyAddedByBrandScrapingTask",
        "schedule": 24 * 60 * 60,  # every 24 hours
    },
    "healthcheck-every-minute": {
        "task": "solesearch_api.tasks.alerting.healthcheck",
        "schedule": 60 * 10,  # every 10 minutes
    },
}

import solesearch_api.tasks.alerting
import solesearch_api.tasks.scraping
