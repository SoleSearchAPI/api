from ingest.models.task import IngestInterface
from ingest.utils.sessions import stockx_session


class StockXOfficialApiIngest(IngestInterface):
    def __init__(self):
        self.base_url = "https://api.stockx.com/v2"

    def get_single_product(self, product_id: str) -> dict:
        return stockx_session.get(
            f"{self.base_url}/catalog/products/{product_id.strip()}"
        ).json()

    def search_products(self, query: str) -> dict:
        return stockx_session.get(
            f"{self.base_url}/search?query={query.strip()}"
        ).json()

    def get_single_product_variant(self, product_id: str, variant_id: str) -> dict:
        return stockx_session.get(
            f"{self.base_url}/catalog/products/{product_id.strip()}/product/{variant_id.strip()}"
        ).json()

    def get_multiple_products(self, query: str) -> dict:
        return

    def execute(self) -> None:
        pass
