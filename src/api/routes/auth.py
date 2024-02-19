import logging
import os

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException
from starlette.requests import Request

STOCKX_CLIENT_ID = os.environ.get("SOLESEARCH_STOCKX_CLIENT_ID", None)
STOCKX_CLIENT_SECRET = os.environ.get("SOLESEARCH_STOCKX_CLIENT_SECRET", None)
STOCKX_API_KEY = os.environ.get("SOLESEARCH_STOCKX_API_KEY", None)

oauth = OAuth()

oauth.register(
    name="stockx",
    client_id=STOCKX_CLIENT_ID,
    client_secret=STOCKX_CLIENT_SECRET,
    server_metadata_url="https://accounts.stockx.com/.well-known/oauth-authorization-server",
    client_kwargs={
        "scope": "openid email profile offline_access",
        "audience": "gateway.stockx.com",
    },
)

router = APIRouter()


@router.get("/")
async def homepage(request: Request):
    return {
        "message": f"Sample homepage. To login, navigate your browser to {request.url_for('login_via_stockx')}"
    }


@router.get("/login/stockx")
async def login_via_stockx(request: Request):
    stockx = oauth.create_client("stockx")
    redirect_uri = request.url_for("stockx_oauth_callback")
    return await stockx.authorize_redirect(request, redirect_uri)
    # params = {
    #     "response_type": "code",
    #     "client_id": STOCKX_CLIENT_ID,
    #     "scope": "openid email profile offline_access",
    #     "audience": "gateway.stockx.com",
    #     # "state": "pRbqDm7XTFx27WZyQW78urwKWmZJW3go",
    # }
    # stockx_oauth_url = f"{stockx_oauth_url}?{urlencode(params)}"
    # return RedirectResponse(stockx_oauth_url)


@router.get("/callback")
async def stockx_oauth_callback(request: Request, state: str = None, code: str = None):
    if code is None:
        raise HTTPException(status_code=400, detail="No code returned from StockX.")
    stockx = oauth.create_client("stockx")
    try:
        token = await stockx.authorize_access_token(request)
        print(token)
        return dict(token)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    # response = requests.post(
    #     url="https://accounts.stockx.com/oauth/token",
    #     data={
    #         "grant_type": "authorization_code",
    #         "code": code,
    #         "client_id": STOCKX_CLIENT_ID,
    #         "client_secret": STOCKX_CLIENT_SECRET,
    #         "redirect_uri": "https://localhost:8000/token",
    #     },
    # )
    # print(response)
    # response_json = response.json()
    # logging.info(response_json)
    # return response_json


@router.get("/token")
async def get_stockx_token(authorization_code: str = None):
    logging.info(authorization_code)
    return {"Successs": f"Authorized with authorization code {authorization_code}"}
