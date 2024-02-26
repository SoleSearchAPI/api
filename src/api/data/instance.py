import logging
import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

CONNECTION_STRING = os.environ.get("SOLESEARCH_DB_CONNECTION_STRING")
if not CONNECTION_STRING:
    raise EnvironmentError(
        "Please set the SOLESEARCH_DB_CONNECTION_STRING environment variable."
    )
client = AsyncIOMotorClient(CONNECTION_STRING)
DATABASE_NAME = os.environ.get("SOLESEARCH_DB_NAME")
if not DATABASE_NAME:
    DATABASE_NAME = "Sneakers"
    logger.warning(
        f"SOLESEARCH_DB_NAME environment variable not set, defaulting to {DATABASE_NAME}."
    )
db = client[os.environ.get("SOLESEARCH_DB_NAME")]
sneakers = db[os.environ.get("SOLESEARCH_DB_PRIMARY_COLLECTION")]
DEFAULT_LIMIT = int(os.environ.get("SOLESEARCH_DEFAULT_LIMIT", 10))
DEFAULT_OFFSET = int(os.environ.get("SOLESEARCH_DEFAULT_OFFSET", 0))
