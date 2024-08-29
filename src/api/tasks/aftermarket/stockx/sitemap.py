import logging
import os
import urllib.parse
from os import path

from bs4 import BeautifulSoup
from core.models.details import SiteMapLink

from ingest.config import DATA_DIR
from ingest.db.mutations import upsert_sitemap_links
from ingest.models.task import IngestInterface
from ingest.utils.helpers import create_and_write_file
from ingest.utils.sessions import session


class SitemapIngest(IngestInterface):
    """
    A class for ingesting sitemaps.

    Parameters:
    - url (str): The URL of the sitemap "root", can recursively ingest from it if it contains sub-sitemaps.
    - name (str): The name of the sitemap.
    - mongo_collection (str): The name of the MongoDB collection to store the sitemap links in.
    - filters (List[Callable[[str], bool]]): A list of functions that take a URL and return a boolean, when a function returns True the link is excluded.
    """

    def __init__(self) -> None:
        self.url = "https://stockx.com/sitemap/sitemap-index.xml"
        self.filters = ([lambda x: x.startswith("https://stockx.com/search?s=")],)
        self.name = ("StockX",)
        self.mongo_collection = ("stockx-links",)
        self.API_KEY = os.environ.get("SCRAPFLY_API_KEY")
        if not self.API_KEY:
            raise EnvironmentError(
                "Please set the SCRAPFLY_API_KEY environment variable."
            )
        self.session = session
        self.logger = logging.getLogger(__name__)

    def recursiveIngest(self, url: str) -> None:
        self.logger.info(f"Ingesting {url}")
        try:
            params = {
                "url": url,
                "tags": "player,project:default",
                "country": "us",
                "asp": "true",
                "render_js": "true",
                "key": SCRAPFLY_API_KEY,
            }
            xmlText = self.session.get(
                f"https://api.scrapfly.io/scrape?{urllib.parse.urlencode(params)}",
            ).json()["result"]["content"]
            create_and_write_file(
                path.join(DATA_DIR, "xml", url.split("/")[-1]),
                xmlText,
            )
            xml_document = BeautifulSoup(xmlText, "lxml")
            if xml_document.find(name="sitemapindex"):
                [self.recursiveIngest(l.text) for l in xml_document.findAll(name="loc")]
            elif xml_document.find(name="urlset"):
                productPages = [
                    SiteMapLink(url=linkAddress, scraped=False, lastScraped=None)
                    for linkAddress in [
                        locElement.text
                        for locElement in xml_document.findAll(name="loc")
                    ]
                    if not any([f(linkAddress) for f in self.filters])
                ]
                upsert_sitemap_links(productPages, self.mongo_collection)
            else:
                raise Exception("Unknown XML/sitemap structure")
        except Exception as e:
            self.logger.error(e)

    def execute(self) -> None:
        self.recursiveIngest(self.url)
