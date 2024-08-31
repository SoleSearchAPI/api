from typing import Optional

from api.models.base import TimestampedModel
from api.models.sneaker import Sneaker
from api.models.sneaker.price import Price
from api.models.sneaker.size import Size
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship


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
