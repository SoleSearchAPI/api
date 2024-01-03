import config
from data.client import find_sneakers
from fastapi import APIRouter

router = APIRouter()


@router.get("/sneakers")
async def get_sneakers(
    limit: int = config.DEFAULT_LIMIT, offset: int = config.DEFAULT_OFFSET
):
    return find_sneakers(limit, offset)
