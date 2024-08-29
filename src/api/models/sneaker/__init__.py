from datetime import datetime
from typing import List, Optional

from api.models.sneaker.enums import Audience, Platform
from api.models.sneaker.image import Image
from api.models.sneaker.link import Link
from api.models.sneaker.price import Price
from api.models.sneaker.sneaker_size import SneakerSizeLink
from sqlmodel import Field, Relationship, SQLModel


class Sneaker(SQLModel, table=True):
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
    # todo: investigate how to do this properly using the SneakerSizeLink table
    # prices: List[Price] = Relationship(back_populates="sneaker")
    images: List[Image] = Relationship(back_populates="sneaker")
    sneaker_sizes: List[SneakerSizeLink] = Relationship(back_populates="sneaker")

    def merge(self, other: Optional["Sneaker"] = None):
        if other:
            stockx_images = [
                img for img in other.images if img.platform == Platform.stockx
            ]
            if stockx_images:
                self.images = stockx_images

            if len(other.colorway) > len(self.colorway):
                self.colorway = other.colorway
