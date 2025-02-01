from datetime import datetime

from sqlalchemy import event
from sqlmodel import Field, SQLModel

from solesearch_api.utils.time import utc_now


class TimestampedModel(SQLModel):
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "created_at" not in kwargs:
            self.created_at = utc_now()
        self.updated_at = self.created_at


@event.listens_for(TimestampedModel, "before_update")
def update_timestamp(mapper, connection, target):
    target.updated_at = utc_now()
