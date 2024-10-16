from datetime import UTC, datetime

from core.models.details import Images, Prices
from core.models.shoes import Sneaker
from ingest.models.task import IngestInterface
from ingest.utils.helpers import try_guess_brand
from ingest.utils.sessions import session


class SnksDropsIngest(IngestInterface):
    def ingest(self) -> None:
        releases = session.get(
            "https://snkr-rest-api-nfrpf.ondigitalocean.app/api/ios/releases"
        )
        if releases.status_code != 200:
            raise Exception("Failed to fetch releases from snkrs-drops")
        else:
            sneakers = []
            for release in releases.json()["items"]:
                if not release["pid"] or release["pid"] == "TBD":
                    continue
                release_date = datetime.strptime(
                    release["date"][:-1], "%Y-%m-%dT%H:%M:%S.%f"
                )
                price = None
                try:
                    price = float(release["price"].replace("$", ""))
                except ValueError:
                    price = None
                sneakers.append(
                    Sneaker(
                        brand=try_guess_brand(release["name"]),
                        sku=release["pid"],
                        name=release["name"],
                        colorway=None,
                        audience=None,
                        release_date=release_date,
                        images=Images(
                            original=release["images"][0],
                            alternateAngles=release["images"][1:],
                        ),
                        links=None,
                        prices=Prices(retail=price) if price else None,
                        sizes=None,
                        description=None,
                        dateAdded=datetime.now(UTC),
                    )
                )
            Sneaker.insert_many(sneakers)

    def execute(self) -> None:
        self.ingest()
