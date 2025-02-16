from solesearch_api.tasks.ingest import get_json, next_json_extractor
from solesearch_api.tasks.ingest.task import IngestTask
from solesearch_api.tasks import app


class AdidasIngest(IngestTask):
    def ingest(self, session, *args, **kwargs):
        brand = "Adidas"
        download_url = "https://www.adidas.com/us/release-dates"
        json = get_json(brand, download_url, extractor=next_json_extractor)
        return json


@app.task(name="adidas_ingest")
def adidas_ingest():
    task = AdidasIngest()
    return task.run()
