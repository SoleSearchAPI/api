from typing import Optional

from api.models.base import TimestampedModel
from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from .enums import Platform
from .sneaker import Sneaker


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
