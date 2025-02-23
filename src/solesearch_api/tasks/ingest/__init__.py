from datetime import datetime
import json
import os
import re
import time
from typing import Callable
import random

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from solesearch_api.config import HTML_DIR, JSON_DIR
from solesearch_api.utils.browser import get_browser_headers
from solesearch_api.utils.extractors import next_json_extractor


def save_to_file(data: str, file_path: str) -> str:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(data)
    return file_path


def json_from_html(html: str, extractor: Callable[[str], dict]) -> dict:
    return extractor(html)


def get_html(
    brand: str,
    url: str,
    headers: dict = None,
    max_retries: int = 5,
    base_delay: float = 1.0,
) -> str:
    file_path = os.path.join(HTML_DIR, brand, datetime.now().strftime(f"%Y-%m-%d.html"))
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
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

    # Merge provided headers with browser headers
    final_headers = get_browser_headers(referer=url)
    if headers:
        final_headers.update(headers)

    # Add compression support
    final_headers["Accept-Encoding"] = "gzip, deflate, br"

    # Make the request with a random delay
    time.sleep(
        base_delay * (0.5 + random.random())
    )  # Random delay between 0.5x and 1.5x base_delay
    response = session.get(url, headers=final_headers, timeout=30)
    response.raise_for_status()
    html = response.text

    save_to_file(html, file_path)
    return html


def get_json(
    brand: str,
    url: str,
    headers: dict = None,
    extractor: Callable[[str], dict] = next_json_extractor,
) -> dict:
    file_path = os.path.join(JSON_DIR, brand, datetime.now().strftime(f"%Y-%m-%d.json"))
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    html_data = get_html(brand, url, headers)
    json_data = json_from_html(html_data, extractor)
    save_to_file(json.dumps(json_data, indent=2), file_path)
    return json_data
