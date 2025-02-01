from typing import TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from solesearch_api.models.enums import SizeStandard

if TYPE_CHECKING:
    from solesearch_api.models.price import Price
    from solesearch_api.models.sneaker import Sneaker


class SneakerSize(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("sneaker_id", "value"),
        Index("ix_sneaker_id_value", "sneaker_id", "value"),
    )
    id: int | None = Field(default=None, primary_key=True)
    value: int

    sneaker_id: int | None = Field(default=None, foreign_key="sneaker.id")
    sneaker: "Sneaker" | None = Relationship(back_populates="sizes")

    prices: list["Price"] = Relationship(back_populates="sneaker_size")

    def get_standardized(self, size_standard: SizeStandard = SizeStandard.MENS_US):
        if size_standard == SizeStandard.MENS_US:
            return self.value
