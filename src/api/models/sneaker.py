from __future__ import annotations

from datetime import datetime
from functools import reduce

from api.models.base import TimestampedModel
from api.models.enums import Audience, Platform, SizeStandard
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship


class Sneaker(TimestampedModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    brand: str | None = None
    sku: str | None = None
    name: str | None = None
    colorway: str | None = None
    audience: Audience | None = None
    release_date: datetime | None = None
    description: str | None = None
    stockx_id: str | None = None
    stadium_goods_id: str | None = None
    source: Platform | None = None
    date_added: datetime | None = None
    last_scraped: datetime | None = None

    # One to many relationships
    links: list[Link] = Relationship(back_populates="sneaker")
    images: list[Image] = Relationship(back_populates="sneaker")
    sizes: list[SneakerSize] = Relationship(back_populates="sneaker")

    @property
    def prices(self) -> list[Price]:
        return list(reduce(lambda x, y: x.prices + y.prices, self.sizes, []))

    def get_links(self) -> list[str]:
        return [link.url for link in self.links]

    def get_images(self) -> list[str]:
        return [image.url for image in sorted(self.images, key=lambda i: i.position)]

    def get_sizes(
        self, size_standard: SizeStandard = SizeStandard.MENS_US
    ) -> list[str]:
        return [size.get_standardized(size_standard) for size in self.sizes]

    def merge(self, other: Sneaker | None = None):
        if other:
            stockx_images = [
                img for img in other.images if img.platform == Platform.stockx
            ]
            if stockx_images:
                self.images = stockx_images

            if len(other.colorway) > len(self.colorway):
                self.colorway = other.colorway


class SneakerSize(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("sneaker_id", "value"),
        Index("ix_sneaker_id_value", "sneaker_id", "value"),
    )
    id: int | None = Field(default=None, primary_key=True)
    value: int

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="sizes")

    prices: list[Price] = Relationship(back_populates="sneakersize")

    def get_standardized(self, size_standard: SizeStandard = SizeStandard.MENS_US):
        if size_standard == SizeStandard.MENS_US:
            return self.value


class Price(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("sneaker_size_id", "platform"),
        Index("ix_sneaker_size_id_platform", "sneaker_size_id", "platform"),
    )
    id: int | None = Field(default=None, primary_key=True)
    platform: Platform | None = None
    amount: int  # Monetary values stored as US cents
    observed_at: datetime | None = None

    sneaker_size_id: int = Field(foreign_key="sneakersize.id")
    sneaker_size: SneakerSize = Relationship(back_populates="prices")

    @property
    def in_dollars(self) -> float:
        return self.amount / 100

    @property
    def for_size(self) -> int:
        return self.sneaker_size.value


class Link(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("platform", "sneaker_id"),
        Index("ix_link_platform_sneaker_id", "platform", "sneaker_id"),
        Index("ix_url", "url"),
    )
    id: int | None = Field(default=None, primary_key=True)
    platform: Platform
    url: str

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="links")


class Image(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("platform", "sneaker_id", "position"),
        Index("ix_image_platform_sneaker_id", "platform", "sneaker_id"),
    )
    id: int | None = Field(default=None, primary_key=True)
    platform: Platform | None = None
    position: int
    url: str

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="images")
