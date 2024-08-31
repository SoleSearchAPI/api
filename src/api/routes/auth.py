import logging
import os
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

import requests
from api.models.auth import Token
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

STOCKX_CLIENT_ID = os.environ.get("SOLESEARCH_STOCKX_CLIENT_ID", None)
STOCKX_CLIENT_SECRET = os.environ.get("SOLESEARCH_STOCKX_CLIENT_SECRET", None)
STOCKX_API_KEY = os.environ.get("SOLESEARCH_STOCKX_API_KEY", None)
STOCKX_STATE = os.environ.get(
    "SOLESEARCH_STOCKX_CALLBACK_STATE", "this should be a secret string"
)

session = requests.session()

router = APIRouter(
    prefix="/auth",
    include_in_schema=False,
)


@router.get("/stockx")
async def login_via_stockx(state: str, request: Request):
    if state != STOCKX_STATE:
        raise HTTPException(status_code=400, detail="Bad state. Nice try, buster.")
    auth_url = "https://accounts.stockx.com/authorize"
    print(STOCKX_CLIENT_ID, STOCKX_CLIENT_SECRET, STOCKX_API_KEY)
    params = {
        "response_type": "code",
        "client_id": STOCKX_CLIENT_ID,
        "redirect_uri": request.url_for("stockx_oauth_callback"),
        "scope": "offline_access openid",
        "audience": "gateway.stockx.com",
        "state": state,
    }
    auth_url = requests.Request("GET", auth_url, params=params).prepare().url
    return RedirectResponse(auth_url)


@router.get("/stockx/callback")
async def stockx_oauth_callback(state: str, code: str, request: Request):
    if code is None:
        raise HTTPException(status_code=400, detail="No code returned from StockX.")
    if state != STOCKX_STATE:
        raise HTTPException(status_code=400, detail="Bad state. Nice try, buster.")
    try:
        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }
        login_data = {
            "grant_type": "authorization_code",
            "client_id": STOCKX_CLIENT_ID,
            "client_secret": STOCKX_CLIENT_SECRET,
            "code": code,
            "redirect_uri": f"https://{urlparse(str(request.url_for('get_sneakers'))).netloc}",
        }
        tokens = (
            session.post(
                "https://accounts.stockx.com/oauth/token",
                data=login_data,
                headers=headers,
            )
        ).json()
        for token_type in ["id_token", "access_token", "refresh_token"]:
            if token_type in tokens:
                token = await Token.find_one(Token.id == token_type)
                setattr(token, "value", tokens[token_type])
                if token_type == "access_token":
                    token.expires = datetime.now(UTC) + timedelta(
                        seconds=int(tokens["expires_in"]) - 30
                    )
                await token.save()
                logging.info(f"Updated {token_type}")
        return tokens
    except Exception as e:
        logging.exception(e)
        raise HTTPException(status_code=500, detail=str(e))
