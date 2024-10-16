from celery import Task
from api.db import SessionLocal


class IngestTask(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        with SessionLocal() as session:
            with session.begin():
                return self.run(session, *args, **kwargs)
