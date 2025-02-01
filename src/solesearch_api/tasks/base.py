from celery import Task

from solesearch_api.db import SessionLocal


class IngestTask(Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        with SessionLocal() as session, session.begin():
            return self.run(session, *args, **kwargs)
