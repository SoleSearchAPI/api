from typing import Annotated

from fastapi import APIRouter, Query

import config
from data.instance import ASCENDING, DESCENDING, find_sneaker_by_id, find_sneakers
from data.models import Audience

router = APIRouter()


@router.get("/sneakers")
async def get_sneakers(
    brand: str | None = None,
    sku: str | None = None,
    name: str | None = None,
    colorway: str | None = None,
    audience: Audience | None = None,
    releaseDate: str | None = None,
    released: bool | None = None,
    sort: str = "releaseDate",
    sortOrder: int = DESCENDING,
    offset: Annotated(int, Query(gte=1, lte=100)) = config.DEFAULT_OFFSET,
    limit: int = config.DEFAULT_LIMIT,
):
    return find_sneakers(
        brand=brand,
        sku=sku,
        name=name,
        colorway=colorway,
        audience=audience,
        release_date=releaseDate,
        released=released,
        sort_by=sort,
        sort_order=sortOrder,
        offset=offset,
        limit=limit,
    )


@router.get("/sneakers/{product_id}")
async def get_sneaker_by_id(product_id: str):
    return find_sneaker_by_id(product_id)


@router.get("/sneakers/{product_id}/prices")
async def get_sneaker_pricing(product_id: str):
    return {"Error": "Not implemented yet"}


@router.get("/sneakers/{product_id}/prices/{size}")
async def get_sneaker_size_pricing(product_id: str, size: str):
    return
