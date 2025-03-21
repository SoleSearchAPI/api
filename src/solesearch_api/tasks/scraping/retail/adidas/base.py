from solesearch_api.models.enums import Audience
from solesearch_api.tasks.scraping.base import BaseScrapingTask


class AdidasScrapingTask(BaseScrapingTask):
    def __init__(self, *args, **kwargs):
        super().__init__(
            brand="Adidas",
            audience_mapping={
                "M": Audience.MEN,
                "W": Audience.WOMEN,
                "K": Audience.GRADE_SCHOOL,
                "U": Audience.UNISEX,
            },
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Brave";v="134"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
                "upgrade-insecure-requests": "1",
                "Referer": "https://www.adidas.com/us/shoes",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            },
            *args,
            **kwargs,
        )
