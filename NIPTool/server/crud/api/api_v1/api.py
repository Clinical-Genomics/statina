from fastapi import FastAPI

from NIPTool.server.crud.api.api_v1.endpoints import insert


app = FastAPI()

app.include_router(insert.router, prefix="/api/v1/insert", tags=["insert"])
