import os
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from api.data.models import PaginatedSneakersResponse, SortKey, SortOrder
from api.util import url_for_query
from core.models.details import Audience
from core.models.shoes import Sneaker, SneakerView

router = APIRouter(
    prefix="/sneakers",
)

MAX_LIMIT = int(os.environ.get("SOLESEARCH_MAX_LIMIT", 100))
DEFAULT_LIMIT = int(os.environ.get("SOLESEARCH_DEFAULT_LIMIT", 20))


@router.get("/")
async def get_sneakers(
    request: Request,
    brand: Annotated[
        str | None,
        Query(
            title="Brand", description="Filter by the brand of the shoes.", min_length=3
        ),
    ] = None,
    name: Annotated[
        str | None,
        Query(
            title="Product Name",
            description="Filter by the name of the shoes.",
            min_length=3,
        ),
    ] = None,
    colorway: Annotated[
        str | None,
        Query(
            title="Colorway",
            description="Filter by the colorway of the shoes.",
            min_length=3,
        ),
    ] = None,
    audience: Annotated[
        Audience | None,
        Query(
            title="Audience",
            description="Filter on the gender/audience of the shoes. See Audience for possible values.",
            min_length=3,
        ),
    ] = None,
    releaseDate: Annotated[
        str | None,
        Query(
            title="Release Date",
            description="Filter by the release date of the shoes. Can be a specific date or an inequality. Operators are (lt, lte, gt, gte). Example usage: lt:2021-01-01",
        ),
    ] = None,
    released: Annotated[
        bool | None,
        Query(
            title="Released?",
            description="Filter by whether the shoes have been released or not. Overrides any filter on releaseDate if set.",
        ),
    ] = None,
    sort: Annotated[
        SortKey,
        Query(
            title="Sort By",
            description="The field to sort by.",
        ),
    ] = SortKey.RELEASE_DATE,
    order: Annotated[
        SortOrder,
        Query(
            title="Sort Order",
            description="The order to sort in based on the sort key.",
        ),
    ] = SortOrder.DESCENDING,
    page: Annotated[
        int | None,
        Query(
            gte=1, title="Page Number", description="The page number of the result set."
        ),
    ] = None,
    pageSize: Annotated[
        int | None,
        Query(
            gte=1,
            lte=MAX_LIMIT,
            title="Page Size",
            description=f"The number of items on each page. Must be in the range [1-{MAX_LIMIT}] (inclusive).",
        ),
    ] = None,
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
        query = query.find(
            {"audience": {"$regex": f"^{audience.value}", "$options": "i"}}
        )
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
        .project(SneakerView)
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
