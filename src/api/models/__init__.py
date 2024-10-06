from datetime import datetime
from functools import reduce
from typing import List

from sqlalchemy import event
from sqlmodel import Field, Index, Relationship, SQLModel, UniqueConstraint

from api.models.enums import Audience, Platform, SizeStandard
from api.utils.time import utc_now


class TimestampedModel(SQLModel):
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)


@event.listens_for(TimestampedModel, "before_update")
def update_timestamp(mapper, connection, target):
    target.updated_at = utc_now()


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
    links: list["Link"] = Relationship(back_populates="sneaker")
    images: list["Image"] = Relationship(back_populates="sneaker")
    sizes: list["SneakerSize"] = Relationship(back_populates="sneaker")

    @property
    def prices(self) -> List["Price"]:
        return List(reduce(lambda x, y: x.prices + y.prices, self.sizes, []))

    def get_links(self) -> List[str]:
        return [link.url for link in self.links]

    def get_images(self) -> List[str]:
        return [image.url for image in sorted(self.images, key=lambda i: i.position)]

    def get_sizes(
        self, size_standard: SizeStandard = SizeStandard.MENS_US
    ) -> List[str]:
        return [size.get_standardized(size_standard) for size in self.sizes]

    def merge(self, other=None):
        if other:
            stockx_images = [
                img for img in other.images if img.platform == Platform.stockx
            ]
            if stockx_images:
                self.images = stockx_images

            if len(other.colorway) > len(self.colorway):
                self.colorway = other.colorway


class SneakerSize(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("sneaker_id", "value"),
        Index("ix_sneaker_id_value", "sneaker_id", "value"),
    )
    id: int | None = Field(default=None, primary_key=True)
    value: int

    sneaker_id: int | None = Field(default=None, foreign_key="sneaker.id")
    sneaker: Sneaker | None = Relationship(back_populates="sizes")

    prices: list["Price"] = Relationship(back_populates="sneaker_size")

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

    sneaker_size_id: int | None = Field(default=None, foreign_key="sneakersize.id")
    sneaker_size: SneakerSize | None = Relationship(back_populates="prices")

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

    sneaker_id: int | None = Field(default=None, foreign_key="sneaker.id")
    sneaker: Sneaker | None = Relationship(back_populates="links")


class Image(TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("platform", "sneaker_id", "position"),
        Index("ix_image_platform_sneaker_id", "platform", "sneaker_id"),
    )
    id: int | None = Field(default=None, primary_key=True)
    platform: Platform | None = None
    position: int
    url: str

    sneaker_id: int | None = Field(default=None, foreign_key="sneaker.id")
    sneaker: Sneaker | None = Relationship(back_populates="images")


class SitemapLink(TimestampedModel, table=True):
    url: str = Field(primary_key=True)
    platform: Platform | None = None
    last_seen: datetime | None = None
    scraped: bool | None = None
    ignored: bool | None = None
    error: bool | None = None


class Token(TimestampedModel, table=True):
    platform: Platform | None = Field(primary_key=True)
    type: str | None = Field(primary_key=True)
    value: str
    expires: datetime | None = None


class Useragent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    useragent: str | None = None
