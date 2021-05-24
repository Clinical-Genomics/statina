from fastapi import FastAPI

from NIPTool.API.external.api.api_v1.endpoints import (
    batches,
    download,
    index,
    login,
    sample,
    statistics,
    update,
)
from NIPTool.API.internal.api.api_v1.endpoints import insert

external_app = FastAPI(
    servers=[
        {"url": "https://nipttool-stage.scilifelab.se", "description": "Staging environment"},
        {"url": "https://nipttool.scilifelab.se", "description": "Production environment"},
    ],
    root_path="/api/v1",
    root_path_in_servers=False,
)
external_app.include_router(login.router, prefix="/login", tags=["login"])
external_app.include_router(batches.router, prefix="/batches", tags=["batches"])
external_app.include_router(index.router, tags=["index"])
external_app.include_router(sample.router, tags=["sample"])
external_app.include_router(update.router, tags=["update"])
external_app.include_router(download.router, tags=["download"])
external_app.include_router(statistics.router, tags=["statistics"])

internal_app = FastAPI(root_path="/api/v1")
internal_app.include_router(insert.router, prefix="/insert", tags=["insert"])
