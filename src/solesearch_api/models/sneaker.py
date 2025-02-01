from datetime import datetime
from functools import reduce

from pydantic import computed_field
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from solesearch_api.models.base import TimestampedModel
from solesearch_api.models.enums import Audience, Platform, SizeStandard


class SneakerBase(SQLModel):
    brand: str | None = None
    sku: str | None = None
    name: str | None = None
    colorway: str | None = None
    audience: Audience | None = None
    release_date: datetime | None = None
    description: str | None = None


class Sneaker(SneakerBase, TimestampedModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    stockx_id: str | None = None
    stadium_goods_id: str | None = None
    source: Platform | None = None

    # Relationships
    links: list["Link"] = Relationship(back_populates="sneaker", cascade_delete=True)
    images: list["Image"] = Relationship(back_populates="sneaker", cascade_delete=True)
    sizes: list["SneakerSize"] = Relationship(
        back_populates="sneaker",
        cascade_delete=True,
    )

    def get_links(self) -> list[str]:
        return [link.url for link in self.links]

    def get_images(self) -> list[str]:
        return [image.url for image in sorted(self.images, key=lambda i: i.position)]

    def get_sizes(
        self,
        size_standard: SizeStandard = SizeStandard.MENS_US,
    ) -> list[str]:
        return [size.get_standardized(size_standard) for size in self.sizes]

    @property
    def prices(self) -> list["Price"]:
        return list(reduce(lambda x, y: x.prices + y.prices, self.sizes, []))

    def get_prices(self) -> list[int]:
        return [price.amount for price in self.prices]

    def merge(self, other=None):
        if other:
            stockx_images = [
                img for img in other.images if img.platform == Platform.stockx
            ]
            if stockx_images:
                self.images = stockx_images

            if len(other.colorway) > len(self.colorway):
                self.colorway = other.colorway


class SneakerPublic(SneakerBase):
    id: int

    @computed_field
    @property
    def links(self) -> list[str]:
        return self.get_links() if hasattr(self, "get_links") else []

    @computed_field
    @property
    def images(self) -> list[str]:
        return self.get_images() if hasattr(self, "get_images") else []

    @computed_field
    @property
    def sizes(self) -> list[str]:
        return self.get_sizes() if hasattr(self, "get_sizes") else []


class PaginatedSneakersPublic(SQLModel):
    total: int
    page: int
    page_size: int
    next_page: str | None
    previous_page: str | None
    items: list[SneakerPublic]


class SneakerSize(TimestampedModel, table=True):
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
