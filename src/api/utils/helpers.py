import json
import re
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse

from api.models.sneaker.enums import Audience
from fastapi import Request

STRIP_HTML = re.compile("<.*?>")


def html_cleaner(dirty: str) -> str:
    return re.sub(STRIP_HTML, "", dirty)


def format_float(num):
    return f"{num:.1f}" if num % 1 != 0 else f"{num:.0f}"


get_middle_pattern = re.compile(r"^.(.*).$")


def get_id_int(s: str) -> int:
    match = get_middle_pattern.match(s)
    if match:
        return int(match.group(1))
    else:
        raise ValueError("Input does not match get_middle_pattern regex.")


def puma_size_lookup(puma_size: str) -> str:
    return format_float((get_id_int(puma_size) - 6) * 0.5)


def extract_redux_state(html: str) -> dict:
    get_redux_pattern = (
        r"window\.__PRELOADED_STATE__ = (.*?)(?=window\.__BUILD_CONTEXT__ = |$)"
    )
    matches = re.findall(get_redux_pattern, html, re.DOTALL)
    return json.loads(matches[0].strip().strip(";"))


def try_guess_brand(title: str) -> str:
    title = title.lower()
    if "adidas" in title:
        return "Adidas"
    elif "jordan" in title:
        return "Jordan"
    elif "yeezy" in title:
        return "Yeezy"
    elif "new balance" in title:
        return "New Balance"
    elif "nike" in title:
        return "Nike"
    elif "asics" in title:
        return "Asics"
    elif "converse" in title:
        return "Converse"
    elif "reebok" in title:
        return "Reebok"
    elif "puma" in title:
        return "Puma"
    elif "vans" in title:
        return "Vans"
    elif "saucony" in title:
        return "Saucony"
    elif "under armour" in title:
        return "Under Armour"
    elif "crocs" in title:
        return "Crocs"
    return ""


def try_guess_audience(text: str) -> list:
    text = text.lower()
    if "women" in text or "woman" in text:
        return Audience.WOMEN
    elif "kids" in text or "kid" in text:
        return Audience.YOUTH
    elif "toddler" in text or "baby" in text:
        return Audience.TODDLER
    elif "men" in text or "man" in text:
        return Audience.MEN
    else:
        return Audience.UNISEX


invalid_suffixes = [
    "-hobby-box",
    "-booster-box",
    "-booster-pack",
    "-blaster-pack",
    "-choice-box",
    "-lot",
    "-pack",
    "-vinyl-figure",
    "-booklet-magazine",
]
invalid_prefixes = [
    "abominable-toys-",
    "abraham-toro-20",
]
invalid_contents = [
    "-t-shirt-",
    "-sweatshirt-",
    "-sweatpant-",
    "-skateboard-deck-",
    "-long-sleeves-",
    "-bucket-cap-",
    "?",
]


def should_skip_link(link: str) -> str:
    """
    Given a stockx link, returns True if we should skip scraping the link.
    """
    if not link:
        return True
    slugs = link.split("/")
    if len(slugs) != 4:
        return True
    slug = slugs[-1]
    return (
        not slug
        or any(slug.endswith(suffix) for suffix in invalid_suffixes)
        or any(slug.startswith(prefix) for prefix in invalid_prefixes)
        or any(content in slug for content in invalid_contents)
    )


def copy_and_mkdir(src: str, dst: str) -> None:
    """
    Copies a file to another directory and creates the
    destination directory if it does not exist.
    """
    directory = Path(dst).parent
    if not Path.exists(directory):
        Path(directory).mkdir(parents=True)
    Path(src).rename(dst)
    return None


def create_and_write_file(filename: str, contents: str) -> None:
    """Creates a file and writes contents to it."""
    directory = Path(filename).parent
    if not Path(directory).exists():
        Path(directory).mkdir(parents=True)
    with Path(filename).open("w") as f:
        f.write(contents)
    return None


def merge_dot_notated_keys(obj: dict):
    # A helper function to recursively set the value in the nested dictionary
    def set_nested_value(dictionary, keys, value):
        key = keys.pop(0)
        if len(keys) == 0:
            dictionary[key] = value
        else:
            if key not in dictionary:
                dictionary[key] = {}
            set_nested_value(dictionary[key], keys, value)

    # Store keys to remove after iteration to avoid runtime error
    keys_to_remove = []

    # Iterate over the keys and merge the nested structures
    for key in list(obj.keys()):
        if "." in key:
            nested_keys = key.split(".")
            set_nested_value(obj, nested_keys, obj[key])
            keys_to_remove.append(key)

    # Remove the original dot-notated keys
    for key in keys_to_remove:
        del obj[key]

    return obj


def url_for_query(request: Request, fastapi_function_name: str, **params: str) -> str:
    url = str(request.url_for(fastapi_function_name))
    parsed = urlparse(url)
    parsed = parsed._replace(query=urlencode(params))
    return urlunparse(parsed)
