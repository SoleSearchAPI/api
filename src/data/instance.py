import motor.motor_asyncio
from dotenv import dotenv_values

config = dotenv_values(dotenv_path="db.env")

client = motor.motor_asyncio.AsyncIOMotorClient(config["DB_URL"])
db = client[config["DB_NAME"]]
sneakers = db[config["SNEAKERS_COLLECTION"]]
ASCENDING = int(config["ASCENDING"])
DESCENDING = int(config["DESCENDING"])
DEFAULT_LIMIT = int(config["DEFAULT_LIMIT"])
DEFAULT_OFFSET = int(config["DEFAULT_OFFSET"])
