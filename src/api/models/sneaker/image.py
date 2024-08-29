from typing import Optional

from api.models.sneaker import Sneaker
from api.models.sneaker.enums import Platform
from sqlmodel import Field, Relationship, SQLModel


class Image(SQLModel, table=True):
    id: int = Field(primary_key=True)
    platform: Platform
    is_primary: Optional[bool] = None
    url: str

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="images")

    def merge(self, target):
        if target.url and target.platform:
            for preference in [
                Platform.stockx,
                Platform.goat,
                Platform.retail,
                Platform.stadium_goods,
            ]:
                if preference == self.platform:
                    break
                if preference == target.platform:
                    self.url = target.url
                    self.platform = target.platform
                    break
            # TODO: save the changes to the current model
