import logging
import os

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
