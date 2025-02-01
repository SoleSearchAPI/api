from typing import TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from solesearch_api.models.base import TimestampedModel
from solesearch_api.models.enums import Platform

if TYPE_CHECKING:
    from solesearch_api.models.sneaker import Sneaker


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
    sneaker: "Sneaker" | None = Relationship(back_populates="images")
