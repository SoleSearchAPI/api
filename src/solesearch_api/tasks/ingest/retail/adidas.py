from datetime import datetime, timezone
from typing import Any

from solesearch_api.tasks.ingest import get_json, next_json_extractor
from solesearch_api.tasks.ingest.task import IngestTask
from solesearch_api.tasks import app
from solesearch_api.models.sneaker import Sneaker, Image, Link, SneakerSize, Price
from solesearch_api.models.enums import Platform, Audience


class AdidasIngest(IngestTask):
    def map_audience(self, gender: str) -> Audience:
        if gender == "M":
            return Audience.MEN
        elif gender == "W":
            return Audience.WOMEN
        elif gender == "K":
            return Audience.YOUTH
        elif gender == "U":
            return Audience.UNISEX
        return Audience.UNKNOWN

    def process_product(self, session, product: dict[str, Any]) -> None:
        # Check if sneaker already exists
        sneaker = (
            session.query(Sneaker)
            .filter(Sneaker.brand == "Adidas", Sneaker.sku == product["id"])
            .first()
        )

        # Extract colorway from altText
        colorway = product.get("altText")

        if not sneaker:
            sneaker = Sneaker(
                brand="Adidas",
                sku=product["id"],
                name=product["name"],
                colorway=colorway,
                audience=self.map_audience(
                    product.get("attribute_list", {}).get("gender", "U")
                ),
                source=Platform.RETAIL,
            )
            session.add(sneaker)
        else:
            # Update existing sneaker's colorway if it's empty or shorter
            if not sneaker.colorway or (
                colorway and len(colorway) > len(sneaker.colorway)
            ):
                sneaker.colorway = colorway

        # Update release date if available
        if preview_to := product.get("attribute_list", {}).get("preview_to"):
            sneaker.release_date = datetime.fromisoformat(
                preview_to.replace("Z", "+00:00")
            )

        # Update or create images, now handling all image types
        existing_images = {img.url: img for img in sneaker.images}

        # Process main image
        if main_image := product.get("image"):
            if main_image["src"] not in existing_images:
                image = Image(
                    platform=Platform.RETAIL,
                    position=0,  # Main image should be first
                    url=main_image["src"],
                    sneaker=sneaker,
                )
                session.add(image)

        # Process second image
        if second_image := product.get("secondImage"):
            if second_image["src"] not in existing_images:
                image = Image(
                    platform=Platform.RETAIL,
                    position=1,  # Second image
                    url=second_image["src"],
                    sneaker=sneaker,
                )
                session.add(image)

        # Process additional images
        for idx, image_data in enumerate(product.get("images", []), start=2):
            if not isinstance(image_data, dict) or "src" not in image_data:
                continue

            image_url = image_data["src"]
            if image_url not in existing_images:
                image = Image(
                    platform=Platform.RETAIL,
                    position=idx,
                    url=image_url,
                    sneaker=sneaker,
                )
                session.add(image)

        # Update or create product link
        product_link = f"https://www.adidas.com{product['productLink']}"
        existing_link = (
            session.query(Link)
            .filter(Link.sneaker_id == sneaker.id, Link.platform == Platform.RETAIL)
            .first()
        )

        if not existing_link:
            link = Link(platform=Platform.RETAIL, url=product_link, sneaker=sneaker)
            session.add(link)
        elif existing_link.url != product_link:
            existing_link.url = product_link

        # Create or update sneaker size with retail price
        if price := product.get("price"):
            size = (
                session.query(SneakerSize)
                .filter(
                    SneakerSize.sneaker_id == sneaker.id,
                    SneakerSize.value == 0,  # Use 0 for retail price base size
                )
                .first()
            )

            if not size:
                size = SneakerSize(
                    value=0, sneaker=sneaker  # Use 0 for retail price base size
                )
                session.add(size)

            # Check if price already exists
            existing_price = (
                session.query(Price)
                .filter(
                    Price.sneaker_size_id == size.id, Price.platform == Platform.RETAIL
                )
                .first()
            )

            price_cents = int(float(price) * 100)  # Convert to cents

            if not existing_price:
                price_obj = Price(
                    platform=Platform.RETAIL,
                    amount=price_cents,
                    observed_at=datetime.now(timezone.utc),
                    sneaker_size=size,
                )
                session.add(price_obj)
            elif existing_price.amount != price_cents:
                existing_price.amount = price_cents
                existing_price.observed_at = datetime.now(timezone.utc)

    def ingest(self, session, *args, **kwargs):
        brand = "Adidas"
        download_url = "https://www.adidas.com/us/release-dates"

        # Additional headers specific to Adidas
        adidas_headers = {
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "DNT": "1",
            "Origin": "https://www.adidas.com",
            "Host": "www.adidas.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "geo_country=US; geo_state=CA",  # Simulate US location
        }

        json_data = get_json(
            brand,
            download_url,
            headers=adidas_headers,
            extractor=next_json_extractor,
        )

        # Process each product in the plcSSRData
        for product in json_data.get("plcSSRData", []):
            self.process_product(session, product)

        return json_data


@app.task(name="adidas_ingest", bind=True, max_retries=5)
def adidas_ingest(self):
    try:
        task = AdidasIngest()
        return task.run()
    except Exception as exc:
        # Retry with exponential backoff
        retry_delay = min(2**self.request.retries, 60)  # Cap at 60 seconds
        self.retry(exc=exc, countdown=retry_delay)
