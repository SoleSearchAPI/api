from datetime import datetime
from zoneinfo import ZoneInfo

import logfire

from solesearch_api.models.enums import Audience, Platform, SizeStandard
from solesearch_api.models.sneaker import (
    Image,
    Link,
    NikeLaunch,
    Sneaker,
    SneakerSize,
)
from solesearch_api.tasks.db.base import create_or_update_sneaker
from solesearch_api.tasks.scraping.base import BaseScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task
from solesearch_api.utils.extractors import next_json_extractor
from solesearch_api.utils.json import get_from_json
from solesearch_api.utils.parsing import html_cleaner


class NikeNewReleasesScrapingTask(BaseScrapingTask):
    # This is the exact name that Celery is looking for
    def __init__(self):
        super().__init__(
            brand="Nike",
            download_url="https://www.nike.com/launch?s=upcoming",
            # See https://www.nike.com/size-fit/kids-footwear
            audience_mapping={
                "Big Kids' Shoes": Audience.GRADE_SCHOOL,
                "Little Kids' Shoes": Audience.PRESCHOOL,
                "Baby Crib Booties": Audience.TODDLER,
                "Baby/Toddler Shoes": Audience.TODDLER,
                "Women's Shoes": Audience.WOMEN,
            },
            extractor=next_json_extractor,
        )

    def guess_audience(self, genders: list[str], subtitle: str = None) -> Audience:
        if subtitle:
            guess = self.audience_mapping.get(subtitle.strip())
            if guess:
                return guess
        if "MEN" in genders and "WOMEN" in genders:
            return Audience.UNISEX
        elif "MEN" in genders:
            return Audience.MEN
        elif "WOMEN" in genders:
            return Audience.WOMEN
        return Audience.UNKNOWN

    def guess_size_standard(self, audience: Audience) -> SizeStandard:
        if audience in [Audience.GRADE_SCHOOL, Audience.PRESCHOOL, Audience.TODDLER]:
            return SizeStandard.KIDS_US
        elif audience == Audience.MEN:
            return SizeStandard.MENS_US
        elif audience == Audience.WOMEN:
            return SizeStandard.WOMENS_US
        return None

    def scrape(self, *args, **kwargs):
        json = self.get_json()
        sneakers = self.json_to_sneakers(json)
        for sneaker in sneakers:
            create_or_update_sneaker(sneaker)

    def json_to_sneakers(self, json: dict) -> list[Sneaker]:
        threads = get_from_json(json, "product.threads.data.items")
        products = get_from_json(json, "product.products.data.items")
        launch_views = get_from_json(json, "product.launchViews.data.items")
        upcoming_ids = get_from_json(json, "viewFeed.upcomingIds")
        sneakers = []
        for thread_id, thread in threads.items():
            hidden_from_upcoming_product_ids = thread.get(
                "hideFromUpcomingProductIds", []
            )
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
                if any(sku == sneaker.sku for sneaker in sneakers):
                    logfire.info(
                        "Skipping product because it was already encountered in this scrape in another thread",
                        attributes={
                            "sku": sku,
                            "thread_id": thread_id,
                            "product_id": product_id,
                        },
                    )
                    continue
                parent_sku = product["styleCode"]

                name = product["title"]
                colorway = product["colorDescription"]

                audience = self.guess_audience(
                    product["genders"], product.get("subtitle")
                )

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

                launch_data = launch_views.get(product_id, {})
                launch_id = launch_data.get("launchViewId")

                sneaker = Sneaker(
                    source=Platform.RETAIL,
                    brand=brand,
                    sku=sku,
                    parent_sku=parent_sku,
                    name=name,
                    colorway=colorway,
                    audience=audience,
                    release_date=release_date,
                    retail_price=retail_price,
                    description=description,
                    meta={
                        "product_id": product_id,
                        "thread_id": thread_id,
                        "launch_id": launch_id,
                        "genders": product.get("genders"),
                        "subtitle": product.get("subtitle"),
                        "hidden_from_upcoming": bool(
                            product_id in hidden_from_upcoming_product_ids
                        ),
                        "pid": product.get("pid"),
                        "is_active": product.get("isActive"),
                        "is_apparel": product.get("isApparel"),
                        "launch_status": product.get("launchStatus"),
                        "manufacturing_country_of_origin": product.get(
                            "manufacturingCountryOfOrigin"
                        ),
                        "merch_group": product.get("merchGroup"),
                        "msrp": product.get("msrp"),
                        "pid": product.get("pid"),
                        "full_price": product.get("fullPrice"),
                        "current_price": product.get("currentPrice"),
                        "discounted": product.get("discounted"),
                        "exclusive_access": product.get("exclusiveAccess"),
                    },
                )

                if launch_id:
                    launch_method = launch_data.get("method")
                    payment_method = launch_data.get("paymentMethod")
                    start_entry_date = launch_data.get("startEntryDate")
                    if start_entry_date:
                        start_entry_date = datetime.fromisoformat(start_entry_date)
                    stop_entry_date = launch_data.get("stopEntryDate")
                    if stop_entry_date:
                        stop_entry_date = datetime.fromisoformat(stop_entry_date)
                    stop_notify_date = launch_data.get("stopNotifyDate")
                    if stop_notify_date:
                        stop_notify_date = datetime.fromisoformat(stop_notify_date)
                    merch_product_status = launch_data.get("merchProductStatus")
                    is_launch_product = launch_data.get("isLaunchProduct")
                    last_observed = launch_data.get("fetchedAt")
                    if last_observed:
                        last_observed = datetime.fromisoformat(last_observed)
                    launch = NikeLaunch(
                        launch_id=launch_id,
                        product_id=product_id,
                        launch_method=launch_method,
                        payment_method=payment_method,
                        start_entry_date=start_entry_date,
                        stop_entry_date=stop_entry_date,
                        stop_notify_date=stop_notify_date,
                        merch_product_status=merch_product_status,
                        is_launch_product=is_launch_product,
                        last_observed=last_observed,
                    )
                    sneaker.nike_launches.append(launch)
                else:
                    logfire.warning(
                        "Nike launch ID not found for product",
                        attributes={
                            "product_id": product_id,
                            "thread_id": thread_id,
                            "launch_data": launch_data,
                        },
                    )

                slug = thread.get("seo", {}).get("slug")
                external_link = thread.get("externalLink")
                if not (external_link or slug):
                    logfire.warning(
                        "Nike thread does not have a slug or external link",
                        attributes={
                            "thread_id": thread_id,
                            "product_id": product_id,
                        },
                    )
                    url = f"https://www.nike.com/launch/thread/{thread_id}"
                else:
                    url = external_link or f"https://www.nike.com/launch/t/{slug}"

                sneaker_link = Link(
                    platform=Platform.RETAIL,
                    url=url,
                )
                sneaker.sneaker_links = [sneaker_link]

                sneaker_images = []

                # First, check for 1st-level cards that are images and see if any productIds match
                position = 0
                for card in thread["cards"]:
                    if card["subType"] == "image" and card.get("actions"):
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
                sneaker.sneaker_images = sneaker_images

                size_standard = self.guess_size_standard(sneaker.audience)
                if not size_standard:
                    logfire.warning(
                        "Nike size standard not found for sneaker",
                        attributes={"sku": sneaker.sku},
                    )
                else:
                    for size in product.get("skus", []):
                        size_value = size.get("nikeSize")
                        sneaker_size = SneakerSize(
                            value=size_value, size_standard=size_standard, meta=size
                        )
                        sneaker.sneaker_sizes.append(sneaker_size)

                sneakers.append(sneaker)
        return sneakers


# Replace the class-based task registration with the decorator-based approach
nike_new_releases_task = register_scraping_task(NikeNewReleasesScrapingTask)
