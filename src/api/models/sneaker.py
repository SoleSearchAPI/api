from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from api.models.base import TimestampedModel
from api.models.enums import Audience, Platform
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship


class Size(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: int = Field(unique=True, index=True)


class Price(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("platform", "sneaker_size_link_id"),
        Index("ix_platform_sneaker_size_link_id", "platform", "sneaker_size_link_id"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: Optional[Platform] = None
    amount: int  # Monetary values stored as US cents

    sneaker_size_link_id: int = Field(foreign_key="sneakersizelink.id")
    sneaker_size_link: SneakerSizeLink = Relationship(back_populates="price")


class SneakerSizeLink(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("sneaker_id", "size_id"),
        Index("ix_sneaker_id_size_id", "sneaker_id", "size_id"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="sneaker_sizes")

    size_id: int = Field(foreign_key="size.id")
    size: Size = Relationship(back_populates="sneaker_sizes")

    price_id: Optional[int] = Field(foreign_key="price.id")
    price: Optional[Price] = Relationship(back_populates="sneaker_size_link")


class Link(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("platform", "sneaker_id"),
        Index("ix_platform_sneaker_id", "platform", "sneaker_id"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: Platform
    url: str

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="links")


class Image(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: Platform
    is_primary: Optional[bool] = None
    url: str

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="images")

    # TODO: this is better handled by storing all images we scrape,
    # and then when accessing the images, we can sort by platform
    # in order of preference and return the first one
    # def merge(self, target):
    #     if target.url and target.platform:
    #         for preference in [
    #             Platform.stockx,
    #             Platform.goat,
    #             Platform.retail,
    #             Platform.stadium_goods,
    #         ]:


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

    def merge(self, other: Optional[Sneaker] = None):
        if other:
            stockx_images = [
                img for img in other.images if img.platform == Platform.stockx
            ]
            if stockx_images:
                self.images = stockx_images

            if len(other.colorway) > len(self.colorway):
                self.colorway = other.colorway
