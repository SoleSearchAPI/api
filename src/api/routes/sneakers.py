import os
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import Session, func, select

from api.db import get_session
from api.models import PaginatedSneakersPublic, Sneaker, SneakerBase, SneakerPublic
from api.models.enums import Audience
from api.models.sorting import SortKey, SortOrder
from api.utils.helpers import url_for_query

router = APIRouter(
    prefix="/sneakers",
)

MAX_LIMIT = int(os.environ.get("SOLESEARCH_MAX_LIMIT", 100))
DEFAULT_LIMIT = int(os.environ.get("SOLESEARCH_DEFAULT_LIMIT", 20))


@router.get("/", response_model=PaginatedSneakersPublic)
async def get_sneakers(
    request: Request,
    db: Session = Depends(get_session),
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
    release_date: Annotated[
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
            description="Filter by whether the shoes have been released or not. Overrides any filter on release_date if set.",
        ),
    ] = None,
    sort: Annotated[
        SortKey, Query(title="Sort By", description="The field to sort by.")
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
            ge=1, title="Page Number", description="The page number of the result set."
        ),
    ] = 1,
    page_size: Annotated[
        int | None,
        Query(
            ge=1,
            le=MAX_LIMIT,
            title="Page Size",
            description=f"The number of items on each page. Must be in the range [1-{MAX_LIMIT}] (inclusive).",
        ),
    ] = DEFAULT_LIMIT,
) -> dict:
    query = select(Sneaker)

    if brand:
        query = query.where(Sneaker.brand.ilike(f"{brand}%"))
    if name:
        query = query.where(Sneaker.name.ilike(f"{name}%"))
    if colorway:
        query = query.where(Sneaker.colorway.ilike(f"{colorway}%"))
    if audience:
        query = query.where(Sneaker.audience == audience)

    if released is not None:
        now = datetime.now(UTC)
        if released:
            query = query.where(Sneaker.release_date <= now)
        else:
            query = query.where(Sneaker.release_date > now)
    elif release_date:
        if ":" in release_date:
            inequality_operator, date_str = release_date.split(":")
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if inequality_operator == "lt":
                query = query.where(Sneaker.release_date < date_obj)
            elif inequality_operator == "lte":
                query = query.where(Sneaker.release_date <= date_obj)
            elif inequality_operator == "gt":
                query = query.where(Sneaker.release_date > date_obj)
            elif inequality_operator == "gte":
                query = query.where(Sneaker.release_date >= date_obj)
        else:
            date_obj = datetime.strptime(release_date, "%Y-%m-%d")
            query = query.where(Sneaker.release_date == date_obj)

    # Count total results
    count_query = select(func.count()).select_from(query.subquery())
    total_count = db.exec(count_query).one()

    # Apply sorting
    if order == SortOrder.ASCENDING:
        query = query.order_by(getattr(Sneaker, sort.value))
    else:
        query = query.order_by(getattr(Sneaker, sort.value).desc())

    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute query
    db_results = db.exec(query).all()

    # Prepare readable results
    results = []
    for db_result in db_results:
        sneaker_public = SneakerPublic(
            id=db_result.id,
            links=db_result.get_links(),
            images=db_result.get_images(),
            sizes=db_result.get_sizes(),
        )
        for key in SneakerBase.model_fields:
            db_value = getattr(db_result, key, None)
            if db_value:
                setattr(sneaker_public, key, db_value)
        results.append(sneaker_public)

    # Prepare pagination links
    params = dict(request.query_params)
    if total_count > page * page_size:
        params["page"] = page + 1
        next_page = url_for_query(request, "get_sneakers", **params)
    else:
        next_page = None
    if page > 1:
        params["page"] = page - 1
        previous_page = url_for_query(request, "get_sneakers", **params)
    else:
        previous_page = None

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "next_page": next_page,
        "previous_page": previous_page,
        "items": results,
    }


@router.get("/{product_id}", response_model=SneakerPublic)
async def get_sneaker_by_id(*, db: Session = Depends(get_session), product_id: int):
    sneaker = db.get(Sneaker, product_id)
    if not sneaker:
        raise HTTPException(status_code=404, detail="Sneaker not found")
    return sneaker


@router.get("/sku/{sku}", response_model=SneakerPublic)
async def get_sneaker_by_sku(
    *, db: Session = Depends(get_session), sku: str, brand: str | None = None
):
    query = select(Sneaker).where(Sneaker.sku == sku)
    if brand:
        query = query.where(Sneaker.brand == brand)
    sneaker = db.exec(query).first()
    if not sneaker:
        raise HTTPException(status_code=404, detail="Sneaker not found")
    return sneaker
