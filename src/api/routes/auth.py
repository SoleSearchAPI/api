import logging
import os
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from api.data.queries import update_tokens

STOCKX_CLIENT_ID = os.environ.get("SOLESEARCH_STOCKX_CLIENT_ID", None)
STOCKX_CLIENT_SECRET = os.environ.get("SOLESEARCH_STOCKX_CLIENT_SECRET", None)
STOCKX_API_KEY = os.environ.get("SOLESEARCH_STOCKX_API_KEY", None)

session = requests.session()

router = APIRouter(
    prefix="/auth",
    include_in_schema=False,
)


@router.get("/stockx")
async def login_via_stockx(state: str, request: Request):
    if state != "YTPc2DqAwnmhHGzSQVtzwEPq2eEgprUi":
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
    if state != "YTPc2DqAwnmhHGzSQVtzwEPq2eEgprUi":
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
            "redirect_uri": f"https://{urlparse(request.url_for("get_sneakers")).netloc}",
        }
        tokens = (
            session.post(
                "https://accounts.stockx.com/oauth/token",
                data=login_data,
                headers=headers,
            )
        ).json()
        await update_tokens(tokens)
        return tokens
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
