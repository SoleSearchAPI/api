from sqlmodel import Session

from solesearch_api.db import engine


class IngestTask:
    def run(self, *args, **kwargs):
        with Session(engine) as session, session.begin():
            return self.ingest(session, *args, **kwargs)
