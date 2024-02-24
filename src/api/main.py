import os

from dotenv import load_dotenv
from fastapi import FastAPI
from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

from api.routes import auth, sneakers

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = FastAPI(
    redoc_url=None,
    responses={404: {"description": "Not found"}},
)

app.add_middleware(SessionMiddleware, secret_key="some secret key here")

app.include_router(sneakers.router)
app.include_router(auth.router)
handler = Mangum(app)
