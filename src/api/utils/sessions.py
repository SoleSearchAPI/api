import logging
import os

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests_ratelimiter import LimiterAdapter

from ingest.models.misc import StockxToken

logger = logging.getLogger(__name__)

session = Session()

session.mount("https://stockx.com/", LimiterAdapter(per_second=1, per_minute=10))
session.mount("https://www.nike.com/", LimiterAdapter(per_second=0.25, per_minute=11))
session.mount("https://us.puma.com/", LimiterAdapter(per_second=1))
session.mount(
    "https://snkr-rest-api-nfrpf.ondigitalocean.app/", LimiterAdapter(per_second=1)
)
session.mount(
    "https://the-sneaker-database.p.rapidapi.com/",
    LimiterAdapter(per_second=0.25, per_minute=10),
)
session.mount("https://api.whatismybrowser.com/", LimiterAdapter(per_hour=1000))
session.mount("https://api.stockx.vlour.me", LimiterAdapter(per_hour=1000))


class TokenRefreshAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.API_KEY = os.environ.get("SOLESEARCH_STOCKX_API_KEY")
        if not self.API_KEY:
            raise EnvironmentError(
                "Please set the SOLESEARCH_STOCKX_API_KEY environment variable."
            )
        self.CLIENT_ID = os.environ.get("SOLESEARCH_STOCKX_CLIENT_ID")
        if not self.CLIENT_ID:
            raise EnvironmentError(
                "Please set the SOLESEARCH_STOCKX_CLIENT_ID environment variable."
            )
        self.CLIENT_SECRET = os.environ.get("SOLESEARCH_STOCKX_CLIENT_SECRET")
        if not self.CLIENT_SECRET:
            raise EnvironmentError(
                "Please set the SOLESEARCH_STOCKX_CLIENT_SECRET environment variable."
            )
        self.max_retries = 3
        self.token = StockxToken.find_one(StockxToken.type == "access_token").token
        self.refresh_token = StockxToken.find_one(
            StockxToken.type == "refresh_token"
        ).token
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        request.headers["Content-Type"] = "application/json"
        request.headers["Authorization"] = f"Bearer {self.token}"
        request.headers["x-api-key"] = self.API_KEY
        response = super().send(request, **kwargs)
        retry_count = 0
        while response.status_code == 401 and retry_count < self.max_retries:
            self.renew_token()
            request.headers["Authorization"] = f"Bearer {self.token}"
            response = super().send(request, **kwargs)
            retry_count += 1
        if response.status_code == 429:
            raise Exception("Rate limit hit, aborting...")
        return response

    def renew_token(self):
        logging.info("Renewing token...")
        tokens = (
            requests.post(
                url="https://accounts.stockx.com/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "audience": "gateway.stockx.com",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        ).json()
        self.token = tokens["access_token"]
        update_stockx_tokens(tokens)
        logging.info("Token renewed!")


async def update_stockx_tokens(tokens: dict):
    for token_type in ["id_token", "access_token", "refresh_token"]:
        if token_type in tokens:
            db_token = await StockxToken.find_one(StockxToken.type == token_type)
            db_token.token = tokens[token_type]
            logger.info(f"Updated {token_type}")


stockx_session = Session()
adapter = TokenRefreshAdapter()
stockx_session.mount("https://api.stockx.com", adapter)
