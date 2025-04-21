__version__ = "3.0.0"

import os

import logfire
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from fastapi_pagination import add_pagination
from starlette.middleware.sessions import SessionMiddleware

from solesearch_api.routes import auth, scrape, sneakers

desc = """
### The Bloomberg Terminal of Sneakers

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
    responses={404: {"description": "404: Not found"}},  # Custom 404 page
)

# Configure Logfire
logfire.configure(service_name="api")
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
    # Include all routers
    app.include_router(sneakers.router)
    app.include_router(auth.router)
    app.include_router(scrape.router)
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


@app.get("/investigate", include_in_schema=False)
async def investigate_url(url: str, extractor_type: str = "next_json_extractor"):
    """
    Endpoint to trigger an investigation download for any URL.
    This will download the HTML and JSON data and store it in the Investigation folder.

    Args:
        url: The URL to investigate
        extractor_type: Type of extractor to use (default: "json")
    """
    try:
        # Import the appropriate extractor
        # This should be equivalent to:
        # from solesearch_api.utils.extractors import next_json_extractor as extractor
        import solesearch_api.utils.extractors as extractor_module

        extractor = getattr(extractor_module, extractor_type)

        # Create an instance of the investigation task
        from solesearch_api.tasks.scraping.investigation import GenericInvestigationTask

        task_instance = GenericInvestigationTask(
            url=url,
            extractor=extractor,
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "Referer": "https://www.adidas.com/us/shoes",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            },
        )

        # Force download of HTML and JSON
        json_data = task_instance.get_json()

        return {
            "status": "success",
            "message": f"Investigation data downloaded for URL: {url}",
            "json_size": len(str(json_data)),
        }
    except Exception as e:
        logfire.error(
            "Failed to download investigation data",
            url=url,
            extractor_type=extractor_type,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"Failed to download investigation data: {str(e)}",
        }
