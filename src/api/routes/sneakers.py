from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from api.data.instance import DEFAULT_LIMIT, DEFAULT_OFFSET
from api.data.models import SortKey, SortOrder
from api.data.queries import find_sneakers
from core.models.details import Audience
from core.models.shoes import Sneaker

router = APIRouter(
    prefix="/sneakers",
)


@router.get("/")
async def get_sneakers(
    brand: str | None = None,
    sku: str | None = None,
    name: str | None = None,
    colorway: str | None = None,
    audience: Audience | None = None,
    releaseDate: str | None = None,
    released: bool | None = None,
    sort: SortKey = SortKey.RELEASE_DATE,
    sortOrder: SortOrder = SortOrder.DESCENDING,
    offset: Annotated[int, Query(gte=DEFAULT_OFFSET)] = DEFAULT_OFFSET,
    limit: Annotated[int, Query(gte=1, lte=100)] = DEFAULT_LIMIT,
):
    return await find_sneakers(
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


@router.get("/{product_id}")
async def get_sneaker_by_id(product_id: str):
    if not product_id:
        raise HTTPException(status_code=400, detail="Invalid product_id")
    return await Sneaker.get(product_id)


@router.get("/sku/{sku}")
async def get_sneaker_by_sku(sku: str, brand: str | None = None):
    if not sku:
        raise HTTPException(status_code=400, detail="Invalid sku")
    if brand:
        return await Sneaker.find_one(Sneaker.sku == sku, Sneaker.brand == brand)
    else:
        return await Sneaker.find_one(Sneaker.sku == sku)
