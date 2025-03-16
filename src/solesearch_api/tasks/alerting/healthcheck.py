import logging
import requests
from requests_aws4auth import AWS4Auth

from solesearch_api.config import (
    AWS_ACCESS_KEY_ID,
    AWS_HEALTHCHECK_URL,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    ENVIRONMENT,
)
from solesearch_api.tasks import app

logger = logging.getLogger(__name__)

if ENVIRONMENT == "production":
    auth = AWS4Auth(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        AWS_REGION,
        "execute-api",
    )


@app.task(name="solesearch_api.tasks.alerting.healthcheck")
def healthcheck():
    if not ENVIRONMENT == "production":
        return
    response = requests.post(
        AWS_HEALTHCHECK_URL,
        json={"ping": True},
        auth=auth,
    )
    response.raise_for_status()
