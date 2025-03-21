from solesearch_api.tasks.db.base import create_or_update_sneaker
from solesearch_api.tasks.scraping.retail.adidas.base import AdidasScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task
from solesearch_api.utils.extractors import (
    react_query_data_extractor,
)


class AdidasPDPScrapingTask(AdidasScrapingTask):
    def __init__(self, *args, **kwargs):
        super().__init__(
            extractor=react_query_data_extractor,
            *args,
            **kwargs,
        )

    def run(self, slug: str, *args, **kwargs):
        self.download_url = f"https://www.adidas.com/us/{slug}"
        super().run(*args, **kwargs)

    def scrape(self, *args, **kwargs):
        json_data = self.get_json()
        sneaker = self.json_to_sneaker(json_data)
        if sneaker:
            create_or_update_sneaker(sneaker)


# Replace the class-based task registration with the decorator-based approach
adidas_pdp_task = register_scraping_task(AdidasPDPScrapingTask)
