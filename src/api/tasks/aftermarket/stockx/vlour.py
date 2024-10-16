import logging
from datetime import UTC, datetime

from beanie import BulkWriter
from beanie.odm.operators.find.logical import And
from beanie.odm.operators.update.general import Set
from requests import Session

from core.models.details import Images, Links, SiteMapLink
from core.models.shoes import Sneaker
from ingest.models.task import IngestInterface
from ingest.utils.helpers import should_skip_link, try_guess_audience

logger = logging.getLogger(__name__)


class StockXVlourIngest(IngestInterface):
    def __init__(self):
        self.base_url = "https://api.stockx.vlour.me"
        self.session = Session()
        self.reset_operations()

    def get_by_slug(self, slug: str) -> dict:
        res = self.session.get(f"{self.base_url}/search", params={"query": slug})
        if res.status_code != 200:
            raise ConnectionRefusedError(
                f"Failed to get product for slug: {slug}, status_code: {res.status_code}"
            )
        json = res.json().get("hits", [])
        if len(json) == 0:
            return {}
        return json[0]

    def get_by_sku(self, sku: str) -> dict:
        return self.session.get(
            f"{self.base_url}/search", params={"query": sku}
        ).json()["hits"][0]

    def search(self, query: str, page: int = 1) -> dict:
        return self.session.get(
            f"{self.base_url}/search", params={"query": query, "page": page}
        ).json()["hits"]

    def get_by_productid(self, stockx_product_id: str) -> dict:
        return self.session.get(f"{self.base_url}/product/{stockx_product_id}").json()

    def get_count(self) -> int:
        return self.session.get(f"{self.base_url}/stats").json()["count"]

    async def error_correct(self) -> None:
        pipeline = [
            {"$match": {"scraped": True, "ignored": False, "error": None}},
            {
                "$lookup": {
                    "from": "sneakers",
                    "let": {"url": "$url"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$links.stockx", "$$url"]}}}
                    ],
                    "as": "matched_links",
                }
            },
            {"$match": {"matched_links": []}},
            {
                "$project": {
                    "url": 1,
                    "ignored": 1,
                    "scraped": 1,
                    "lastSeenOnSitemap": 1,
                }
            },
        ]
        results = await SiteMapLink.aggregate(
            pipeline, projection_model=SiteMapLink
        ).to_list()
        for document in results:
            document.ignored = None
            document.scraped = False
            await document.save()
        print("Done!")

    async def write_all(self) -> None:
        if self.sneakers_operations:
            print(f"Inserting {len(self.sneakers_operations)} sneakers...")
            await Sneaker.insert_many(self.sneakers_operations)
        if self.total_operations > 0:
            print(f"Updating {self.total_operations} links...")
            await self.bulk_writer.commit()
        self.reset_operations()

    def reset_operations(self) -> None:
        self.sneakers_operations = []
        self.bulk_writer = BulkWriter()
        self.total_operations = 0

    async def execute(self) -> None:
        await self.error_correct()
        self.reset_operations()
        async for link in SiteMapLink.find(
            And(
                SiteMapLink.scraped is not True,
                not SiteMapLink.error,
            )
        ):
            slug = link.url.split("/")[-1].strip()
            self.total_operations += 1
            if should_skip_link(link):
                link.ignored = True
            else:
                print(f"Checking StockX sitemap link: {link.url}")
                stockx_product = self.get_by_slug(slug)
                if not stockx_product:
                    print(f"Failed to get product for slug: {slug}")
                    await link.update(
                        Set({SiteMapLink.error: True}), bulk_writer=self.bulk_writer
                    )
                    continue
                link.ignored = "sneakers" not in stockx_product["labels"]
            link.scraped = True
            try:
                if not link.ignored:
                    if stockx_product["labels"][-1] == "":
                        raise Exception(f"SKU is empty: {link.url}")
                    self.sneakers_operations.append(
                        Sneaker(
                            stockxId=stockx_product["id"],
                            name=stockx_product["title"],
                            sku=stockx_product["labels"][-1],
                            description=stockx_product["description"],
                            brand=stockx_product["brand"],
                            audience=try_guess_audience(stockx_product["gender"]),
                            images=Images(original=stockx_product["image"]),
                            links=Links(stockx=link.url),
                            dateAdded=datetime.now(UTC),
                            lastScraped=datetime.now(UTC),
                        )
                    )
            except Exception as e:
                print(f"Error: {e}")
                link.error = True
            finally:
                await link.update(
                    Set(
                        {
                            SiteMapLink.error: link.error,
                            SiteMapLink.ignored: link.ignored,
                            SiteMapLink.scraped: link.scraped,
                        }
                    ),
                    bulk_writer=self.bulk_writer,
                )
                if self.total_operations >= 1000:
                    await self.write_all()
        await self.write_all()
        print("Finished checking StockX sitemap links!")
