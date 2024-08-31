from datetime import datetime
from typing import Optional

from api.models.base import TimestampedModel
from api.models.sneaker.enums import Platform
from sqlmodel import Field, SQLModel


class Token(TimestampedModel, table=True):
    platform: Optional[Platform] = Field(primary_key=True)
    type: Optional[str] = Field(primary_key=True)
    value: str
    expires: Optional[datetime] = None


class Useragent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    useragent: Optional[str] = None
