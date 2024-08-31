import logging
import os
from contextlib import contextmanager

import requests
from api.db import get_session
from api.models.auth import Token
from api.models.sneaker.enums import Platform
from requests.adapters import HTTPAdapter
from requests_ratelimiter import LimiterAdapter
from sqlmodel import select

logger = logging.getLogger(__name__)

session = requests.Session()

session.mount("https://stockx.com/", LimiterAdapter(per_second=1, per_minute=10))
session.mount("https://www.nike.com/", LimiterAdapter(per_second=0.25, per_minute=11))
session.mount("https://us.puma.com/", LimiterAdapter(per_second=1))
session.mount(
    "https://snkr-rest-api-nfrpf.ondigitalocean.app/",
    LimiterAdapter(per_second=1),
)
session.mount(
    "https://the-sneaker-database.p.rapidapi.com/",
    LimiterAdapter(per_second=0.25, per_minute=10),
)
session.mount("https://api.whatismybrowser.com/", LimiterAdapter(per_hour=1000))
session.mount("https://api.stockx.vlour.me", LimiterAdapter(per_hour=1000))


@contextmanager
def get_db():
    session = next(get_session())
    try:
        yield session
    finally:
        session.close()


class TokenRefreshAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.API_KEY = os.environ.get("SOLESEARCH_STOCKX_API_KEY")
        if not self.API_KEY:
            raise OSError(
                "Please set the SOLESEARCH_STOCKX_API_KEY environment variable."
            )
        self.CLIENT_ID = os.environ.get("SOLESEARCH_STOCKX_CLIENT_ID")
        if not self.CLIENT_ID:
            raise OSError(
                "Please set the SOLESEARCH_STOCKX_CLIENT_ID environment variable."
            )
        self.CLIENT_SECRET = os.environ.get("SOLESEARCH_STOCKX_CLIENT_SECRET")
        if not self.CLIENT_SECRET:
            raise OSError(
                "Please set the SOLESEARCH_STOCKX_CLIENT_SECRET environment variable."
            )
        self.max_retries = 3
        self.token = self.get_token("access_token")
        self.refresh_token = self.get_token("refresh_token")
        super().__init__(*args, **kwargs)

    def get_token(self, token_type: str) -> str:
        with get_db() as session:
            token = session.exec(
                select(Token).where(
                    Token.type == token_type, Token.platform == Platform.STOCKX
                )
            ).first()
            return token.value if token else ""

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
        tokens = requests.post(
            url="https://accounts.stockx.com/oauth/token",
            timeout=20,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.CLIENT_ID,
                "client_secret": self.CLIENT_SECRET,
                "audience": "gateway.stockx.com",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ).json()
        self.token = tokens["access_token"]
        update_stockx_tokens(tokens)
        logging.info("Token renewed!")


def update_stockx_tokens(tokens: dict):
    with get_db() as session:
        token_types = ["id_token", "access_token", "refresh_token"]
        db_tokens = session.exec(
            select(Token).where(
                Token.type.in_(token_types), Token.platform == Platform.STOCKX
            )
        ).all()

        for token_type in token_types:
            if token_type in tokens:
                token = next((t for t in db_tokens if t.type == token_type), None)
                if token:
                    token.value = tokens[token_type]
                else:
                    new_token = Token(
                        type=token_type,
                        value=tokens[token_type],
                        platform=Platform.STOCKX,
                    )
                    session.add(new_token)

        session.commit()
        logger.info(f"Updated tokens: {', '.join(token_types)}")


stockx_session = requests.Session()
adapter = TokenRefreshAdapter()
stockx_session.mount("https://api.stockx.com", adapter)
