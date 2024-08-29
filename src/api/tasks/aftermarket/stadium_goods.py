import logging

from core.models.details import Images, Links, Prices
from core.models.shoes import Sneaker
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType

from ingest.db.mutations import upsert_many
from ingest.models.task import IngestInterface
from ingest.utils.helpers import extract_redux_state, try_guess_audience
from ingest.utils.proxies import get_working_proxy


class StadiumGoodsIngest(IngestInterface):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.collection_name = "stadiumgoods"
        self.logger = logging.getLogger(__name__)

    def get_stadium_goods_queue(self) -> List[dict]:
        return list(
            db["stadiumgoods"].find(
                {"$or": [{"sku": {"$exists": False}}, {"sku": None}]},
                {"links.stadium_goods": 1, "stadiumGoodsId": 1},
            )
        )

    def grab_redux_with_selenium(self, url: str) -> dict:
        self.driver.get(url)
        redux_state_script = self.driver.find_element(
            By.CSS_SELECTOR, "body > script:nth-child(3)"
        )
        return extract_redux_state(redux_state_script.get_attribute("innerHTML"))

    def shopping_index(self, url: str) -> int:
        page_data = self.grab_redux_with_selenium(url)
        shoes = []
        for productId, product in page_data["entities"]["products"].items():
            brand = page_data["entities"]["brands"][str(product["brand"])]["name"]
            audience = [try_guess_audience(product["genderName"])]
            links = Links(
                stadium_goods=f"https://www.stadiumgoods.com/shopping/{product['slug'].strip()}"
            )
            prices = Prices(stadium_goods=product["prices"])
            images = None
            angles = [
                list(angle["sources"].values())[-1] for angle in product["images"]
            ]
            images = Images(original=angles[0], alternateAngles=angles[1:])
            shoes.append(
                StadiumGoods(
                    stadiumGoodsId=productId,
                    brand=brand,
                    name=product["shortDescription"],
                    audience=audience,
                    links=links,
                    prices=prices,
                    images=images,
                )
            )
        upsert_many(shoes, self.collection_name)
        return int(
            list(page_data["entities"]["searchResults"].values())[0]["products"][
                "totalPages"
            ]
        )

    def product_page(self, url: str, productId: str) -> StadiumGoods:
        page_data = self.grab_redux_with_selenium(url)
        product_data = page_data["entities"]["products"][productId]
        sku = product_data["sku"].strip().replace(" ", "-")
        description = product_data["description"]
        colorway = next(
            (
                x["color"]["name"]
                for x in product_data["colors"]
                if "DesignerColor" in x["tags"]
            ),
            None,
        )
        prices = {}
        sizes = []
        for variant in product_data["variants"]:
            prices[variant["sizeDescription"]] = variant["price"][
                "includingTaxesWithoutDiscount"
            ]
            sizes.append(
                float(
                    "".join(
                        i for i in variant["sizeDescription"] if i.isdigit() or i == "."
                    )
                )
            )
        sizes = list(set(sizes))
        return StadiumGoods(
            stadiumGoodsId=productId,
            sku=sku,
            description=description,
            colorway=colorway,
            prices=Prices(stadium_goods=prices),
            sizes=sizes,
        )

    def execute(self) -> None:
        page = 1
        totalPages = 500
        while page <= totalPages:
            url = f"https://www.stadiumgoods.com/en-us/shopping?categories=139499|139522|139515|186123|139557|139569|195318&pageindex={page}"
            try:
                totalPages = self.shopping_index(url)
                page += 1
            except NoSuchElementException:
                self.driver.quit()
                proxy_address = get_working_proxy()
                proxy = Proxy(
                    {
                        "proxyType": ProxyType.MANUAL,
                        "httpProxy": proxy_address,
                        "sslProxy": proxy_address,
                        "noProxy": "localhost",
                    }
                )
                self.driver = webdriver.Chrome(proxy=proxy)
            except Exception as e:
                self.logger.error(e)

    def execute_product_pages(self) -> None:
        updates = []
        queue = Sneaker.find({"$or": [{"sku": {"$exists": False}}, {"sku": None}]})
        for i in range(len(queue)):
            product = queue[i]
            self.logger.info(
                f"Scraping Stadium Goods '{product['stadiumGoodsId']}' {i+1}/{len(queue)}"
            )
            keep_trying = True
            retry_count = 0
            while keep_trying and retry_count < 5:
                try:
                    update = self.product_page(
                        product["links"]["stadium_goods"], product["stadiumGoodsId"]
                    )
                    updates.append(update)
                    self.logger.info("Done")
                    keep_trying = False
                except NoSuchElementException:
                    retry_count += 1
                    self.driver.quit()
                    proxy_address = get_working_proxy()
                    proxy = Proxy(
                        {
                            "proxyType": ProxyType.MANUAL,
                            "httpProxy": proxy_address,
                            "sslProxy": proxy_address,
                            "noProxy": "localhost",
                        }
                    )
                    self.driver = webdriver.Chrome(proxy=proxy)
                except Exception as e:
                    self.logger.error(e)
                    keep_trying = False
        upsert_many(updates, self.collection_name)
