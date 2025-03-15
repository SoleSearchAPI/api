from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, Request

from solesearch_api.tasks.scraping import adidas_new_releases_task
from solesearch_api.tasks.scraping import nike_scraping_task
from solesearch_api.tasks.scraping import nike_instock_scraping_task

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


@router.get("/{retailer}")
async def scrape_retailer_new_releases(
    request: Request, retailer: str, nocache: bool = False
):
    task_mapping = {
        "nike": nike_scraping_task,
        "nike_instock": nike_instock_scraping_task,
        "adidas": adidas_new_releases_task,
    }
    if retailer not in task_mapping:
        raise HTTPException(status_code=404, detail="Retailer not found")
    task = task_mapping[retailer].delay(nocache=nocache)
    return task_status_factory(request, task)


@router.get("/status/{task_id}")
async def get_scrape_status(request: Request, task_id: str):
    task = AsyncResult(task_id)
    return task_result_factory(request, task)
