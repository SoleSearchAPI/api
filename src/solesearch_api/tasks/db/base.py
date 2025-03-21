import logfire
from sqlmodel import Session, select

from solesearch_api.models.enums import Platform
from solesearch_api.models.sneaker import Sneaker
from solesearch_api.db import engine

logfire.configure(service_name="worker")


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
            sneaker: The sneaker object to create or update

        Returns:
            The created or updated sneaker object
        """
        # Check if sneaker already exists with eager loading of relationships
        statement = select(Sneaker).where(
            Sneaker.sku == sneaker.sku,
            Sneaker.brand == sneaker.brand,
        )
        existing_sneaker = session.exec(statement).first()

        if existing_sneaker:
            logfire.info(
                f"{sneaker.brand} SKU '{sneaker.sku}' found, updating existing sneaker",
                sneaker=sneaker,
                existing_sneaker=existing_sneaker,
            )

            # Update existing sneaker with new information
            existing_sneaker.name = choose_better_name(
                existing_sneaker.name, sneaker.name
            )
            existing_sneaker.parent_sku = (
                existing_sneaker.parent_sku or sneaker.parent_sku
            )
            existing_sneaker.audience = existing_sneaker.audience or sneaker.audience
            existing_sneaker.release_date = (
                existing_sneaker.release_date or sneaker.release_date
            )
            existing_sneaker.retail_price = max(
                existing_sneaker.retail_price, sneaker.retail_price
            )
            existing_sneaker.colorway = existing_sneaker.colorway or sneaker.colorway
            existing_sneaker.description = choose_better_description(
                existing_sneaker.description, sneaker.description
            )
            existing_sneaker.source = existing_sneaker.source or sneaker.source
            existing_sneaker.stockx_id = existing_sneaker.stockx_id or sneaker.stockx_id
            existing_sneaker.stadium_goods_id = (
                existing_sneaker.stadium_goods_id or sneaker.stadium_goods_id
            )

            # Add any new links
            existing_links = {
                link.platform: link.url for link in existing_sneaker.links
            }
            for new_link in sneaker.links:
                if existing_links.get(new_link.platform) != new_link.url:
                    logfire.warning(
                        f"{sneaker.brand} SKU '{sneaker.sku}' already has a link for {new_link.platform}",
                        sneaker_id=existing_sneaker.id,
                        sneaker_sku=sneaker.sku,
                        sneaker_brand=sneaker.brand,
                        existing_link=existing_links[new_link.platform],
                        new_link=new_link.url,
                    )
                else:
                    new_link.sneaker = existing_sneaker
                    existing_sneaker.links.append(new_link)

            # Add any new images
            existing_image_urls = {image.url for image in existing_sneaker.images}
            for image in sneaker.images:
                if image.url not in existing_image_urls:
                    image.sneaker = existing_sneaker
                    existing_sneaker.images.append(image)

            # Add any new sizes
            existing_size_values = {size.value for size in existing_sneaker.sizes}
            for size in sneaker.sizes:
                if size.value not in existing_size_values:
                    size.sneaker = existing_sneaker
                    existing_sneaker.sizes.append(size)

            session.add(existing_sneaker)
            result = existing_sneaker

        else:
            logfire.info(
                f"{sneaker.brand} SKU '{sneaker.sku}' not found, creating new sneaker",
                sneaker=sneaker,
            )
            session.add(sneaker)
            result = sneaker

        session.commit()
        logfire.info(
            "Committed session",
        )
        return result


def choose_better_name(existing_name: str, new_name: str) -> str:
    """
    Custom logic to determine the best sneaker name.
    Example: If one is more descriptive (longer), prefer it.
    """
    if not existing_name:
        return new_name
    if not new_name:
        return existing_name
    return new_name if len(new_name) > len(existing_name) else existing_name


def choose_better_description(existing_desc: str, new_desc: str) -> str:
    """
    Custom logic to determine the best description.
    Example: Prefer the longer description.
    """
    if not existing_desc:
        return new_desc
    if not new_desc:
        return existing_desc
    return new_desc if len(new_desc) > len(existing_desc) else existing_desc
