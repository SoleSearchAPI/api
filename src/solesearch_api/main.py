__version__ = "2.2.0"

import os

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination
from starlette.middleware.sessions import SessionMiddleware

from solesearch_api.db import initialize_db
from solesearch_api.routes import auth, sneakers, triggers

desc = """
### The Bloomberg Terminal of Sneakers
- Find product information, from every brand, fast.
- Never miss another release date.
- Never buy bricks. Stay ahead of the game with our comprehensive price insights.

[Twitter](https://twitter.com/SoleSearchAPI) | [Github](https://github.com/SoleSearchAPI)
"""

app = FastAPI(
    redoc_url=None,
    docs_url=None,
    title="SoleSearch",
    version=__version__,
    contact={
        "name": "SoleSearch",
        "url": "https://solesearch.io",
        "email": "support@solesearch.io",
    },
    description=desc,
    responses={404: {"description": "Not found"}},  # Custom 404 page
)

# Configure Logfire
logfire.configure()
logfire.instrument_fastapi(app)

# Enable session handling for StocxkX OAuth flow
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
)
# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # Create the database tables
    initialize_db()
    # Include all routers
    app.include_router(sneakers.router)
    app.include_router(auth.router)
    app.include_router(triggers.router)
    # Load the pagination module
    add_pagination(app)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_favicon_url="https://i.imgur.com/2Y59zOy.png",
    )


# Redirect the root URL to the documentation
@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")
