import re

STRIP_HTML = re.compile("<.*?>")


def html_cleaner(html: str) -> str:
    return re.sub(STRIP_HTML, "", html)
