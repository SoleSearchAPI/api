from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from solesearch_common.models.base import TimestampedModel
from solesearch_common.models.enums import Platform
from solesearch_common.models.sneaker import Sneaker


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
