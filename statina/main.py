from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from fastapi import Request

from statina.API.external.api.api_v1.endpoints import (
    batches,
    download,
    index,
    login,
    user,
    sample,
    statistics,
    update,
)
from statina.API.internal.api.api_v1.endpoints import insert
from statina.exeptions import CredentialsError

external_app = FastAPI(
    servers=[{"url": "https://nipttol-stage.scilifelab.se", "description": "Staging environment"}],
    root_path_in_servers=False,
)


@external_app.exception_handler(CredentialsError)
async def exception_handler(request: Request, exc: CredentialsError) -> Response:
    return RedirectResponse(url="/")


external_app.include_router(login.router, prefix="/login", tags=["login"])
external_app.include_router(batches.router, prefix="/batches", tags=["batches"])
external_app.include_router(index.router, tags=["index"])
external_app.include_router(sample.router, tags=["sample"])
external_app.include_router(update.router, tags=["update"])
external_app.include_router(download.router, tags=["download"])
external_app.include_router(statistics.router, tags=["statistics"])

internal_app = FastAPI()
internal_app.include_router(insert.router, prefix="/insert", tags=["insert"])
