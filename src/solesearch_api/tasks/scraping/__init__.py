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
from solesearch_api.tasks.scraping.retail.adidas.mens_sneakers import (
    adidas_mens_sneakers_task,
)
from solesearch_api.tasks.scraping.retail.adidas.womens_sneakers import (
    adidas_womens_sneakers_task,
)

# Nike Tasks
from solesearch_api.tasks.scraping.retail.nike.new_releases import (
    nike_new_releases_task,
)
from solesearch_api.tasks.scraping.retail.nike.in_stock import (
    nike_in_stock_scraping_task,
)

# Goat Tasks
from solesearch_api.tasks.scraping.aftermarket.goat.browse_brand_index import (
    goat_brand_index_task,
)
from solesearch_api.tasks.scraping.aftermarket.goat.recently_added_by_brand import (
    goat_recently_added_by_brand_task,
)
