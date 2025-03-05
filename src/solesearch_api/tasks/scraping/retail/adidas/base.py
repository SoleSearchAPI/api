from solesearch_api.models.enums import Audience
from solesearch_api.tasks.scraping.base import BaseScrapingTask


class AdidasScrapingTask(BaseScrapingTask):
    def __init__(self, *args, **kwargs):
        super().__init__(
            brand="Adidas",
            audience_mapping={
                "M": Audience.MEN,
                "W": Audience.WOMEN,
                "K": Audience.YOUTH,
                "U": Audience.UNISEX,
            },
            headers={
                "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "DNT": "1",
                "Origin": "https://www.adidas.com",
                "Host": "www.adidas.com",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Cookie": "geo_country=US; geo_state=CA",
            },
            *args,
            **kwargs,
        )
