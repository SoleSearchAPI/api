from enum import Enum
from typing import List

from core.models.shoes import SneakerView
from pydantic import BaseModel


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
