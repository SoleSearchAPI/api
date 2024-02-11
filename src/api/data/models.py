from enum import Enum
from typing import List

from core.models.details import Audience, Images, Links, Prices
from core.models.shoes import Sneaker
from pydantic import BaseModel, ValidationError


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
