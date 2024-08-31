from typing import Optional

from api.models.base import TimestampedModel
from api.models.sneaker import Sneaker
from api.models.sneaker.enums import Platform
from sqlmodel import Field, Relationship


class Image(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: Platform
    is_primary: Optional[bool] = None
    url: str

    sneaker_id: int = Field(foreign_key="sneaker.id")
    sneaker: Sneaker = Relationship(back_populates="images")

    # TODO: this is better handled by storing all images we scrape,
    # and then when accessing the images, we can sort by platform
    # in order of preference and return the first one
    # def merge(self, target):
    #     if target.url and target.platform:
    #         for preference in [
    #             Platform.stockx,
    #             Platform.goat,
    #             Platform.retail,
    #             Platform.stadium_goods,
    #         ]:
