from core.graphql.sc_operations import Operations
from sgqlc.endpoint.requests import RequestsEndpoint

from ingest.db.instance import client
from ingest.models.task import IngestInterface


class SneakerCrushIngest(IngestInterface):
    def execute(self) -> None:
        endpoint = RequestsEndpoint(
            url="https://thesneakercrush.com/graphql",
            base_headers={
                "x-secret": "xDqkUbTE3B6KvSlEbKva1xopqMr9BR9bbwcY4+uGuRvpRyWiA60UTN5YkTCulD2x"
            },
        )
        op = Operations.query.get_sneakers
        hasNextPage = True
        p = 0
        while hasNextPage:
            data = endpoint(op, {"sort": {"date": -1}, "perPage": 1000, "page": p})
            if data["data"]["ReleasePagination"]["items"]:
                for item in data["data"]["ReleasePagination"]["items"]:
                    if item["_id"]:
                        item["sneakerCrushId"] = item["_id"]
                        del item["_id"]
                client["sneakercrush-sneakers"].insert_many(
                    data["data"]["ReleasePagination"]["items"],
                )
                print(f"Inserted 1000 sneakers!")
            if data["data"]["ReleasePagination"]["pageInfo"]:
                hasNextPage = data["data"]["ReleasePagination"]["pageInfo"][
                    "hasNextPage"
                ]
                print(f"Page {p} done!")
            else:
                hasNextPage = False
            p += 1
        print("Done")

    def drop_dupes(self) -> None:
        dupes = client["sneakercrush-sneakers"].aggregate(
            [
                {
                    "$group": {
                        "_id": "$sneakerCrushId",
                        "uniqueIds": {"$addToSet": "$_id"},
                        "count": {"$sum": 1},
                    }
                },
                {"$match": {"count": {"$gt": 1}}},
            ]
        )
        for document in dupes:
            document["uniqueIds"].pop(0)
            client["sneakercrush-sneakers"].delete_many(
                {"_id": {"$in": document["uniqueIds"]}}
            )
