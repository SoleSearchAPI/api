from bson import ObjectId

from data.instance import ASCENDING, DESCENDING, config, sneakers
from data.models import Audience


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


def find_sneakers(
    brand: str = None,
    sku: str = None,
    name: str = None,
    colorway: str = None,
    audience: Audience = None,
    releaseDate: float = None,
    released: bool = None,
    sort_key: str = "releaseDate",
    sort_dir: int = DESCENDING,
    offset: int = 0,
    limit: int = config.DEFAULT_LIMIT,
):
    sneakers.find(
        {
            field: value
            for field, value in {
                brand: brand,
                sku: sku,
                name: name,
                colorway: colorway,
                audience: audience,
                releaseDate: releaseDate,
                released: released,
            }.items()
            if value is not None
        }
    ).sort(sort_key, sort_dir).skip(offset).limit(limit)
