from typing import List, Optional

from api.models.sneaker.price import Price
from sqlmodel import Field, Relationship, SQLModel


class Size(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    size: int = Field(unique=True)
    prices: List[Price] = Relationship(back_populates="size")
