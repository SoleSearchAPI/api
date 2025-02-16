from datetime import datetime
import json
import os
import re
from typing import Callable

import requests
from bs4 import BeautifulSoup

from solesearch_api.config import HTML_DIR, JSON_DIR
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
) -> str:
    file_path = os.path.join(HTML_DIR, brand, datetime.now().strftime(f"%Y-%m-%d.html"))
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    response = requests.get(url, headers=headers)
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
