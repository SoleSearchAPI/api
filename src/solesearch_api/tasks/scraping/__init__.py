# Import all tasks to ensure they are registered with Celery
from solesearch_api.tasks.scraping.retail.adidas.new_releases import (
    adidas_new_releases_task,
)
from solesearch_api.tasks.scraping.retail.adidas.pdp import adidas_pdp_task
from solesearch_api.tasks.scraping.retail.nike import nike_scraping_task
