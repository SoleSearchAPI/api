from datetime import datetime
from typing import List, Optional

from api.models.base import TimestampedModel
from sqlmodel import Field, Relationship

from .enums import Audience, Platform
from .image import Image
from .link import Link
from .price import Price
from .size import Size
from .sneaker_size_link import SneakerSizeLink


class Sneaker(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    brand: Optional[str] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    colorway: Optional[str] = None
    audience: Optional[Audience] = None
    release_date: Optional[datetime] = None
    description: Optional[str] = None
    stockx_id: Optional[str] = None
    stadium_goods_id: Optional[str] = None
    source: Optional[Platform] = None
    date_added: Optional[datetime] = None
    last_scraped: Optional[datetime] = None

    links: List[Link] = Relationship(back_populates="sneaker")
    images: List[Image] = Relationship(back_populates="sneaker")
    sneaker_sizes: List[SneakerSizeLink] = Relationship(back_populates="sneaker")

    @property
    def sizes(self) -> List[Size]:
        return [sneaker_size.size for sneaker_size in self.sneaker_sizes]

    @property
    def prices(self) -> List[Price]:
        return [sneaker_size.price for sneaker_size in self.sneaker_sizes]

    def merge(self, other: Optional["Sneaker"] = None):
        if other:
            stockx_images = [
                img for img in other.images if img.platform == Platform.stockx
            ]
            if stockx_images:
                self.images = stockx_images

            if len(other.colorway) > len(self.colorway):
                self.colorway = other.colorway