import re

import logfire
from solesearch_api.models.enums import Audience, Platform
from solesearch_api.models.sneaker import Image, Link, Sneaker
from solesearch_api.tasks.db.base import create_or_update_sneaker
from solesearch_api.tasks.scraping.retail.adidas.base import AdidasScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task
from solesearch_api.utils.extractors import next_json_extractor


class AdidasYouthBaseScrapingTask(AdidasScrapingTask):
    def __init__(self, *args, **kwargs):
        super().__init__(
            extractor=next_json_extractor,
            *args,
            **kwargs,
        )

    def scrape(self, *args, **kwargs):
        json_data = self.get_json()

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
                variant_sneaker.links.append(variant_sneaker_link)

            sneakers.append(variant_sneaker)

        return sneakers


class AdidasBabyAndToddlerScrapingTask(AdidasYouthBaseScrapingTask):
    audience = Audience.TODDLER

    def __init__(self):
        super().__init__(
            download_url="https://www.adidas.com/us/kids-infant_toddler-shoes"
        )


class AdidasChildrenAndLittleKidsScrapingTask(AdidasYouthBaseScrapingTask):
    audience = Audience.PRESCHOOL

    def __init__(self):
        super().__init__(download_url="https://www.adidas.com/us/children-shoes")


class AdidasYouthAndBigKidsScrapingTask(AdidasYouthBaseScrapingTask):
    audience = Audience.GRADE_SCHOOL

    def __init__(self):
        super().__init__(download_url="https://www.adidas.com/us/youth-shoes")


adidas_baby_and_toddler_task = register_scraping_task(AdidasBabyAndToddlerScrapingTask)
adidas_children_and_little_kids_task = register_scraping_task(
    AdidasChildrenAndLittleKidsScrapingTask
)
adidas_youth_and_big_kids_task = register_scraping_task(
    AdidasYouthAndBigKidsScrapingTask
)
