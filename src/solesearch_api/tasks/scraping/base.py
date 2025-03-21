import json
import os
import random
import time
from datetime import datetime
from typing import Callable

import logfire
import requests
from requests.adapters import HTTPAdapter
from sqlmodel import Session
from urllib3 import Retry

from solesearch_api.config import HTML_DIR, JSON_DIR
from solesearch_api.db import engine
from solesearch_api.models.enums import Audience
from solesearch_api.utils.browser import get_default_browser_headers

logfire.configure(service_name="worker")


class MisconfigurationError(ValueError):
    pass


class BaseScrapingTask:
    def __init__(
        self,
        brand: str,
        audience_mapping: dict[str, Audience],
        download_url: str = None,
        headers: dict = {},
        extractor: Callable[[str], dict] | None = None,
        *args,
        **kwargs,
    ):
        if not brand:
            raise MisconfigurationError("brand is required")
        if not audience_mapping:
            raise MisconfigurationError("audience_mapping is required")
        if not extractor:
            raise MisconfigurationError("extractor is required")
        self.audience_mapping = audience_mapping
        self.brand = brand
        self.download_url = download_url
        self.headers = get_default_browser_headers()
        if headers:
            self.headers.update(headers)
        self.extractor = extractor

    def run(self, *args, **kwargs):
        logfire.info(
            "Running scraping task",
            brand=self.brand,
            task_name=self.__class__.__name__,
        )
        result = self.scrape(*args, **kwargs)
        logfire.info(
            "Scraping task completed",
            brand=self.brand,
            task_name=self.__class__.__name__,
            result=result,
        )
        return result

    def guess_audience(self, gender: str | list[str]) -> Audience:
        if gender not in self.audience_mapping:
            logfire.warning(
                f"'{gender}' not in {self.__class__.__name__} audience_mapping",
            )
        return self.audience_mapping.get(gender, Audience.UNKNOWN)

    def save_to_file(self, data: str, file_path: str) -> str:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(data)
        return file_path

    def get_html(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
    ) -> str:
        file_path = os.path.join(
            HTML_DIR,
            self.brand,
            self.__class__.__name__,
            datetime.now().strftime("%Y-%m-%d.html"),
        )
        if os.path.exists(file_path):
            with open(file_path) as f:
                logfire.info(
                    "HTML data loaded from file",
                    brand=self.brand,
                    task_name=self.__class__.__name__,
                    file_path=file_path,
                )
                return f.read()
        # Create a session with retry strategy
        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=base_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "OPTIONS"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Make the request with a random delay
        time.sleep(
            base_delay * (0.5 + random.random()),
        )  # Random delay between 0.5x and 1.5x base_delay
        response = session.get(self.download_url, headers=self.headers, timeout=30)
        response.raise_for_status()
        html = response.text
        self.save_to_file(html, file_path)
        logfire.info(
            "HTML data saved to file",
            brand=self.brand,
            task_name=self.__class__.__name__,
            file_path=file_path,
        )
        return html

    def get_json(self) -> dict:
        file_path = os.path.join(
            JSON_DIR,
            self.brand,
            self.__class__.__name__,
            datetime.now().strftime("%Y-%m-%d.json"),
        )
        if os.path.exists(file_path):
            with open(file_path) as f:
                logfire.info(
                    "JSON data loaded from file",
                    brand=self.brand,
                    task_name=self.__class__.__name__,
                    file_path=file_path,
                )
                return json.load(f)
        html_data = self.get_html()
        json_data = self.extractor(html_data)
        self.save_to_file(json.dumps(json_data, indent=2), file_path)
        logfire.info(
            "JSON data saved to file",
            brand=self.brand,
            task_name=self.__class__.__name__,
            file_path=file_path,
        )
        return json_data
