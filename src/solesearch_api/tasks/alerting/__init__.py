# Import all tasks to ensure they are registered with Celery
from solesearch_api.tasks.alerting.healthcheck import healthcheck
