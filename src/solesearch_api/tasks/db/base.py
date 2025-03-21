import logfire
from sqlmodel import Session, select

from solesearch_api.models.sneaker import Sneaker
from solesearch_api.tasks import app
from solesearch_api.db import engine

logfire.configure(service_name="worker")


@app.task(name="create_or_update_sneaker")
def create_or_update_sneaker(
    sneaker: Sneaker,
):
    with Session(engine) as session:
        """
        Create a new sneaker or update an existing one with the same SKU and brand.

        This function centralizes the logic for handling sneaker uniqueness based on SKU and brand.
        It will update all fields of an existing sneaker with the new data, and handle relationships
        like links, images, sizes, and prices.

        Args:
            - sneaker: The sneaker object to create or update

        Returns:
            - The created or updated sneaker object
        """
        # Check if sneaker already exists with eager loading of relationships
        statement = select(Sneaker).where(
            Sneaker.sku == sneaker.sku,
            Sneaker.brand == sneaker.brand,
        )
        existing_sneaker = session.exec(statement).first()
        if existing_sneaker is None:
            logfire.info(
                "Sneaker not found, creating new sneaker",
                sneaker=sneaker,
            )
            # Just add the new sneaker if it doesn't exist already
            result = sneaker
        else:
            logfire.info(
                "Sneaker found, updating existing sneaker",
                sneaker=sneaker,
                existing_sneaker=existing_sneaker,
            )
            # Update existing sneaker with new information
            existing_sneaker.name = sneaker.name or existing_sneaker.name
            existing_sneaker.parent_sku = (
                sneaker.parent_sku or existing_sneaker.parent_sku
            )
            existing_sneaker.audience = sneaker.audience or existing_sneaker.audience
            existing_sneaker.release_date = (
                sneaker.release_date or existing_sneaker.release_date
            )
            existing_sneaker.retail_price = (
                sneaker.retail_price or existing_sneaker.retail_price
            )
            existing_sneaker.colorway = sneaker.colorway or existing_sneaker.colorway
            existing_sneaker.description = (
                sneaker.description or existing_sneaker.description
            )
            existing_sneaker.source = existing_sneaker.source or sneaker.source
            existing_sneaker.stockx_id = existing_sneaker.stockx_id or sneaker.stockx_id
            existing_sneaker.stadium_goods_id = (
                existing_sneaker.stadium_goods_id or sneaker.stadium_goods_id
            )

            # Add any new links
            existing_link_urls = {link.url for link in existing_sneaker.links}
            for link in sneaker.links:
                if link.url not in existing_link_urls:
                    existing_sneaker.links.append(link)

            # Add any new images
            existing_image_urls = {image.url for image in existing_sneaker.images}
            for image in sneaker.images:
                if image.url not in existing_image_urls:
                    session.add(image)
                    existing_sneaker.images.append(image)

            # Add any new sizes
            existing_size_values = {size.value for size in existing_sneaker.sizes}
            for size in sneaker.sizes:
                if size.value not in existing_size_values:
                    session.add(size)
                    existing_sneaker.sizes.append(size)
            result = existing_sneaker
        session.add(result)
        session.commit()
        return result
