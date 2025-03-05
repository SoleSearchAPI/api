import re
from datetime import UTC, datetime

from solesearch_api.models.enums import Audience, Platform
from solesearch_api.models.sneaker import Image, Link, Price, Sneaker
from solesearch_api.tasks.scraping.base import BaseScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task
from solesearch_api.utils.extractors import next_json_extractor
from solesearch_api.utils.json import get_from_json
from solesearch_api.utils.parsing import html_cleaner


class NikeScrapingTask(BaseScrapingTask):
    # This is the exact name that Celery is looking for
    name = "solesearch_api.tasks.scraping.NikeScrapingTask"

    def __init__(self):
        super().__init__(
            brand="Nike",
            download_url="https://www.nike.com/launch?s=upcoming",
            audience_mapping={
                "Men": Audience.MEN,
                "Women": Audience.WOMEN,
                "Unisex": Audience.UNISEX,
            },
            extractor=next_json_extractor,
        )

    def scrape(self, session, *args, **kwargs):
        json = self.get_json()
        sneakers = self.json_to_sneakers(json)
        for sneaker in sneakers:
            session.add(sneaker)

    def json_to_sneakers(self, json: dict) -> list[Sneaker]:
        products = get_from_json(json, "product.threads.data.items")
        product_details = get_from_json(json, "product.products.data.items")
        more_details = {
            x["threadId"]: (x["productId"], x["startEntryDate"])
            for x in json["viewFeed"]["upcomingIds"]
        }
        sneakers = []
        for thread_id in products:
            product_id = more_details.get(thread_id)
            if product_id:
                product_id = product_id[0]
            else:
                raise ValueError(f"Missing product_id for thread_id: {thread_id}")

            product = products[thread_id]
            details = product_details.get(product_id)
            if not details:
                raise ValueError(
                    f"Missing product details for product_id: {product_id}",
                )

            if details["productType"] != "FOOTWEAR":
                raise ValueError(
                    f"Product was type {details['productType']}, not footwear!",
                )

            sku = details["styleColor"]
            brand = details["brand"]
            name = re.sub(r" \(.*-.*\) Release Date", "", product["seo"]["title"])
            colorway = details["colorDescription"]
            audience = self.guess_audience(details["genders"])
            release_date = more_details[thread_id][1]
            description = html_cleaner(
                next(
                    filter(
                        lambda x: x["subType"] == "carousel",
                        product["cards"],
                    ),
                )["description"],
            )

            sneaker = Sneaker(
                source=Platform.RETAIL,
                brand=brand,
                sku=sku,
                name=name,
                colorway=colorway,
                audience=audience,
                release_date=release_date,
                description=description,
            )

            sneaker_link = Link(
                platform=Platform.RETAIL,
                url=product["externalLink"],
            )
            sneaker.links = [sneaker_link]

            sneaker_images = []
            for index, image in enumerate(product["cards"]):
                if image["subType"] == "image":
                    sneaker_images.append(
                        Image(
                            platform=Platform.RETAIL,
                            position=index,
                            url=image["defaultURL"],
                        ),
                    )
            sneaker.images = sneaker_images

            sneaker_price = Price(
                platform=Platform.RETAIL,
                amount=details.get("msrp", details.get("fullPrice", None)),
                observed_at=datetime.now(UTC),
            )
            sneaker.prices = [sneaker_price]

            sneakers.append(sneaker)
        return sneakers


# Replace the class-based task registration with the decorator-based approach
nike_scraping_task = register_scraping_task(NikeScrapingTask)
