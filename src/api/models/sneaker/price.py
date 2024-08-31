from typing import Optional

from api.models.base import TimestampedModel
from api.models.sneaker.enums import Platform
from api.models.sneaker.sneaker_size_link import SneakerSizeLink
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship


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
