import logging

from core.models.shoes import Sneaker

logger = logging.getLogger(__name__)


async def fix_duplicate_skus():
    async for dupe in Sneaker.aggregate(
        [
            {"$group": {"_id": "$sku", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}},
            {"$project": {"sku": "$_id", "_id": 0}},
        ]
    ):
        await merge_duplicate_skus(dupe["sku"])


async def merge_duplicate_skus(sku: str):
    """Merge duplicate skus in the database."""
    dupes = await Sneaker.find(Sneaker.sku == sku).sort(-Sneaker.dateAdded).to_list()
    merged = dupes.pop()
    for sneaker in dupes:
        for key, value in dict(sneaker).items():
            # Skip merging these fields
            if key in ["id", "sku", "dateAdded", "lastScraped"]:
                continue
            if key in ["stockId", "stadiumGoodsId"]:
                if not value:
                    continue
                if not getattr(merged, key):
                    setattr(merged, key, value)
                    continue
                if value != getattr(merged, key):
                    logger.warning(
                        f"Mismatched {key} for {merged.sku}: {value} != {getattr(merged, key)}"
                    )
            # Keep the longest value all of these fields
            if key in ["colorway", "description", "name"]:
                if len(value) > len(getattr(merged, key)):
                    setattr(merged, key, value)
            # Merge any available sizes
            if key == "sizes" and value is not None:
                setattr(merged, key, list(set(merged.sizes + value)))
            # Prefer images from certain sources, keep the longest list of angles
            if key == "images" and len(sneaker.images.original) > 0:
                if not merged.images:
                    merged.images = sneaker.images
                else:
                    if not merged.images.original:
                        merged.images.original = sneaker.images.original
                    if merged.images.alternateAngles is None:
                        merged.images.alternateAngles = sneaker.images.alternateAngles
                    image_preference_order = [
                        "static.nike.com",
                        "images.puma.com",
                        "images.stockx.com",
                        "image.goat.com",
                    ]
                    for preference in image_preference_order:
                        if preference in sneaker.images.original:
                            merged.images.original = sneaker.images.original
                            break
                    if len(sneaker.images.alternateAngles) > len(
                        merged.images.alternateAngles
                    ):
                        merged.images.alternateAngles = sneaker.images.alternateAngles
            # Merge any available links
            if key == "links" and value is not None:
                for link_source, link in dict(value).items():
                    if not getattr(merged.links, link_source):
                        setattr(merged.links, link_source, link)
            # Merge any prices, prefer the highest
            if key == "prices" and value is not None:
                for price_source, price in dict(value).items():
                    if not price:
                        continue
                    if not getattr(merged.prices, price_source):
                        setattr(merged.prices, price_source, price)
                    elif price > getattr(merged.prices, price_source):
                        setattr(merged.prices, price_source, price)
            # For any other fields, prefer any non-null value
            if not getattr(merged, key):
                setattr(merged, key, value)
        await sneaker.delete()
    await merged.save()


async def fix_incorrectly_mapped_stockx_links():
    """Fix incorrectly mapped stockx links in the database."""
    # Check if the slug equals the name lowercased and spaces replaced with hypens
    async for dupe in Sneaker.aggregate(
        [
            {"$group": {"_id": "$sku", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}},
            {"$project": {"sku": "$_id", "_id": 0}},
        ]
    ):
        async for sneaker in Sneaker.find(Sneaker.sku == dupe["sku"]):
            if (
                sneaker.name.lower().replace(" ", "-")
                == sneaker.links.stockx.split("/")[-1]
            ):

                await sneaker.save()
