from solesearch_api.models.enums import Audience
from solesearch_api.tasks.scraping.retail.adidas.base import AdidasPaginatedScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task


class AdidasMensSneakersScrapingTask(AdidasPaginatedScrapingTask):
    audience = Audience.MEN

    def __init__(self):
        super().__init__(download_url="https://www.adidas.com/us/men-shoes")


adidas_mens_sneakers_task = register_scraping_task(AdidasMensSneakersScrapingTask)
