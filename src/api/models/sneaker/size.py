from typing import Optional

from api.models.base import TimestampedModel
from sqlmodel import Field


class Size(TimestampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: int = Field(unique=True, index=True)
