from celery.result import AsyncResult
from fastapi import APIRouter, Request

from solesearch_api.tasks.scraping.retail.adidas.new_releases import (
    adidas_new_releases_task,
)
from solesearch_api.tasks.scraping.retail.adidas.pdp import adidas_pdp_task
from solesearch_api.tasks.scraping.retail.nike import nike_scraping_task

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


@router.get("/nike")
async def scrape_nike_new_releases(request: Request):
    task = nike_scraping_task.apply_async()
    return task_status_factory(request, task)


@router.get("/adidas")
async def scrape_adidas_new_releases(request: Request):
    task = adidas_new_releases_task.apply_async()
    return task_status_factory(request, task)


@router.get("/adidas/{slug}")
async def scrape_adidas_pdp(request: Request, slug: str):
    task = adidas_pdp_task.apply_async(args=[slug])
    return task_status_factory(request, task)


@router.get("/status/{task_id}")
async def get_scrape_status(request: Request, task_id: str):
    task = AsyncResult(task_id)
    return task_result_factory(request, task)
