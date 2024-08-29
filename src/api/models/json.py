import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime

import requests

from ingest.config import ARCHIVE_DIR, DATA_DIR
from ingest.models.task import IngestInterface
from ingest.utils.helpers import copy_and_mkdir


class Ingest(IngestInterface, ABC):
    def __init__(self, brand: str, download_url: str = None) -> None:
        self.brand = brand
        self.download_url = download_url
        self.logger = logging.getLogger(f"{__name__}.{brand}")
        self.paths = {
            type: str(os.path.join(DATA_DIR, type, f"{brand.lower()}.{type}"))
            for type in ["html", "json"]
        }
        self.archive_paths = {
            type: str(os.path.join(ARCHIVE_DIR, type)) for type in ["html", "json"]
        }

    def download(self, headers: dict) -> None:
        """Downloads the brand's web page and writes it to the filesystem."""
        r = requests.get(self.download_url)
        if r.status_code == 200:
            with open(file=self.paths["html"], mode="w", encoding="utf-8") as html_file:
                html_file.write(r.text)
        else:
            raise ConnectionError(
                f"Failed to retrieve {self.download_url}, status code {r.status_code}"
            )

    @abstractmethod
    def extractor(self, input: str) -> str:
        """Pulls the raw data from the HTML file and returns JSON."""
        pass

    def parse(self) -> None:
        """
        Parses the raw HTML with self.extractor(),
        and stores the parsed JSON string in the filesystem.
        """
        with open(file=self.paths["html"]) as html_file:
            html_str = html_file.read()
            json_str = self.extractor(html_str)
            with open(file=self.paths["json"], mode="w") as json_file:
                json_file.write(json_str)

    @abstractmethod
    def ingest(self) -> None:
        """Reads JSON data from the parsed file and inserts into the database."""
        pass

    def archive(self) -> None:
        """Archives the HTML and JSON files in the archive directory."""
        filename = f"{self.brand.lower()}_{datetime.now().strftime('%d%m%Y_%H%M%S')}"
        for type in ["json", "html"]:
            filename = os.path.join(
                self.archive_paths[type],
                f"{self.brand.lower()}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.{type}",
            )
            self.logger.info("Archiving %s", self.paths[type])
            copy_and_mkdir(self.paths[type], filename)
            self.logger.info("Archived %s", filename)

    def execute(self) -> None:
        """Executes the ingest process."""
        try:
            self.logger.info("Starting %s ingest", self.brand)
            self.download()
            self.parse()
            self.ingest()
            self.archive()
            self.logger.info("Completed %s ingest", self.brand)
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Failed to complete %s ingest", self.brand)
