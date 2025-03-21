from datetime import datetime, timezone
import logfire
import re

from solesearch_api.models.enums import Platform
from solesearch_api.models.sneaker import Image, Link, Sneaker
from solesearch_api.tasks.db.base import create_or_update_sneaker
from solesearch_api.tasks.scraping.retail.adidas.base import AdidasScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task
from solesearch_api.utils.extractors import next_json_extractor


class AdidasNewReleasesScrapingTask(AdidasScrapingTask):
    def __init__(self, *args, **kwargs):
        super().__init__(
            download_url="https://www.adidas.com/us/release-dates",
            extractor=next_json_extractor,
            *args,
            **kwargs,
        )

    def scrape(self, *args, **kwargs):
        json_data = self.get_json()

        # Process each product in the plcSSRData
        for product in json_data.get("plcSSRData", []):
            sneaker = self.json_to_sneaker(product)
            if sneaker:
                create_or_update_sneaker(sneaker)

    def json_to_sneaker(self, data: dict) -> Sneaker | None:
        sku = data.get("id", "").strip()
        if not sku:
            logfire.warning(f"No SKU found for {self.brand} product: {data}")
            return None

        release_date = data.get("preview_to", "").strip()
        if release_date:
            release_date = datetime.fromisoformat(release_date.rstrip("Z"))
            release_date = release_date.replace(tzinfo=timezone.utc)
        else:
            release_date = None

        price = data.get("price")
        if price is not None:
            price = price * 100

        sneaker = Sneaker(
            source=Platform.RETAIL,
            brand=self.brand,
            name=data.get("name"),
            sku=sku,
            parent_sku=data.get("model_number"),
            audience=self.guess_audience(data.get("attribute_list", {}).get("gender")),
            release_date=release_date,
            retail_price=price,
        )

        sneaker_slug = data.get("productLink", "").strip()
        if sneaker_slug:
            sneaker_link = Link(
                url=f"https://www.adidas.com{sneaker_slug}",
                platform=Platform.RETAIL,
            )
            sneaker.links.append(sneaker_link)

        for index, image in enumerate(data.get("images", [])):
            image_url = re.sub(r"images/[^/]+/", "images/", image.get("src"))
            position = image.get("metadata", {}).get("sortOrder")
            position = int(position) if position else index
            image = Image(
                platform=Platform.RETAIL,
                position=position,
                url=image_url,
            )
            sneaker.images.append(image)

        return sneaker


# Replace the class-based task registration with the decorator-based approach
adidas_new_releases_task = register_scraping_task(AdidasNewReleasesScrapingTask)
