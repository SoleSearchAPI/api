import motor.motor_asyncio
from dotenv import dotenv_values

config = dotenv_values(dotenv_path=".env")

client = motor.motor_asyncio.AsyncIOMotorClient(config["SOLESEARCH_DB_CONNECTION_STRING"])
db = client[config["SOLESEARCH_DB_NAME"]]
sneakers = db[config["SOLESEARCH_DB_PRIMARY_COLLECTION"]]
DEFAULT_LIMIT = int(config["SOLESEARCH_DEFAULT_LIMIT"])
DEFAULT_OFFSET = int(config["SOLESEARCH_DEFAULT_OFFSET"])
