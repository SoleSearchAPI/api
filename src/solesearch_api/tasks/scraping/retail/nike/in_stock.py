from solesearch_api.models.enums import Audience
from solesearch_api.tasks.scraping.base import BaseScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task
from solesearch_api.utils.extractors import next_json_extractor


class NikeInStockScrapingTask(BaseScrapingTask):
    def __init__(self):
        super().__init__(
            brand="Nike",
            download_url="https://www.nike.com/launch?s=in-stock",
            audience_mapping={
                "M": Audience.MEN,
                "W": Audience.WOMEN,
            },
            extractor=next_json_extractor,
        )

    def scrape(self, session, *args, **kwargs):
        json_data = self.get_json()
        return json_data


nike_in_stock_scraping_task = register_scraping_task(NikeInStockScrapingTask)
