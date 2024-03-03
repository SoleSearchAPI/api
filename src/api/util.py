from urllib.parse import urlencode, urlparse, urlunparse

from fastapi import Request


def url_for_query(request: Request, name: str, **params: str) -> str:
    url = str(request.url_for(name))
    parsed = urlparse(url)
    parsed = parsed._replace(query=urlencode(params))
    return urlunparse(parsed)
