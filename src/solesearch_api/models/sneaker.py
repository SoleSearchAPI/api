from datetime import datetime
from functools import reduce

from pydantic import computed_field
from sqlmodel import Field, Relationship, SQLModel

from solesearch_common.models.base import TimestampedModel
from solesearch_common.models.enums import Audience, Platform, SizeStandard
from solesearch_common.models.image import Image
from solesearch_common.models.link import Link
from solesearch_common.models.price import Price
from solesearch_common.models.sneaker_size import SneakerSize


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
        back_populates="sneaker", cascade_delete=True
    )

    def get_links(self) -> list[str]:
        return [link.url for link in self.links]

    def get_images(self) -> list[str]:
        return [image.url for image in sorted(self.images, key=lambda i: i.position)]

    def get_sizes(
        self, size_standard: SizeStandard = SizeStandard.MENS_US
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
