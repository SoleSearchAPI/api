from celery import Task
from sqlmodel import Session

from solesearch_api.db import engine


class IngestTask(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        with Session(engine) as session, session.begin():
            return self.run(session, *args, **kwargs)
