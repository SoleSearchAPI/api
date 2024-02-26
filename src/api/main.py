import os

from dotenv import load_dotenv

if not os.environ.get("AWS_EXECUTION_ENV"):
    load_dotenv(os.path.join(os.getcwd(), ".env"))

from beanie import init_beanie
from fastapi import FastAPI
from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

from api.data.instance import DATABASE_NAME, client
from api.routes import auth, sneakers
from core.models.shoes import Sneaker

app = FastAPI(
    redoc_url=None,
    responses={404: {"description": "Not found"}},
)

app.add_middleware(SessionMiddleware, secret_key="some secret key here")


@app.on_event("startup")
async def startup_event():
    await init_beanie(
        database=client.get_database(DATABASE_NAME),
        document_models=[Sneaker],
    )

    app.include_router(sneakers.router)
    app.include_router(auth.router)


handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
