from dotenv import load_dotenv
from fastapi import FastAPI
from src.api.routes import auth, sneakers
# from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

config = load_dotenv(dotenv_path=".env")

app = FastAPI(
    redoc_url=None,
    responses={404: {"description": "Not found"}},
)

app.add_middleware(SessionMiddleware, secret_key="some secret key here")

app.include_router(sneakers.router)
app.include_router(auth.router)
# handler = Mangum(app)
