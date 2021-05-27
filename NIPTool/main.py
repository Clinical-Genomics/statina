from fastapi import FastAPI

from NIPTool.API.external.api.api_v1.endpoints import (
    batches,
    download,
    index,
    login,
    new_user,
    sample,
    statistics,
    update,
)
from NIPTool.API.internal.api.api_v1.endpoints import insert

external_app = FastAPI()
external_app.include_router(login.router, prefix="/api/v1/login", tags=["login"])
external_app.include_router(login.router, prefix="/api/v1/new_user", tags=["new_user"])
external_app.include_router(batches.router, prefix="/api/v1/batches", tags=["batches"])
external_app.include_router(index.router, prefix="/api/v1", tags=["index"])
external_app.include_router(sample.router, prefix="/api/v1", tags=["sample"])
external_app.include_router(update.router, prefix="/api/v1", tags=["update"])
external_app.include_router(download.router, prefix="/api/v1", tags=["download"])
external_app.include_router(statistics.router, prefix="/api/v1", tags=["statistics"])

internal_app = FastAPI()
internal_app.include_router(insert.router, prefix="/api/v1/insert", tags=["insert"])
