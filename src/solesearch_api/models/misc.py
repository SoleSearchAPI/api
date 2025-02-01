from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from solesearch_api.models.base import TimestampedModel
from solesearch_api.models.enums import Platform


class SitemapLink(TimestampedModel, table=True):
    url: str = Field(primary_key=True)
    platform: Platform | None = None
    last_seen: datetime | None = None
    scraped: bool | None = None
    ignored: bool | None = None
    error: bool | None = None


class Token(TimestampedModel, table=True):
    platform: Platform | None = Field(primary_key=True)
    type: str | None = Field(primary_key=True)
    value: str
    expires: datetime | None = None


class Useragent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    useragent: str | None = None


class TokenType(str, Enum):
    ID_TOKEN = "id_token"  # noqa: S105
    ACCESS_TOKEN = "access_token"  # noqa: S105
    REFRESH_TOKEN = "refresh_token"  # noqa: S105
