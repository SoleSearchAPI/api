import asyncio
from typing import Any, Dict

from api.models.enums import Audience, Platform

# Import your SQLModel classes
from api.models.sneaker import Image, Link, Sneaker
from api.utils.time import utc_now
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

# MongoDB connection
MONGO_URI = "mongodb://root:example@localhost:27017/"
MONGO_DB_NAME = "Sneakers"

# PostgreSQL connection
POSTGRES_URI = "postgresql://solesearch:solesearch@localhost/Sneakers"

# Create synchronous engine
engine = create_engine(POSTGRES_URI, echo=True)


def transform_sneaker(data: Dict[str, Any]) -> Sneaker:
    """
    Transform the data from MongoDB format to SQLModel format.
    Implement your data transformation logic here.
    """
    sneaker = Sneaker(
        created_at=data.get("dateAdded") if data.get("dateAdded") else utc_now(),
        updated_at=data.get("lastScraped") if data.get("lastScraped") else utc_now(),
        brand=data.get("brand") if data.get("brand") else None,
        sku=data.get("sku") if data.get("sku") else None,
        name=data.get("name") if data.get("name") else None,
        colorway=data.get("colorway") if data.get("colorway") else None,
        audience=Audience(data["audience"]) if data.get("audience") else None,
        release_date=data.get("releaseDate") if data.get("releaseDate") else None,
        description=data.get("description") if data.get("description") else None,
        stockx_id=data.get("stockxId") if data.get("stockxId") else None,
        stadium_goods_id=data.get("stadiumGoodsId")
        if data.get("stadiumGoodsId")
        else None,
        source=Platform(data["source"]) if data.get("source") else None,
        sizes=[],
        links=[],
        images=[],
    )

    for platform, link in data["links"].items():
        if link:
            sneaker.links.append(Link(platform=Platform(platform), url=link))

    if data.get("images"):
        if data.get("images").get("original"):
            sneaker.images.append(
                Image(position=0, url=data.get("images").get("original"))
            )
        if data.get("images").get("alternateAngles"):
            for i, url in enumerate(data.get("images").get("alternateAngles")):
                sneaker.images.append(Image(position=i + 1, url=url))

    return sneaker


async def migrate_sneakers(mongo_client: AsyncIOMotorClient, limit: int = 1):
    sneaker_collection = mongo_client[MONGO_DB_NAME].sneakers
    with Session(engine) as session:
        async for sneaker_data in sneaker_collection.find().limit(limit):
            sql_sneaker = transform_sneaker(sneaker_data)
            session.add(sql_sneaker)
        session.commit()


async def main():
    mongo_client = AsyncIOMotorClient(MONGO_URI)

    # Create tables if they don't exist
    SQLModel.metadata.create_all(engine)

    await migrate_sneakers(mongo_client, 3)

    mongo_client.close()


if __name__ == "__main__":
    asyncio.run(main())
