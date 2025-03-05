from typing import Callable

from sqlmodel import Session, select

from solesearch_api.db import engine
from solesearch_api.models.sneaker import Sneaker
from solesearch_api.tasks import app


@app.task(name="create_or_update_sneaker")
@app.task(name="create_or_update_sneaker")
def create_or_update_sneaker(
    session: Session,
    sku: str,
    brand: str,
    json: dict,
    json_to_sneaker: Callable[[dict], Sneaker],
):
    with Session(engine) as session:
        # Check if sneaker already exists
        statement = select(Sneaker).where(Sneaker.sku == sku, Sneaker.brand == brand)
        sneaker = session.exec(statement).first()

        if sneaker:
            return

        sneaker = json_to_sneaker(json)
        session.add(sneaker)
        session.commit()
