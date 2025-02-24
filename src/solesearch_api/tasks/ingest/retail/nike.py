from solesearch_api.tasks.ingest import get_json, next_json_extractor
from solesearch_api.tasks.ingest.task import IngestTask
from solesearch_api.tasks import app


class NikeIngest(IngestTask):
    def ingest(self, session, *args, **kwargs):
        brand = "Nike"
        download_url = "https://www.nike.com/launch?s=upcoming"
        json = get_json(brand, download_url, extractor=next_json_extractor)
        return json


@app.task(name="nike_ingest")
def nike_ingest():
    task = NikeIngest()
    return task.run()


# def json_to_sneakers(json):
#     react_state = json
#     products = react_state["product"]["threads"]["data"]["items"]
#     product_details = react_state["product"]["products"]["data"]["items"]
#     more_details = {
#         x["threadId"]: (x["productId"], x["startEntryDate"])
#         for x in react_state["viewFeed"]["upcomingIds"]
#     }
#     sneakers = []
#     for thread_id in products:
#         try:
#             product_id = more_details.get(thread_id)
#             if product_id:
#                 product_id = product_id[0]
#             else:
#                 raise Exception(f"Missing product_id for thread_id: {thread_id}")

#             product = products[thread_id]
#             details = product_details.get(product_id)
#             if not details:
#                 raise Exception(f"Missing product details for product_id: {product_id}")

#             if details["productType"] != "FOOTWEAR":
#                 raise Exception(
#                     f"Product was type {details['productType']}, not footwear!"
#                 )

#             sku = details["styleColor"]
#             brand = details["brand"]
#             name = re.sub(r" \(.*-.*\) Release Date", "", product["seo"]["title"])
#             colorway = details["colorDescription"]
#             audience = details["genders"]
#             release_date = more_details[thread_id][1]
#             images = Images(
#                 original=product["coverCard"]["defaultURL"],
#                 alternateAngles=[
#                     x["defaultURL"]
#                     for x in next(
#                         filter(
#                             lambda x: x["subType"] == "carousel",
#                             product["cards"],
#                         )
#                     )["cards"]
#                     if x["subType"] == "image"
#                     and x["defaultURL"] != product["coverCard"]["defaultURL"]
#                 ],
#             )
#             links = Links(retail=product["externalLink"])
#             prices = Prices(retail=details.get("msrp", details.get("fullPrice", None)))
#             sizes = [x["nikeSize"] for x in details["skus"]]
#             description = html_cleaner(
#                 next(
#                     filter(
#                         lambda x: x["subType"] == "carousel",
#                         product["cards"],
#                     )
#                 )["description"]
#             )

#             now_utc = datetime.now(UTC)

#             sneakers.append(
#                 Sneaker(
#                     brand=brand,
#                     sku=sku,
#                     name=name,
#                     colorway=colorway,
#                     audience=audience,
#                     releaseDate=release_date,
#                     images=images,
#                     links=links,
#                     prices=prices,
#                     sizes=sizes,
#                     description=description,
#                     dateAdded=now_utc,
#                     lastScraped=now_utc,
#                     source="nike.com",
#                 )
#             )

#         except Exception as e:
#             self.logger.error(f"Skipping threadId: '{thread_id}'. {e}")
#     Sneaker.insert_many(sneakers, ordered=False)
#     logger.info(f"Inserted {len(sneakers)} sneakers")
