import os

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(
    os.environ.get("SOLESEARCH_DB_CONNECTION_STRING")
)
db = client[os.environ.get("SOLESEARCH_DB_NAME")]
sneakers = db[os.environ.get("SOLESEARCH_DB_PRIMARY_COLLECTION")]
DEFAULT_LIMIT = int(os.environ.get("SOLESEARCH_DEFAULT_LIMIT", 10))
DEFAULT_OFFSET = int(os.environ.get("SOLESEARCH_DEFAULT_OFFSET", 0))
