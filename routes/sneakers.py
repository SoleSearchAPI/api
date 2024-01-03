import config
from data.client import find_sneaker_by_id, find_sneakers
from fastapi import APIRouter

router = APIRouter()


@router.get("/sneakers")
async def get_sneakers(
    limit: int = config.DEFAULT_LIMIT, offset: int = config.DEFAULT_OFFSET
):
    return find_sneakers(limit, offset)


@router.get("/sneakers/{product_id}")
async def get_sneaker_by_id(product_id: str):
    return find_sneaker_by_id(product_id)
