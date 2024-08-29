from api.models.sneaker import Sneaker
from api.models.sneaker.enums import Platform
from sqlmodel import Field, Relationship, SQLModel


class Link(SQLModel, table=True):
    id: int = Field(primary_key=True)
    platform: Platform
    url: str

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="links")
