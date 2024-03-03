import os
from datetime import UTC, datetime
import os
from typing import Annotated

from core.models.details import Audience
from core.models.shoes import Sneaker
from fastapi import APIRouter, HTTPException, Query, Request

from api.data.models import PaginatedSneakersResponse, SortKey, SortOrder
from api.util import url_for_query

router = APIRouter(
    prefix="/sneakers",
)

MAX_LIMIT = int(os.environ.get("SOLESEARCH_MAX_LIMIT", 100))
DEFAULT_LIMIT = int(os.environ.get("SOLESEARCH_DEFAULT_LIMIT", 20))


@router.get("/")
async def get_sneakers(
    request: Request,
    brand: str | None = None,
    name: str | None = None,
    colorway: str | None = None,
    audience: Audience | None = None,
    releaseDate: str | None = None,
    released: bool | None = None,
    sort: SortKey = SortKey.RELEASE_DATE,
    order: SortOrder = SortOrder.DESCENDING,
    page: Annotated[int | None, Query(gte=1)] = None,
    pageSize: Annotated[int | None, Query(gte=1, lte=MAX_LIMIT)] = None,
) -> PaginatedSneakersResponse:
    query = Sneaker.find()
    if not page:
        page = 1
    if not pageSize:
        pageSize = DEFAULT_LIMIT
    if brand:
        query = query.find({"brand": {"$regex": f"^{brand}", "$options": "i"}})
    if name:
        query = query.find({"name": {"$regex": f"^{name}", "$options": "i"}})
    if colorway:
        query = query.find({"colorway": {"$regex": f"^{colorway}", "$options": "i"}})
    if audience:
        query = query.find({"audience": {"$regex": f"^{audience.value}"}})
    if released is not None:
        now = datetime.now(UTC)
        if released:
            query = query.find(Sneaker.releaseDate <= now)
        else:
            query = query.find(Sneaker.releaseDate > now)
    elif releaseDate:
        if ":" in releaseDate:
            inequality_operator, date_str = releaseDate.split(":")
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if inequality_operator == "lt":
                query = query.find(Sneaker.releaseDate < date_obj)
            elif inequality_operator == "lte":
                query = query.find(Sneaker.releaseDate <= date_obj)
            elif inequality_operator == "gt":
                query = query.find(Sneaker.releaseDate > date_obj)
            elif inequality_operator == "gte":
                query = query.find(Sneaker.releaseDate >= date_obj)
        else:
            date_obj = datetime.strptime(releaseDate, "%Y-%m-%d")
            query = query.find(Sneaker.releaseDate == date_obj)
    total_count = await query.count()
    params = dict(request.query_params)
    if total_count > page * pageSize:
        params["page"] = page + 1
        next_page = url_for_query(request, "get_sneakers", **params)
    else:
        next_page = None
    if page > 1:
        params["page"] = page - 1
        previous_page = url_for_query(request, "get_sneakers", **params)
    else:
        previous_page = None
    items = (
        await query.sort(f"{'+' if order == SortOrder.ASCENDING else '-'}{sort.value}")
        .skip((page - 1) * pageSize)
        .limit(pageSize)
        .to_list()
    )
    result = PaginatedSneakersResponse(
        total=total_count,
        page=page,
        pageSize=pageSize,
        nextPage=next_page,
        previousPage=previous_page,
        items=items,
    )
    return result


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
