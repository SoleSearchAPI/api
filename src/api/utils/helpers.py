import json
import os
import re

from core.models.details import Audience

STRIP_HTML = re.compile("<.*?>")


def html_cleaner(input: str) -> str:
    return re.sub(STRIP_HTML, "", input)


def format_float(num):
    return f"{num:.1f}" if num % 1 != 0 else f"{num:.0f}"


def puma_size_lookup(input: str) -> str:
    return format_float((get_id_int(input) - 6) * 0.5)


get_middle_pattern = re.compile(r"^.(.*).$")


def get_id_int(input: str) -> int:
    match = get_middle_pattern.match(input)
    if match:
        return int(match.group(1))
    else:
        raise ValueError("Invalid input")


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


def try_guess_audience(input: str) -> list:
    input = input.lower()
    if "women" in input or "woman" in input:
        return Audience.WOMEN
    elif "kids" in input or "kid" in input:
        return Audience.KIDS
    elif "toddler" in input or "baby" in input:
        return Audience.TODDLER
    elif "men" in input or "man" in input:
        return Audience.MEN
    elif "boy" in input:
        return Audience.BOYS
    elif "girl" in input:
        return Audience.GIRLS
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
        or any((slug.endswith(suffix) for suffix in invalid_suffixes))
        or any((slug.startswith(prefix) for prefix in invalid_prefixes))
        or any((content in slug for content in invalid_contents))
    )


def copy_and_mkdir(src: str, dst: str) -> None:
    """Copies a file to another directory and creates the destination directory if it does not exist."""
    directory = os.path.dirname(dst)
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.rename(src, dst)
    return None


def create_and_write_file(filename: str, contents: str) -> None:
    """Creates a file and writes contents to it."""
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename, "w") as f:
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
