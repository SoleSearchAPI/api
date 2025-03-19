# Import all tasks to ensure they are registered with Celery

# Adidas Tasks
from solesearch_api.tasks.scraping.retail.adidas.new_releases import (
    adidas_new_releases_task,
)
from solesearch_api.tasks.scraping.retail.adidas.kids_sneakers import (
    adidas_baby_and_toddler_task,
    adidas_children_and_little_kids_task,
    adidas_youth_and_big_kids_task,
)

# Nike Tasks
from solesearch_api.tasks.scraping.retail.nike.new_releases import (
    nike_new_releases_task,
)
from solesearch_api.tasks.scraping.retail.nike.in_stock import (
    nike_in_stock_scraping_task,
)
