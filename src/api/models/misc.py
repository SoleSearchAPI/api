from datetime import datetime
from typing import Optional

from api.models.sneaker.enums import Platform
from sqlmodel import Field, SQLModel


class Token(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: Optional[Platform] = None
    type: Optional[str] = None
    value: str
    expires: Optional[datetime] = None


class SitemapLink(SQLModel, table=True):
    url: str = Field(primary_key=True)
    platform: Optional[Platform] = None
    last_seen: Optional[datetime] = None
    scraped: Optional[bool] = None
    ignored: Optional[bool] = None
    error: Optional[bool] = None


class Useragent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    useragent: Optional[str] = None
