from datetime import datetime
from zoneinfo import ZoneInfo

import logfire
from constructor_io.constructor_io import ConstructorIO

from solesearch_api.models.enums import Audience, Platform
from solesearch_api.models.sneaker import Image, Link, Sneaker, SneakerSize
from solesearch_api.tasks.db.base import create_or_update_sneaker
from solesearch_api.tasks.scraping.base import BaseScrapingTask
from solesearch_api.tasks.scraping.task_registry import register_scraping_task


class GoatRecentlyAddedByBrandScrapingTask(BaseScrapingTask):
    def __init__(self):
        super().__init__(
            brand="GOAT",
            audience_mapping={},
            download_url=None,
        )
        self.client = ConstructorIO(
            {
                "api_key": "key_XT7bjdbvjgECO5d8",
                "service_url": "https://ac.cnstrc.com",
                "version": "ciojs-client-2.54.0",
            }
        )

    def scrape(self, *args, **kwargs):
        from solesearch_api.tasks import app

        browse_brand_index_task = app.tasks[
            "solesearch_api.tasks.scraping.GoatBrandIndexScrapingTask"
        ]

        brand_facets_response = self.client.browse.get_browse_facet_options(
            facet_name="brand",
            parameters={
                "fmt_options": {
                    "show_hidden_facets": True,
                    "show_protected_facets": True,
                }
            },
        )

        brand_options = (
            brand_facets_response.get("response").get("facets")[0].get("options")
        )

        for brand in brand_options:
            brand_id = brand.get("value")
            brand_name = brand.get("display_name")

            browse_brand_index_task.delay(brand=brand_name, brand_id=brand_id)


goat_recently_added_by_brand_task = register_scraping_task(
    GoatRecentlyAddedByBrandScrapingTask
)
