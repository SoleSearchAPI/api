from datetime import datetime

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship

from solesearch_common.models.base import TimestampedModel
from solesearch_common.models.enums import Platform
from solesearch_common.models.sneaker_size import SneakerSize


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
