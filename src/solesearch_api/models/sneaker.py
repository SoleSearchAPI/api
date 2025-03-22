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
    id: int | None = Field(default=None, primary_key=True)
    sku: str | None = None
    brand: str | None = None
    parent_sku: str | None = None
    name: str | None = None
    colorway: str | None = None
    audience: Audience | None = None
    release_date: datetime | None = None
    description: str | None = None
    retail_price: int | None = None


class Sneaker(SneakerBase, TimestampedModel, table=True):
    __table_args__ = (
        UniqueConstraint("sku", "brand", name="uix_sneaker_sku_brand"),
        Index("ix_sneaker_sku_brand", "sku", "brand"),
    )
    last_observed: datetime | None = None
    stockx_id: str | None = None
    stadium_goods_id: str | None = None
    source: Platform | None = None
    meta: dict = Field(sa_type=JSONB, default_factory=dict)

    # Relationships
    sneaker_links: list["Link"] = Relationship(
        back_populates="sneaker", cascade_delete=True
    )
    sneaker_images: list["Image"] = Relationship(
        back_populates="sneaker", cascade_delete=True
    )
    sneaker_sizes: list["SneakerSize"] = Relationship(
        back_populates="sneaker",
        cascade_delete=True,
    )
    nike_launches: list["NikeLaunch"] = Relationship(
        back_populates="sneaker", cascade_delete=True
    )


class SneakerPublic(SneakerBase):
    sneaker_links: list["Link"] = Field(default_factory=list, exclude=True)
    sneaker_images: list["Image"] = Field(default_factory=list, exclude=True)

    sneaker_sizes: list["SneakerSizePublic"] = Field(
        default_factory=list, alias="sizes"
    )

    @computed_field
    @property
    def retail_price_formatted(self) -> str | None:
        if self.retail_price is None:
            return None
        retail_price_in_dollars = Decimal(self.retail_price) / 100
        return f"${retail_price_in_dollars:.2f}"

    @computed_field
    @property
    def images(self) -> list[str]:
        return [
            img.url for img in sorted(self.sneaker_images, key=lambda x: x.position)
        ]

    @computed_field
    @property
    def links(self) -> dict[Platform, str]:
        return {link.platform: link.url for link in self.sneaker_links}


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
    sneaker: Sneaker | None = Relationship(back_populates="sneaker_sizes")

    sneaker_size_prices: list["Price"] = Relationship(back_populates="sneaker_size")


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
    sneaker_size: SneakerSize | None = Relationship(
        back_populates="sneaker_size_prices"
    )

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
    sneaker: Sneaker | None = Relationship(back_populates="sneaker_links")


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
    sneaker: Sneaker | None = Relationship(back_populates="sneaker_images")


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


class SneakerSizePublic(SQLModel):
    value: str
    size_standard: SizeStandard
    sneaker_size_prices: list["PricePublic"] = []


class PricePublic(SQLModel):
    platform: Platform | None = None
    amount: int

    @computed_field
    @property
    def amount_formatted(self) -> str:
        return f"${Decimal(self.amount) / 100:.2f}"

    last_observed: datetime | None = None
    first_observed: datetime | None = None
