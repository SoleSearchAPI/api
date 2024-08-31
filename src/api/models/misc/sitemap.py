from datetime import datetime
from typing import Optional

from api.models.base import TimestampedModel
from api.models.sneaker.enums import Platform
from sqlmodel import Field


class SitemapLink(TimestampedModel, table=True):
    url: str = Field(primary_key=True)
    platform: Optional[Platform] = None
    last_seen: Optional[datetime] = None
    scraped: Optional[bool] = None
    ignored: Optional[bool] = None
    error: Optional[bool] = None
