from fastapi import FastAPI
from mangum import Mangum

from src.api.routes import sneakers

app = FastAPI(
    responses={404: {"resource": "Not found"}},
)


@app.get("/ping")
async def ping():
    return {"alive": True}


app.include_router(sneakers.router)

handler = Mangum(app)