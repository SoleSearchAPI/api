import logging
from datetime import datetime

from core.models.details import Audience, Images, Links, Prices
from core.models.shoes import Shoe
from ingest.db.instance import kof_collection
from ingest.db.mutations import upsert_many
from ingest.utils.helpers import try_guess_audience, try_guess_brand

logger = logging.getLogger(__name__)


def execute() -> None:
    kof_cursor = kof_collection.find({})
    sneakers = []
    for i, kof_shoe in enumerate(kof_cursor):
        sneakers.append(shoe_from_json(kof_shoe))
        if i % 1000 == 0:
            upsert_many(sneakers)
            sneakers = []
    if sneakers:
        upsert_many(sneakers)
    logger.info("Done!")


def shoe_from_json(json: dict) -> Shoe:
    release_date = datetime.fromtimestamp(json["releaseDate"])
    return Shoe(
        brand=try_guess_brand(json["brand"]),
        sku=json["sku"],
        name=json["name"],
        colorway=json["colorway"],
        audience=try_guess_audience(json["audience"]),
        release_date=release_date,
        released=json["released"],
        images=Images(
            original=json["images"]["original"],
            alternateAngles=json["images"]["alternateAngles"],
        ),
        links=Links(
            stockx=json["links"]["stockx"],
            retail=json["links"]["retail"],
            goat=json["links"]["goat"],
        ),
        prices=Prices(
            stockx=json["prices"]["stockx"],
            retail=json["prices"]["retail"],
            goat=json["prices"]["goat"],
        ),
        sizes=json["sizes"]["sizes"],
        description=json["description"],
        dateAdded=datetime.fromtimestamp(json["dateAdded"]),
    )
