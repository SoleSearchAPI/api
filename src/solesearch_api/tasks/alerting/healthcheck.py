import logging
import requests
from requests_aws4auth import AWS4Auth

from solesearch_api.config import (
    AWS_ACCESS_KEY_ID,
    AWS_HEALTHCHECK_URL,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
)
from solesearch_api.tasks import app

logger = logging.getLogger(__name__)

auth = AWS4Auth(
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    "execute-api",
)


@app.task(name="solesearch_api.tasks.alerting.healthcheck")
def healthcheck():
    response = requests.post(
        AWS_HEALTHCHECK_URL,
        json={"ping": True},
        auth=auth,
    )
    response.raise_for_status()
