from enum import Enum
from typing import List

from pydantic import BaseModel, ValidationError


class Audience(str, Enum):
    UNISEX = "Unisex"
    MEN = "Men"
    WOMEN = "Women"
    BOYS = "Boys"
    GIRLS = "Girls"
    KIDS = "Kids"
    TODDLER = "Toddler"


class Links(BaseModel):
    retail: str = None  # Link to the retail page
    stockx: str = None  # Link to the StockX listing
    goat: str = None  # Link to the GOAT listing


class Prices(BaseModel):
    retail: float = None  # The retailer's price / MSRP
    stockx: float = None  # Current price on stockX
    goat: float = None  # Current price on GOAT


class Images(BaseModel):
    original: str = None  # Link to the head-on, full size image
    alternateAngles: List[
        str
    ] = None  # Links to other angles of the product, if available


class Sizes(BaseModel):
    # sizes stores all available sizes converted to US Men's.
    # Methods are provided for converting to other sizes.
    # If a size is not available, it is not included in the list.
    sizes: List[int] = None


class Sneaker(BaseModel):
    brand: str  # The shoe manufacturer
    sku: str  # Stock Keeping Unit, format typically differs by retailer
    name: str  # Product name
    colorway: str  # Colorway of the shoe
    audience: Audience  # See src.models.details.Audience
    releaseDate: float  # Release date in epoch time (milliseconds)
    released: bool  # true if product is available yet, false otherwise
    images: Images  # See src.models.details.Images
    links: Links  # See src.models.details.Links
    prices: Prices  # See src.models.details.Prices
    sizes: Sizes  # See src.models.details.Sizes
    description: str  # Long-form product description
