import asyncio
import os

from beanie import Document

from ingest.models.task import IngestInterface
from ingest.utils.sessions import session


class UserAgent(Document):
    useragent: str

    class Settings:
        collection = "useragents"


class UserAgentIngest(IngestInterface):
    def __init__(self):
        self.url = "https://api.whatismybrowser.com/api/v2/user_agent_database_search"
        self.headers = {
            "X-API-KEY": os.environ.get("SOLESEARCH_WIMB_API_KEY", "API_KEY_NOT_SET"),
        }

    async def __get_useragents_api(
        self, operating_system_name: str, software_name: str
    ) -> None:
        querystring = {
            "order_by": "first_seen_at",
            "limit": "500",
            "software_type": "browser",
            "operating_system_name": operating_system_name,
            "software_name": software_name,
        }
        useragents = [
            UserAgent(useragent=result["user_agent"])
            for result in session.get(
                self.url,
                headers=self.headers,
                params=querystring,
            ).json()["search_results"]["user_agents"]
        ]
        UserAgent.insert_many(useragents)

    async def execute(self) -> None:
        await UserAgent.delete_all()
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.__get_useragents_api("macOS", "Safari"))
            tg.create_task(self.__get_useragents_api("macOS", "Chrome"))
            tg.create_task(self.__get_useragents_api("Windows", "Chrome"))
            tg.create_task(self.__get_useragents_api("Windows", "Firefox"))
