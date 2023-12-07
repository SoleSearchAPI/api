import motor.motor_asyncio
from fastapi import FastAPI

from config import MONGODB_URL

app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("SoleSearch")
student_collection = db.get_collection("sneakers")


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "We're working on it... great things to come soon!",
    }
