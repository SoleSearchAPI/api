import requests
from requests_aws4auth import AWS4Auth

from solesearch_api.config import (
    AWS_ACCESS_KEY_ID,
    AWS_HEALTHCHECK_URL,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    ENVIRONMENT,
)
from solesearch_api.tasks import app

if ENVIRONMENT == "production":
    auth = AWS4Auth(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        AWS_REGION,
        "execute-api",
    )


@app.task(name="solesearch_api.tasks.alerting.healthcheck")
def healthcheck():
    if ENVIRONMENT != "production":
        return
    response = requests.post(
        AWS_HEALTHCHECK_URL,
        json={"ping": True},
        auth=auth,
        timeout=20,
    )
    response.raise_for_status()
