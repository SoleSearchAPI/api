from dotenv import load_dotenv
from fastapi import FastAPI

# from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

config = load_dotenv(dotenv_path=".env")

from src.api.routes import auth, sneakers

app = FastAPI(
    responses={404: {"resource": "Not found"}},
)

app.add_middleware(SessionMiddleware, secret_key="some secret key here")


@app.get("/ping")
async def ping():
    return {"alive": True}


app.include_router(sneakers.router)
app.include_router(auth.router)
# handler = Mangum(app)
