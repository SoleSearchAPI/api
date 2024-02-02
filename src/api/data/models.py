from enum import Enum
from typing import List

from pydantic import BaseModel, ValidationError

from core.models.details import Audience, Images, Links, Prices
from core.models.shoes import Shoe


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
