from fastapi import APIRouter, Request

from solesearch_api.tasks.ingest.retail.adidas import adidas_ingest
from solesearch_api.tasks.ingest.retail.nike import nike_ingest
from celery.result import AsyncResult

router = APIRouter(
    prefix="/triggers",
)


@router.get("/nike")
async def trigger_nike_ingest(request: Request):
    task = nike_ingest.apply_async()
    return {
        "task_id": task.id,
        "status": task.status,
        "status_link": f"{request.base_url}triggers/status/{task.id}",
    }


@router.get("/adidas")
async def trigger_adidas_ingest(request: Request):
    task = adidas_ingest.apply_async()
    return {
        "task_id": task.id,
        "status": task.status,
        "status_link": f"{request.base_url}triggers/status/{task.id}",
    }


@router.get("/status/{task_id}")
async def get_ingest_status(task_id: str):
    task = AsyncResult(task_id)
    return {"task_id": task.id, "status": task.status, "result": task.result}
