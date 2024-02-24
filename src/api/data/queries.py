import logging
from datetime import UTC, datetime

from bson import ObjectId

from api.data.instance import DEFAULT_LIMIT, DEFAULT_OFFSET, db, sneakers
from api.data.models import SortKey, SortOrder
from core.models.details import Audience


def find_sneaker_by_id(id: str = ""):
    if not id:
        raise ValueError("The supplied productId cannot be null")
    return sneakers.find_one({"_id": ObjectId(id)})


def find_sneaker_by_sku(sku: str = "", brand=None):
    if not sku:
        raise ValueError("The supplied SKU cannot be null")
    query = {"sku": sku}
    if brand:
        query["brand"] = brand
    return sneakers.find_one(query)


async def find_sneakers(
    brand: str = None,
    sku: str = None,
    name: str = None,
    colorway: str = None,
    audience: Audience = None,
    release_date: str = None,
    released: bool = None,
    sort_by: SortKey = SortKey.RELEASE_DATE,
    sort_order: SortOrder = SortOrder.DESCENDING,
    offset: int = DEFAULT_OFFSET,
    limit: int = DEFAULT_LIMIT,
):
    query = {
        field: value
        for field, value in {
            "brand": brand,
            "sku": sku,
            "name": name,
            "colorway": colorway,
            "audience": audience,
        }.items()
        if value is not None
    }

    if released is not None:
        if released is True:
            query["releaseDate"]["$lte"] = datetime.now(UTC)
        else:
            query["releaseDate"]["$gt"] = datetime.now(UTC)
    elif release_date:
        if ":" in release_date:
            inequality_operator = release_date.split(":")[0]
            if inequality_operator in ["lt", "lte", "gt", "gte"]:
                query["releaseDate"][f"${inequality_operator}"] = datetime.strptime(
                    release_date.split(":")[1], "%Y-%m-%d"
                )
        else:
            query["releaseDate"] = datetime.strptime(release_date, "%Y-%m-%d")

    response_list = (
        await sneakers.find(query)
        .sort(sort_by, 1 if sort_order == SortOrder.ASCENDING else -1)
        .skip(offset)
        .limit(limit)
        .to_list(length=limit)
    )

    for item in response_list:
        item["id"] = str(item["_id"])
        del item["_id"]

    return response_list


async def update_tokens(tokens: dict = {}):
    if "id_token" in tokens:
        db["OAuth"].update_one(
            {"type": "id_token"},
            {"$set": {"token": tokens["id_token"]}},
        )
        logging.info("Updated id_token")
    if "access_token" in tokens:
        db["OAuth"].update_one(
            {"type": "access_token"},
            {"$set": {"token": tokens["access_token"]}},
        )
        logging.info("Updated access_token")
    if "refresh_token" in tokens:
        db["OAuth"].update_one(
            {"type": "refresh_token"},
            {"$set": {"token": tokens["refresh_token"]}},
        )
        logging.info("Updated refresh_token")
