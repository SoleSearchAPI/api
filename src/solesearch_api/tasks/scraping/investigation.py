from typing import Callable

from solesearch_api.tasks.scraping.base import BaseScrapingTask
from solesearch_api.models.enums import Audience


class GenericInvestigationTask(BaseScrapingTask):
    def __init__(
        self,
        url: str,
        extractor: Callable[[str], dict],
        headers: dict = None,
    ):
        # Pass empty audience mapping since we're just investigating
        super().__init__(
            brand="Investigation",
            audience_mapping={},
            download_url=url,
            headers=headers or {},
            extractor=extractor,
            investigation=True,
        )
