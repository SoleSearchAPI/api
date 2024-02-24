import os

from dotenv import load_dotenv
from fastapi import FastAPI
from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

if not os.environ.get("AWS_EXECUTION_ENV"):
    load_dotenv(os.path.join(os.getcwd(), ".env"))

from api.routes import auth, sneakers

app = FastAPI(
    redoc_url=None,
    responses={404: {"description": "Not found"}},
)

app.add_middleware(SessionMiddleware, secret_key="some secret key here")

app.include_router(sneakers.router)
app.include_router(auth.router)
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
