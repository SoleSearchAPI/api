from api.models.sneaker import Sneaker
from api.models.sneaker.size import Size
from sqlmodel import Field, Relationship, SQLModel


class SneakerSizeLink(SQLModel, table=True):
    sneaker_id: int = Field(foreign_key="sneaker.id", primary_key=True)
    sneaker: Sneaker = Relationship(back_populates="sneaker_sizes")

    size_id: int = Field(foreign_key="size.id", primary_key=True)
    size: Size = Relationship(back_populates="sneaker_sizes")
