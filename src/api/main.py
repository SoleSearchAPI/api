__version__ = "2.0.0"

import os

from dotenv import load_dotenv

# Load environment variables from .env file if not running in AWS Lambda
if not os.environ.get("AWS_EXECUTION_ENV"):
    print("Loading .env file")
    load_dotenv(os.path.join(os.getcwd(), ".env"))

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from mangum import Mangum
from starlette.middleware.sessions import SessionMiddleware

from api.data.instance import DATABASE_NAME, client
from api.routes import auth, sneakers
from core.models.shoes import Sneaker

desc = """
### The Bloomberg Terminal of Sneakers
- Find product information, from every brand, fast. 👟
- Never miss another release date. 📅
- Never buy bricks. Stay ahead of the game with our comprehensive price history and trends. 💵
"""

app = FastAPI(
    redoc_url=None,
    docs_url=None,
    title="SoleSearch",
    version=__version__,
    contact={"name": "SoleSearch Email Support", "email": "support@solesearch.io"},
    description=desc,
    responses={404: {"description": "Not found"}},  # Custom 404 page
)

# Serve static files from the /static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Enable session handling for StocxkX OAuth flow
SESSION_SECRET = os.environ.get("SOLESEARCH_SESSION_SECRET", "this should be a secret")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)


@app.on_event("startup")
async def startup_event():
    # Initialize Beanie ODM
    await init_beanie(
        database=client.get_database(DATABASE_NAME),
        document_models=[Sneaker],
    )
    # Include all routers
    app.include_router(sneakers.router)
    app.include_router(auth.router)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_favicon_url="/static/favicon.png",
    )


# This is the entry point for AWS Lambda
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    # Run the app locally using Uvicorn, with SSL enabled
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
    )
