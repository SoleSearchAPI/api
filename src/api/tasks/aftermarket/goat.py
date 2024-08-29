import json
from datetime import datetime

import requests
from requests.utils import quote

default_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.6",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
}

default_params = {
    "c": "ciojs-client-2.35.2",
    "key": "key_XT7bjdbvjgECO5d8",
    "i": "b1f4104a-124a-4b72-aa1c-1a42614cc092",
    "num_results_per_page": "100",
    "sort_order": "descending",
    "fmt_options[hidden_fields]": "gp_instant_ship_lowest_price_cents_3",
    "fmt_options[hidden_facets]": "gp_instant_ship_lowest_price_cents_3",
    "variations_map": r'{"group_by":[{"name":"product_condition","field":"data.product_condition"},{"name":"box_condition","field":"data.box_condition"}],"values":{"min_regional_price":{"aggregation":"min","field":"data.gp_lowest_price_cents_3"},"min_regional_instant_ship_price":{"aggregation":"min","field":"data.gp_instant_ship_lowest_price_cents_3"}},"dtype":"object"}',
    "qs": r'{"features":{"display_variations":true},"feature_variants":{"display_variations":"matched"}}',
}


def __get_from_hidden_api(url, additional_params={}, additional_headers={}):
    response = requests.get(
        url,
        headers={**default_headers, **additional_headers},
        params={**default_params, **additional_params},
    )
    json = response.json()
    return json


def get_trending_sneakers():
    # Gets the "most wanted" collection
    response = __get_from_hidden_api(
        url="https://ac.cnstrc.com/browse/collection_id/most-wanted-new",
        additional_params={
            "s": "4",
            "page": "1",
            "filters[recently_released]": "sneakers",
            "sort_by": "release_date",
            "_dt": str(int(datetime.now().timestamp() * 1000)),
        },
    )
    return response["response"]["results"]


def search(search_term):
    # Searches the goat website for the given search term
    # Returns a list of the top 10 search results
    response = __get_from_hidden_api(
        url=f"https://ac.cnstrc.com/search/{quote(search_term)}",
        additional_params={
            "s": "2",
            "page": "1",
            "sort_by": "relevance",
            "_dt": str(int(datetime.now().timestamp() * 1000)),
        },
    )
    return response
