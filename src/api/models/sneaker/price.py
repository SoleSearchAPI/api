from typing import Optional

from api.models.sneaker.enums import Platform
from api.models.sneaker.sneaker_size import SneakerSize
from sqlmodel import Field, Relationship, SQLModel


class Price(SQLModel, table=True):
    id: int = Field(primary_key=True)
    platform: Optional[Platform] = None
    amount: int

    sneaker_size_id: int | None = Relationship(back_populates="price")
    sneaker_size: SneakerSize = Relationship(back_populates="prices")

    def merge(self, target):
        if self.platform == target.platform and target.amount > 0:
            # TODO: Add price history record in SQL?
            self.amount = target.amount
