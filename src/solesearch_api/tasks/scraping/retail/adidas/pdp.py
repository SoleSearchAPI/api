import logging

from solesearch_api.tasks.scraping.retail.adidas.base import AdidasScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task
from solesearch_api.utils.extractors import (
    react_query_data_extractor,
)

logger = logging.getLogger(__name__)


class AdidasPDPScrapingTask(AdidasScrapingTask):
    # This is the name that Celery will look for
    name = "solesearch_api.tasks.scraping.retail.adidas.pdp"

    def __init__(self, *args, **kwargs):
        super().__init__(
            extractor=react_query_data_extractor,
            *args,
            **kwargs,
        )

    def run(self, slug: str, *args, **kwargs):
        self.download_url = f"https://www.adidas.com/us/{slug}"
        super().run(*args, **kwargs)

    def scrape(self, session, *args, **kwargs):
        json_data = self.get_json()
        sneaker = self.json_to_sneaker(json_data)
        if sneaker:
            session.add(sneaker)


# Replace the class-based task registration with the decorator-based approach
adidas_pdp_task = register_scraping_task(AdidasPDPScrapingTask)
