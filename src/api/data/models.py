from enum import Enum
from typing import List

from beanie import Document
from pydantic import BaseModel

from core.models.shoes import Sneaker, SneakerView


class Token(Document):
    type: str
    token: str

    class Settings:
        collection = "OAuth"


class PaginatedSneakersResponse(BaseModel):
    total: int
    page: int
    pageSize: int
    nextPage: str | None
    previousPage: str | None
    items: List[SneakerView]


class SortKey(str, Enum):
    BRAND = "brand"
    SKU = "sku"
    NAME = "name"
    COLORWAY = "colorway"
    AUDIENCE = "audience"
    RELEASE_DATE = "releaseDate"
    PRICE = "price"


class SortOrder(str, Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"
