from datetime import datetime

from api.utils.time import utc_now
from sqlalchemy import event
from sqlmodel import Field, SQLModel


class TimestampedModel(SQLModel):
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)


@event.listens_for(TimestampedModel, "before_update")
def update_timestamp(mapper, connection, target):
    target.updated_at = utc_now()
