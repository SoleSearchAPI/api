import json
from datetime import UTC, datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from core.models.details import Audience, Images, Links, Prices
from core.models.shoes import Sneaker
from ingest.models.json import Ingest
from ingest.utils.helpers import html_cleaner, puma_size_lookup


class PumaIngest(Ingest):
    def __init__(self):
        super().__init__(
            brand="Puma", download_url="https://us.puma.com/us/en/launch-calendar"
        )

    def extractor(self, input: str) -> str:
        soup = BeautifulSoup(input, "html.parser")
        nextjs_data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
        hrefs = {
            a["href"].split("?")[0].split("/")[-1]: a["href"]
            for a in soup.select("a.tw-5wv114.tw-ozwx86")
            if a["href"].startswith("/us/en/pd/")
        }
        json_data = json.loads(
            list(nextjs_data["props"]["urqlState"].values())[-1]["data"]
        )["content"]["products"]
        return json.dumps(
            {
                "hrefs": hrefs,
                "next": json_data,
            }
        )

    def ingest(self):
        product_count = 0
        with open(file=self.paths["json"]) as json_file:
            json_data = json.loads(json_file.read())
            sneakers: List[Sneaker] = []
            for product in json_data["next"]:
                masterId = product["masterId"]
                if not masterId:
                    self.logger.debug(
                        "Skipping product with no masterId. These are usually links to collections or collaborations and not individual products."
                    )
                    continue
                if masterId not in json_data["hrefs"]:
                    self.logger.error(
                        f"No matching product found with masterId={masterId}"
                    )
                    continue
                href = json_data["hrefs"][masterId]
                if href:
                    retail_link_base = (
                        f"https://us.puma.com{href.split('?')[0]}?swatch="
                    )
                    product_details_page = requests.get(
                        f"https://us.puma.com{href}"
                    ).text
                    soup = BeautifulSoup(product_details_page, "html.parser")

                    def detail_test(blob):
                        if "data" in blob:
                            blob_new = json.loads(blob["data"].replace('\\"', ""))
                            if "product" in blob_new:
                                if "productStory" in blob_new["product"]:
                                    return blob_new["product"]
                        return {}

                    product_details = {}
                    try:
                        product_details = next(
                            filter(
                                lambda x: x != {},
                                map(
                                    detail_test,
                                    json.loads(
                                        soup.find("script", id="__NEXT_DATA__").string
                                    )["props"]["urqlState"].values(),
                                ),
                            )
                        )
                    except StopIteration:
                        print("No product details found!")
                    brand = "Puma"
                    name = product_details["name"]
                    for variant in product_details["variations"]:
                        sku = variant["styleNumber"]
                        colorway = variant["colorName"]
                        release_date = int(
                            datetime.strptime(
                                product["launchDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
                            )
                        )
                        images = Images(
                            original=variant["preview"],
                            alternateAngles=[img["href"] for img in variant["images"]],
                        )
                        prices = Prices(retail=float(variant["price"]))
                        links = Links(retail=retail_link_base + variant["colorValue"])
                        sizes = [
                            puma_size_lookup(s["id"])
                            for s in variant["sizeGroups"][0]["sizes"]
                        ]

                        # TODO: This deserves another look... very hacky
                        genders = []
                        for group in variant["sizeGroups"]:
                            if not group["label"]:
                                if (puma_size_lookup(group["sizes"][0]["id"])) == group[
                                    "sizes"
                                ][0]["label"]:
                                    genders.append("MEN")
                                else:
                                    genders.append("WOMEN")
                            else:
                                if group["label"] == "Mens":
                                    genders.append("MEN")
                                elif group["label"] == "Womens":
                                    genders.append("WOMEN")
                        audience = ""
                        if "MEN" in genders:
                            if "WOMEN" in genders:
                                audience = Audience.UNISEX
                            else:
                                audience = Audience.MEN
                        elif "WOMEN" in genders:
                            audience = Audience.WOMEN
                        else:
                            audience = Audience.UNISEX

                        description = html_cleaner(variant["description"])

                        now_epoch = datetime.now(UTC)

                        # Create an instance of the Shoe object
                        sneakers.append(
                            Sneaker(
                                sku=sku,
                                brand=brand,
                                name=name,
                                colorway=colorway,
                                audience=audience,
                                releaseDate=release_date,
                                images=images,
                                links=links,
                                prices=prices,
                                sizes=sizes,
                                description=description,
                                dateAdded=now_epoch,
                                lastScraped=now_epoch,
                                source="puma.com",
                            )
                        )
                        product_count += 1
                else:
                    raise Exception(f"Missing URL for master_id: {masterId}")
            Sneaker.insert_many(sneakers)
            self.logger.info(f"Found {product_count} products!")
