import logging
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from api.data.queries import update_tokens
import requests

STOCKX_CLIENT_ID = os.environ.get("SOLESEARCH_STOCKX_CLIENT_ID", None)
STOCKX_CLIENT_SECRET = os.environ.get("SOLESEARCH_STOCKX_CLIENT_SECRET", None)
STOCKX_API_KEY = os.environ.get("SOLESEARCH_STOCKX_API_KEY", None)

router = APIRouter()
session = requests.session()

@router.get("/")
async def homepage():
    return {
        "error_message": f"Read the docs: https://api.solesearch.io/docs",
    }


@router.get("/login/stockx")
async def login_via_stockx(state: str = None):
    if state != "YTPc2DqAwnmhHGzSQVtzwEPq2eEgprUi":
        raise HTTPException(status_code=400, detail="Bad state. Nice try, buster.")
    auth_url = "https://accounts.stockx.com/authorize"
    params = {
        "response_type": "code",
        "client_id": STOCKX_CLIENT_ID,
        "redirect_uri": "https://localhost:8000/callback",
        "scope": "offline_access openid",
        "audience": "gateway.stockx.com",
        "state": state,
    }
    auth_url = requests.Request("GET", auth_url, params=params).prepare().url
    return RedirectResponse(auth_url)


@router.get("/callback")
async def stockx_oauth_callback(state: str = None, code: str = None):
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
            "redirect_uri": "https://localhost:8000/token",
        }
        tokens = (session.post("https://accounts.stockx.com/oauth/token", data=login_data, headers=headers)).json()
        await update_tokens(tokens)
        return tokens
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    