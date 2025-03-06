import re
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import logfire

from solesearch_api.models.enums import Audience, Platform
from solesearch_api.models.sneaker import Image, Link, Price, Sneaker
from solesearch_api.tasks.db.base import create_or_update_sneaker
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
                Audience.MEN: ["MEN"],
                Audience.WOMEN: ["WOMEN"],
                Audience.UNISEX: ["MEN", "WOMEN"],
            },
            extractor=next_json_extractor,
        )

    def guess_audience(self, genders: list[str]) -> Audience:
        if "MEN" in genders and "WOMEN" in genders:
            return Audience.UNISEX
        elif "MEN" in genders:
            return Audience.MEN
        elif "WOMEN" in genders:
            return Audience.WOMEN
        return Audience.UNKNOWN

    def scrape(self, session, *args, **kwargs):
        json = self.get_json()
        sneakers = self.json_to_sneakers(json)
        for sneaker in sneakers:
            create_or_update_sneaker(session, sneaker)
        session.commit()

    def json_to_sneakers(self, json: dict) -> list[Sneaker]:
        threads = get_from_json(json, "product.threads.data.items")
        products = get_from_json(json, "product.products.data.items")
        upcoming_ids = get_from_json(json, "viewFeed.upcomingIds")
        sneakers = []
        for thread_id, thread in threads.items():
            for product_id in thread["productIds"]:
                product = products.get(product_id)
                if not product:
                    logfire.error(
                        "Nike product not found for thread",
                        attributes={
                            "thread_id": thread_id,
                            "product_id": product_id,
                        },
                    )
                    continue

                if product["productType"] != "FOOTWEAR":
                    logfire.info(
                        "Skipping product because it is not footwear",
                        attributes={
                            "product_id": product_id,
                            "product_type": product["productType"],
                        },
                    )
                    continue

                brand = product["brand"]
                sku = product["styleColor"]
                parent_sku = product["styleCode"]

                name = product["title"]
                colorway = product["colorDescription"]

                audience = self.guess_audience(product["genders"])

                try:
                    upcoming_id = next(
                        filter(
                            lambda x: x["threadId"] == thread_id,
                            upcoming_ids,
                        )
                    )
                    release_date = datetime.fromtimestamp(
                        upcoming_id.get("startEntryDate") / 1000
                    )
                    release_date = release_date.replace(
                        tzinfo=ZoneInfo("America/New_York")
                    )
                except StopIteration:
                    logfire.warning(
                        "Nike thread does not have an upcoming ID",
                        attributes={
                            "thread_id": thread_id,
                            "product_id": product_id,
                        },
                    )
                    release_date = None

                retail_price = product["fullPrice"] * 100

                if product.get("discounted"):
                    logfire.info(
                        "Nike has a discount on a product",
                        attributes={
                            "sku": sku,
                            "discounted": product["discounted"],
                            "fullPrice": retail_price,
                            "currentPrice": product["currentPrice"],
                            "msrp": product["msrp"],
                        },
                    )

                carousel = next(
                    filter(
                        lambda x: x["subType"] == "carousel",
                        thread["cards"],
                    )
                )
                try:
                    description = html_cleaner(carousel.get("description", ""))
                except Exception as e:
                    logfire.error(
                        "Error parsing description from Nike thread",
                        attributes={
                            "error": str(e),
                            "thread_id": thread_id,
                            "product_id": product_id,
                        },
                    )
                    description = None

                sneaker = Sneaker(
                    source=Platform.RETAIL,
                    brand=brand,
                    sku=sku,
                    parent_sku=parent_sku,
                    name=name,
                    colorway=colorway,
                    audience=audience,
                    release_date=release_date,
                    description=description,
                )

                slug = thread.get("seo", {}).get("slug")
                if not slug:
                    logfire.warning(
                        "Nike thread does not have a slug",
                        attributes={
                            "thread_id": thread_id,
                            "product_id": product_id,
                        },
                    )
                    url = f"https://www.nike.com/launch/thread/{thread_id}"
                else:
                    url = f"https://www.nike.com/launch/t/{slug}"

                sneaker_link = Link(
                    platform=Platform.RETAIL,
                    url=url,
                )
                sneaker.links = [sneaker_link]

                sneaker_images = []

                # First, check for 1st-level cards that are images and see if any productIds match
                position = 0
                for card in thread["cards"]:
                    if card["subType"] == "image":
                        if card.get("actions"):
                            # if any action has a productId that matches the current productId, use this image
                            for action in card["actions"]:
                                if action["product"]["productId"] == product_id:
                                    if card.get("imageId") and card.get("imageSlug"):
                                        image_url = f"https://static.nike.com/a/images/{card['imageId']}/{card['imageSlug']}.jpg"
                                    else:
                                        image_url = card["defaultURL"]
                                    sneaker_images.append(
                                        Image(
                                            platform=Platform.RETAIL,
                                            position=position,
                                            url=image_url,
                                        ),
                                    )
                                    position += 1
                if not sneaker_images:
                    for index, image in enumerate(carousel["cards"]):
                        if image["subType"] == "image":
                            if image.get("imageId") and image.get("imageSlug"):
                                image_url = f"https://static.nike.com/a/images/{image['imageId']}/{image['imageSlug']}.jpg"
                            else:
                                image_url = image["defaultURL"]
                            sneaker_images.append(
                                Image(
                                    platform=Platform.RETAIL,
                                    position=index,
                                    url=image_url,
                                ),
                            )
                sneaker.images = sneaker_images

                sneakers.append(sneaker)
        return sneakers


# Replace the class-based task registration with the decorator-based approach
nike_scraping_task = register_scraping_task(NikeScrapingTask)
