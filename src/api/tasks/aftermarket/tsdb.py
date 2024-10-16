import logging
from datetime import datetime

from core.models.details import Images, Links, Prices
from core.models.shoes import Sneaker
from requests_ratelimiter import LimiterSession

from ingest.utils.helpers import try_guess_audience, try_guess_brand

session = LimiterSession(per_second=0.1)
RAPIDAPI_KEY = "f635b2115amsh097a1839162450cp1159d6jsnc89aca8eaeff"
url = "https://the-sneaker-database.p.rapidapi.com/search"
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.7",
    "origin": "https://thesneakerdatabase.com",
    "referer": "https://thesneakerdatabase.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Rapidapi-Host": "the-sneaker-database.p.rapidapi.com",
    "X-Rapidapi-Key": RAPIDAPI_KEY,
}

logger = logging.getLogger(__name__)


def get_by_sku(sku: str) -> dict:
    url = "https://the-sneaker-database.p.rapidapi.com/search"
    querystring = {"query": sku.strip(), "limit": "50"}
    response = session.get(url, headers=headers, params=querystring).json()
    if "results" in response and len(response["results"]) > 0:
        return response["results"][0]


async def get_latest() -> None:
    num_pages = 10
    querystring = {"limit": "100", "page": "0"}
    for page in range(num_pages):
        logger.info(f"Getting page {page}/{num_pages} of search results...")
        querystring["page"] = str(page)
        response = session.get(url, headers=headers, params=querystring).json()
        if "results" in response and len(response["results"]) > 0:
            for result in response["results"]:
                existing = await Sneaker.find_one(sku=result["sku"])
                if existing:
                    logger.info(f"{result['sku']} already in DB, filling in gaps...")
                else:
                    guessed_brand = try_guess_brand(result["brand"].strip())
                    sneaker = Sneaker(
                        sku=result["sku"].strip(),
                        name=result["name"].strip(),
                        brand=(
                            guessed_brand
                            if len(guessed_brand) > 0
                            else result["brand"].strip()
                        ),
                        colorway=result["colorway"].strip(),
                        audience=try_guess_audience(result["gender"]),
                        release_date=datetime.strptime(result["releaseDate"].strip()),
                        prices=Prices(retail=float(result["retailPrice"])),
                        links=Links(
                            stockx=result["links"]["stockX"],
                            goat=result["links"]["goat"],
                            flight_club=result["links"]["flightClub"],
                            stadium_goods=result["links"]["stadiumGoods"],
                        ),
                        description=result["story"].strip(),
                        images=Images(url=result["media"]["imageUrl"]),
                        tsdbId=result["id"],
                    )
                    await Sneaker.insert(sneaker)
                    logger.info(f"Inserting {result['sku']} into DB...")


async def execute() -> None:
    await get_latest()
