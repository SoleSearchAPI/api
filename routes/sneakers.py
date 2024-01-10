from fastapi import APIRouter

import config
from data.instance import find_sneaker_by_id, find_sneakers

router = APIRouter()


@router.get("/sneakers")
async def get_sneakers(
    limit: int = config.DEFAULT_LIMIT, offset: int = config.DEFAULT_OFFSET
):
    return find_sneakers(limit, offset)


@router.get("/sneakers/{product_id}")
async def get_sneaker_by_id(product_id: str):
    return find_sneaker_by_id(product_id)


@router.get("/sneakers/{product_id}/prices")
async def get_sneaker_pricing(product_id: str):
    return {"Error": "Not implemented yet"}


@router.get("/sneakers/{product_id}/prices/{size}")
async def get_sneaker_size_pricing(product_id: str, size: str):
    return
