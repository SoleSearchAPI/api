from datetime import datetime
from zoneinfo import ZoneInfo

import logfire
from constructor_io.constructor_io import ConstructorIO

from solesearch_api.models.enums import Audience, Platform
from solesearch_api.models.sneaker import Image, Link, Sneaker, SneakerSize
from solesearch_api.tasks.db.base import create_or_update_sneaker
from solesearch_api.tasks.scraping.base import BaseScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task


class GoatScrapingTask(BaseScrapingTask):
    def __init__(self):
        super().__init__(
            brand="GOAT",
            audience_mapping={},  # We'll set audience to UNKNOWN
            download_url=None,  # We'll use constructor.io SDK instead
        )
        self.client = ConstructorIO(
            {
                "api_key": "key_XT7bjdbvjgECO5d8",
                "service_url": "https://ac.cnstrc.com",
                "version": "ciojs-client-2.54.0",
            }
        )

    def scrape(self, *args, **kwargs):
        page = 1
        while True:
            response = self.client.browse.get_browse_results(
                filter_name="group_id",
                filter_value="sneakers",
                parameters={
                    "sort_by": "relevance",
                    "sort_order": "descending",
                    "page": page,
                    "results_per_page": 200,
                },
            )

            if not response.get("response", {}).get("results"):
                break

            for result in response["response"]["results"]:
                data = result["data"]
                sneaker = self.json_to_sneaker(data)
                if sneaker:
                    create_or_update_sneaker(sneaker)

            page += 1

    def json_to_sneaker(self, data: dict) -> Sneaker | None:
        if not data.get("sku"):
            logfire.warning("No SKU found for GOAT product", data=data)
            return None

        # Parse release date (ignoring time component)
        release_date = None
        if data.get("release_date_time"):
            try:
                # Extract just the date part and set time to midnight
                date_str = data["release_date_time"].split()[0]
                release_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=ZoneInfo("America/New_York")
                )
            except ValueError as e:
                logfire.warning(
                    "Error parsing GOAT release date",
                    error=str(e),
                    release_date_time=data.get("release_date_time"),
                )

        sneaker = Sneaker(
            source=Platform.GOAT,
            brand=data.get("brand", "Unknown"),
            sku=data["sku"],
            name=data.get("value"),
            colorway=data.get("color"),
            audience=Audience.UNKNOWN,  # As per requirements
            release_date=release_date,
            retail_price=data.get("retail_price_cents"),
            description=None,  # GOAT doesn't provide descriptions
            meta={
                "id": data.get("id"),
                "slug": data.get("slug"),
                "category": data.get("category"),
                "product_type": data.get("product_type"),
                "variation_id": data.get("variation_id"),
                "box_condition": data.get("box_condition"),
                "product_condition": data.get("product_condition"),
                "lowest_price_cents": data.get("lowest_price_cents"),
                "instant_ship_lowest_price_cents": data.get(
                    "instant_ship_lowest_price_cents"
                ),
                "count_for_product_condition": data.get("count_for_product_condition"),
            },
        )

        # Add link
        if data.get("slug"):
            sneaker_link = Link(
                platform=Platform.GOAT,
                url=f"https://www.goat.com/sneakers/{data['slug']}",
            )
            sneaker.sneaker_links = [sneaker_link]

        # Add image
        if data.get("image_url"):
            sneaker_image = Image(
                platform=Platform.GOAT,
                position=0,
                url=data["image_url"],
            )
            sneaker.sneaker_images = [sneaker_image]

        # Add sizes (GOAT doesn't provide size information in browse results)
        # We'll need to fetch this separately if needed

        return sneaker


# Register the task with Celery
goat_scraping_task = register_scraping_task(GoatScrapingTask)
