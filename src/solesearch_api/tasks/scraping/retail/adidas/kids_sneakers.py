from solesearch_api.models.enums import Audience
from solesearch_api.tasks.scraping.retail.adidas.base import AdidasPaginatedScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task


class AdidasBabyAndToddlerScrapingTask(AdidasPaginatedScrapingTask):
    audience = Audience.TODDLER

    def __init__(self):
        super().__init__(
            download_url="https://www.adidas.com/us/kids-infant_toddler-shoes"
        )


class AdidasChildrenAndLittleKidsScrapingTask(AdidasPaginatedScrapingTask):
    audience = Audience.PRESCHOOL

    def __init__(self):
        super().__init__(download_url="https://www.adidas.com/us/children-shoes")


class AdidasYouthAndBigKidsScrapingTask(AdidasPaginatedScrapingTask):
    audience = Audience.GRADE_SCHOOL

    def __init__(self):
        super().__init__(download_url="https://www.adidas.com/us/youth-shoes")


adidas_baby_and_toddler_task = register_scraping_task(AdidasBabyAndToddlerScrapingTask)
adidas_children_and_little_kids_task = register_scraping_task(
    AdidasChildrenAndLittleKidsScrapingTask
)
adidas_youth_and_big_kids_task = register_scraping_task(
    AdidasYouthAndBigKidsScrapingTask
)
