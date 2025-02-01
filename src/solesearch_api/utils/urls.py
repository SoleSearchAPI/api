from urllib.parse import urlencode, urlparse, urlunparse

from fastapi import Request


def url_for_query(request: Request, fastapi_function_name: str, **params: str) -> str:
    url = str(request.url_for(fastapi_function_name))
    parsed = urlparse(url)
    parsed = parsed._replace(query=urlencode(params))
    return urlunparse(parsed)
