from typing import List

from core.data.models import Sneaker
from pydantic import BaseModel


class PaginatedSneakersResponse(BaseModel):
    total: int
    page: int
    pageSize: int
    nextPage: str | None
    previousPage: str | None
    items: List[Sneaker]
