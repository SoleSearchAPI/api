from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Request

from solesearch_api.tasks.scraping import (
    adidas_baby_and_toddler_task,
    adidas_children_and_little_kids_task,
    adidas_youth_and_big_kids_task,
    adidas_new_releases_task,
    adidas_mens_sneakers_task,
    adidas_womens_sneakers_task,
    nike_in_stock_scraping_task,
    nike_new_releases_task,
)

router = APIRouter(
    prefix="/scrape",
)


def task_status_factory(request: Request, task: AsyncResult):
    return {
        "task_id": task.id,
        "status": task.status,
        "status_link": str(request.url_for("get_scrape_status", task_id=task.id)),
    }


def task_result_factory(request: Request, task: AsyncResult):
    task_status = task_status_factory(request, task)
    return {
        **task_status,
        "result": task.result,
    }


@router.get("/{task_name:path}")
async def scrape_retailer_new_releases(
    request: Request, task_name: str, nocache: bool = False
):

    task_mapping = {
        "nike": nike_new_releases_task,
        "nike/in_stock": nike_in_stock_scraping_task,
        "adidas": adidas_new_releases_task,
        "adidas/baby": adidas_baby_and_toddler_task,
        "adidas/children": adidas_children_and_little_kids_task,
        "adidas/youth": adidas_youth_and_big_kids_task,
        "adidas/womens": adidas_womens_sneakers_task,
        "adidas/mens": adidas_mens_sneakers_task,
    }
    if task_name not in task_mapping:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_mapping[task_name].delay(nocache=nocache)
    return task_status_factory(request, task)


@router.get("/status/{task_id}")
async def get_scrape_status(request: Request, task_id: str):
    task = AsyncResult(task_id)
    return task_result_factory(request, task)
