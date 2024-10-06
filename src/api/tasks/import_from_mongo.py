import asyncio
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorClient
from sqlmodel import Session, SQLModel, create_engine

from api.models import Image, Link, Sneaker
from api.models.enums import Audience, Platform

# MongoDB connection
MONGO_URI = "mongodb://root:example@localhost:27017/"
MONGO_DB_NAME = "Sneakers"

# PostgreSQL connection
POSTGRES_URI = "postgresql://solesearch:solesearch@localhost/Sneakers"

# Create synchronous engine
engine = create_engine(POSTGRES_URI, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def transform_sneaker(data: Dict[str, Any]) -> Sneaker:
    """
    Transform the data from MongoDB format to SQLModel format.
    Implement your data transformation logic here.
    """
    sneaker_links = []
    for platform, link in data.get("links", {}).items():
        if link:
            sneaker_links.append(Link(platform=Platform(platform), url=link))

    sneaker_images = []
    if data.get("images"):
        if data.get("images").get("original"):
            sneaker_images.append(
                Image(position=0, url=data.get("images").get("original"))
            )
        if data.get("images").get("alternateAngles"):
            for i, url in enumerate(data.get("images").get("alternateAngles")):
                sneaker_images.append(Image(position=i + 1, url=url))

    sneaker = Sneaker(
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
        links=sneaker_links,
        images=sneaker_images,
    )

    return sneaker


async def migrate_sneakers(mongo_client: AsyncIOMotorClient):
    sneaker_collection = mongo_client[MONGO_DB_NAME].sneakers
    batch_size = 1000
    with Session(engine) as session:
        while True:
            cursor = sneaker_collection.find().limit(batch_size)
            batch_empty = True
            processed_ids = []
            async for sneaker_data in cursor:
                batch_empty = False
                sql_sneaker = transform_sneaker(sneaker_data)
                session.add(sql_sneaker)
                processed_ids.append(sneaker_data["_id"])
            if batch_empty:
                break
            try:
                session.commit()
                await sneaker_collection.delete_many({"_id": {"$in": processed_ids}})
            except Exception as e:
                session.rollback()
                print(f"Session commit failed: {e}")
                break


async def main():
    mongo_client = AsyncIOMotorClient(MONGO_URI)

    await migrate_sneakers(mongo_client)

    mongo_client.close()


if __name__ == "__main__":
    create_db_and_tables()
    asyncio.run(main())
