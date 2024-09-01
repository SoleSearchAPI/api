from sqlmodel import Session, SQLModel, create_engine

import api.models  # noqa: F401
from api.config import DB_URL, ENVIRONMENT
from api.models.env import Environment

engine = create_engine(DB_URL, echo=ENVIRONMENT != Environment.PRODUCTION)


def initialize_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
