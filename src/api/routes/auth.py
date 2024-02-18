import logging
import os
from http.client import HTTPException

import requests
from fastapi import APIRouter

STOCKX_CLIENT_ID = os.environ.get("SOLESEARCH_STOCKX_CLIENT_ID", None)
STOCKX_CLIENT_SECRET = os.environ.get("SOLESEARCH_STOCKX_CLIENT_SECRET", None)
STOCKX_API_KEY = os.environ.get("SOLESEARCH_STOCKX_API_KEY", None)

router = APIRouter(
    prefix="/auth",
)


@router.get("/stockx/code")
async def get_stockx_auth(state: str = None, code: str = None):
    if state != "pRbqDm7XTFx27WZyQW78urwKWmZJW3go":
        raise HTTPException(status_code=401, detail="Bad secret. Nice try, buster.")
    if code is None:
        raise HTTPException(status_code=400, detail="No code provided")
    response = requests.post(
        url="https://accounts.stockx.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": STOCKX_CLIENT_ID,
            "client_secret": STOCKX_CLIENT_SECRET,
            "redirect_uri": "https://localhost:8000/auth/stockx/token",
        },
        headers={"x-api-key": STOCKX_API_KEY},
    )
    print(response)
    response_json = response.json()
    logging.info(response_json)
    return response_json


@router.get("/stockx/token")
async def get_stockx_token(authorization_code: str = None):
    logging.info(authorization_code)
    return {"Successs": "Check the logs for authorization code"}
