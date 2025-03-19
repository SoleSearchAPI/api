from datetime import datetime
from decimal import Decimal
from functools import reduce

from pydantic import computed_field
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from solesearch_api.models.base import TimestampedModel
from solesearch_api.models.enums import Audience, Platform, SizeStandard


class SneakerBase(SQLModel):
    brand: str | None = None
    sku: str | None = None
    parent_sku: str | None = None
    name: str | None = None
    colorway: str | None = None
    audience: Audience | None = None
    release_date: datetime | None = None
    description: str | None = None
    retail_price: int | None = None  # Monetary values stored as US cents


class Sneaker(SneakerBase, TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("sku", "brand", name="uix_sneaker_sku_brand"),
        Index("ix_sneaker_sku_brand", "sku", "brand"),
    )
    id: int | None = Field(default=None, primary_key=True)
    last_observed: datetime | None = None
    stockx_id: str | None = None
    stadium_goods_id: str | None = None
    source: Platform | None = None
    meta: dict = Field(sa_type=JSONB, default_factory=dict)

    # Relationships
    links: list["Link"] = Relationship(back_populates="sneaker", cascade_delete=True)
    images: list["Image"] = Relationship(back_populates="sneaker", cascade_delete=True)
    sizes: list["SneakerSize"] = Relationship(
        back_populates="sneaker",
        cascade_delete=True,
    )
    nike_launches: list["NikeLaunch"] = Relationship(
        back_populates="sneaker", cascade_delete=True
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
    def retail_price_formatted(self) -> str | None:
        if self.retail_price is None:
            return None
        retail_price_in_dollars = Decimal(self.retail_price) / 100
        return f"${retail_price_in_dollars:.2f}"

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
        UniqueConstraint("sneaker_id", "value", "size_standard"),
        Index(
            "ix_sneaker_id_value_size_standard",
            "sneaker_id",
            "value",
            "size_standard",
        ),
    )
    id: int | None = Field(default=None, primary_key=True)
    value: str
    size_standard: SizeStandard
    meta: dict = Field(sa_type=JSONB, default_factory=dict)

    sneaker_id: int | None = Field(default=None, foreign_key="sneaker.id")
    sneaker: Sneaker | None = Relationship(back_populates="sizes")

    prices: list["Price"] = Relationship(back_populates="sneaker_size")


class Price(SQLModel, table=True):
    # Ordered by last_observed timestamp
    __table_args__ = (
        Index("ix_sneaker_size_id_platform", "sneaker_size_id", "platform"),
        Index("ix_amount", "amount"),
        Index("ix_last_observed", "last_observed"),
        Index("ix_first_observed", "first_observed"),
    )
    id: int | None = Field(default=None, primary_key=True)
    platform: Platform | None = None
    amount: int  # Monetary values stored as US cents
    first_observed: datetime | None = None
    last_observed: datetime | None = None

    sneaker_size_id: int | None = Field(default=None, foreign_key="sneakersize.id")
    sneaker_size: SneakerSize | None = Relationship(back_populates="prices")

    @property
    def in_dollars(self) -> Decimal:
        return Decimal(self.amount) / 100


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


class NikeLaunch(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("product_id", "launch_id"),
        Index("ix_product_id_launch_id", "product_id", "launch_id"),
    )
    id: int | None = Field(default=None, primary_key=True)

    sneaker_id: int | None = Field(default=None, foreign_key="sneaker.id")
    sneaker: Sneaker | None = Relationship(back_populates="nike_launches")

    launch_id: str
    product_id: str
    launch_method: str | None = None
    payment_method: str | None = None
    launch_link: str | None = None
    start_entry_date: datetime | None = None
    stop_entry_date: datetime | None = None
    stop_notify_date: datetime | None = None
    merch_product_status: str | None = None
    is_launch_product: bool | None = None
    last_observed: datetime | None = None
