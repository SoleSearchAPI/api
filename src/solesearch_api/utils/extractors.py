import json
import re

from bs4 import BeautifulSoup


def react_json_extractor(html: str) -> dict:
    react_app_script = re.search("<script>document.getElementById.*</script>", html)
    return (
        "{"
        + react_app_script.group()
        .split("{", 2)[2]
        .split("};window.initilizeAppWithHandoffState", 1)[0]
        + "}"
    )


def next_json_extractor(html: str) -> dict:
    """Extracts the JSON blob from the __NEXT_DATA__ script in an HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")

    if script_tag:
        json_data = json.loads(script_tag.string)
        page_props = json_data.get("props", {}).get("pageProps", None)

        if not page_props:
            return None

        if isinstance(page_props, str):
            page_props = json.loads(page_props)

        initial_state = page_props.get("initialState")
        if initial_state and isinstance(initial_state, str):
            return json.loads(initial_state)
        elif initial_state and isinstance(initial_state, dict):
            return initial_state

        return page_props

    return {}
