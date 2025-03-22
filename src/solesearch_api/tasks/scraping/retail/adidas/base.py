import re
import logfire
from solesearch_api.models.enums import Audience, Platform
from solesearch_api.models.sneaker import Image, Link, Sneaker
from solesearch_api.tasks.db.base import create_or_update_sneaker
from solesearch_api.tasks.scraping.base import BaseScrapingTask
from solesearch_api.utils.extractors import next_json_extractor
from solesearch_api.utils.json import get_from_json


class AdidasScrapingTask(BaseScrapingTask):
    def __init__(self, *args, **kwargs):
        super().__init__(
            brand="Adidas",
            audience_mapping={
                "M": Audience.MEN,
                "W": Audience.WOMEN,
                "K": Audience.GRADE_SCHOOL,
                "U": Audience.UNISEX,
            },
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "Referer": "https://www.adidas.com/us/shoes",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            },
            *args,
            **kwargs,
        )


class AdidasPaginatedScrapingTask(AdidasScrapingTask):
    def __init__(self, *args, **kwargs):
        super().__init__(
            extractor=next_json_extractor,
            *args,
            **kwargs,
        )

    def scrape(self, *args, **kwargs):
        if kwargs.get("download_url"):
            self.download_url = kwargs["download_url"]

        # Extract page number from URL for prefix
        page_prefix = "page_start_0"  # Default to first page
        if "start=" in self.download_url:
            start_param = self.download_url.split("start=")[1].split("&")[0]
            page_prefix = f"page_start_{start_param}"
        self.prefix = page_prefix

        json_data = self.get_json()

        next_page_url = self.get_next_page_url(json_data)
        if next_page_url and next_page_url != self.download_url:
            from solesearch_api.tasks import app

            task_name = f"solesearch_api.tasks.scraping.{self.__class__.__name__}"
            task = app.tasks[task_name]
            task.delay(download_url=next_page_url)

        # Process each product in the products array
        for product in json_data.get("products", []):
            sneakers = self.json_to_sneakers(product)
            for sneaker in sneakers:
                create_or_update_sneaker(sneaker)

    def json_to_sneakers(self, data: dict) -> list[Sneaker] | None:
        sneakers = []
        sku = data.get("id", "").strip()
        if not sku:
            logfire.warning(f"No SKU found for {self.brand} product: {data}")
            return None

        price = data.get("priceData", {}).get("price")
        if price is not None:
            price = price * 100

        sneaker = Sneaker(
            source=Platform.RETAIL,
            brand=self.brand,
            name=data.get("title"),
            sku=sku,
            parent_sku=data.get("modelNumber"),
            audience=self.audience,
            retail_price=price,
        )

        sneaker_slug = data.get("url", "").strip()
        if sneaker_slug:
            sneaker_link = Link(
                url=f"https://www.adidas.com{sneaker_slug}",
                platform=Platform.RETAIL,
            )
            sneaker.sneaker_links.append(sneaker_link)

        for index, image in enumerate(data.get("images", [])):
            image_url = re.sub(r"images/[^/]+/", "images/", image.get("src"))
            position = image.get("metadata", {}).get("sortOrder")
            position = int(position) if position else index
            image = Image(
                platform=Platform.RETAIL,
                position=position,
                url=image_url,
            )
            sneaker.sneaker_images.append(image)

        sneakers.append(sneaker)

        for variant_sku in data.get("colourVariations", []):
            variant_sku = variant_sku.strip()
            if not variant_sku:
                continue

            variant_sneaker = Sneaker(
                source=Platform.RETAIL,
                brand=self.brand,
                name=data.get("title"),
                sku=variant_sku,
                parent_sku=data.get("modelNumber"),
                audience=self.audience,
                retail_price=price,
            )

            variant_sneaker_slug = data.get("url", "").strip()
            if variant_sneaker_slug:
                variant_sneaker_slug = variant_sneaker_slug.split("/")[:-1] + [
                    f"{variant_sku}.html"
                ]
                variant_sneaker_slug = "/".join(variant_sneaker_slug)
                if not variant_sneaker_slug.startswith("/"):
                    variant_sneaker_slug = f"/{variant_sneaker_slug}"
                variant_sneaker_link = Link(
                    url=f"https://www.adidas.com{variant_sneaker_slug}",
                    platform=Platform.RETAIL,
                )
                variant_sneaker.sneaker_links.append(variant_sneaker_link)

            sneakers.append(variant_sneaker)

        return sneakers

    def get_next_page_url(self, json_data: dict) -> str | None:
        products_per_page = get_from_json(json_data, "info.viewSize")
        products_count = get_from_json(json_data, "info.count")
        start_at_product = get_from_json(json_data, "info.startIndex")
        next_start_at_product = start_at_product + products_per_page
        if next_start_at_product < products_count:
            next_page_url = (
                f"{self.download_url.split('?')[0]}?start={next_start_at_product}"
            )
            return next_page_url
        return None
