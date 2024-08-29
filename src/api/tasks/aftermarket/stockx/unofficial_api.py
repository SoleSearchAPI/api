import json
from datetime import UTC, datetime
from typing import List

from core.models.details import Images, Links, Prices
from core.models.shoes import Sneaker
from ingest.db.mutations import upsert, upsert_many
from ingest.models.task import IngestInterface
from ingest.utils.helpers import merge_dot_notated_keys, try_guess_audience
from ingest.utils.sessions import session


def json_to_model(self, product: dict) -> Sneaker:
    product = merge_dot_notated_keys(product)
    stockx_price = product["market"]
    stockx_price["lowestAskThresholdMet"] = product["lowestAskThresholdMet"]
    stockx_price["lowestAskRange"] = product["lowestAskRange"]
    stockx_price["greatValues"] = product["greatValues"]
    stockx_price["belowRetail"] = product["belowRetail"]
    stockx_price["tickerSymbol"] = product["tickerSymbol"]
    stockx_price["discountPercentage"] = product["discountPercentage"]
    return Sneaker(
        stockxId=product["uuid"],
        brand=product["brand"],
        name=product["title"],
        sku=product["styleId"],
        sillhouette=product["shoe"],
        colorway=product["colorway"],
        description=product["description"],
        prices=Prices(stockx_price, retail_price=product["retailPrice"]),
        links=Links(stockx=f"https://stockx.com/{product['urlKey']}".strip()),
        releaseDate=datetime.fromtimestamp(float(product["releaseTime"]), UTC),
        images=Images(
            original=product["media"]["imageUrl"],
            alternateAngles=product["media"]["gallery"],
        ),
        audience=try_guess_audience(product["gender"]),
    )


class StockXUnofficialApiIngest(IngestInterface):
    def scrape(self, page: int) -> tuple[bool, List[dict] | dict]:
        response = session.get(
            "https://stockx.com/api/browse",
            params={
                "_tags": "sneakers",
                "page": page,
            },
        )
        if response.status_code == 200:
            data = response.json()
            if len(data["Products"]) == 0 or not data["Pagination"]["nextPage"]:
                return [False, {}]
            return [True, data["Products"]]
        else:
            return [False, {}]

    def execute(self) -> None:
        shouldContinue = True
        page = 1
        while shouldContinue:
            sneakers = []
            shouldContinue, products = self.scrape(page)
            if not shouldContinue:
                break
            for product in products:
                sneakers.append(json_to_model(product))
            upsert_many(sneakers)
            page += 1

    def get_single_product(self, style_id: str) -> Sneaker:
        response = session.get(
            "https://stockx.com/api/browse",
            params={
                "_tags": f"style_id|{style_id.strip().lower()}",
            },
        )
        if response.status_code == 200:
            data = json.loads(response.text)
            if len(data["Products"]) > 0:
                sneaker_model = self.json_to_model(data["Products"][0])
                upsert(sneaker_model)
                return sneaker_model
            else:
                raise Exception(f"No product found with style_id: {style_id}")
        else:
            raise Exception(f"Error: {response.status_code}")
