from solesearch_api.models.enums import Audience
from solesearch_api.tasks.scraping.retail.adidas.base import AdidasPaginatedScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task


class AdidasWomensSneakersScrapingTask(AdidasPaginatedScrapingTask):
    audience = Audience.WOMEN

    def __init__(self):
        super().__init__(download_url="https://www.adidas.com/us/women-shoes")


adidas_womens_sneakers_task = register_scraping_task(AdidasWomensSneakersScrapingTask)
