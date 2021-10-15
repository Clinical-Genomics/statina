from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from statina.exeptions import CredentialsError

import statina.API.external.api.api_v1.endpoints as external_api_v1
import statina.API.internal.api.api_v1.endpoints as internal_api_v1

external_versions = {"v1": external_api_v1}
internal_versions = {"v1": internal_api_v1}


def external(version: str) -> FastAPI:
    api = external_versions[version]
    external_app = FastAPI()

    @external_app.exception_handler(CredentialsError)
    async def exception_handler(request: Request, exc: CredentialsError) -> Response:
        return RedirectResponse(url="/")

    external_app.include_router(api.login.router, prefix="/login", tags=["login"])
    external_app.include_router(
        api.batches.router,
        prefix="/batches",
        tags=["batches"],
    )
    external_app.include_router(api.index.router, tags=["index"])
    external_app.include_router(api.sample.router, tags=["sample"])
    external_app.include_router(api.update.router, tags=["update"])
    external_app.include_router(api.download.router, tags=["download"])
    external_app.include_router(api.statistics.router, tags=["statistics"])
    return external_app


def internal(version: str) -> FastAPI:
    api = internal_versions[version]
    internal_app = FastAPI()
    internal_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    internal_app.include_router(api.insert.router, prefix="/insert", tags=["insert"])
    internal_app.include_router(api.login.router, prefix="/login", tags=["login"])
    internal_app.include_router(
        api.batches.router,
        prefix="/batches",
        tags=["batches"],
    )
    internal_app.include_router(api.index.router, tags=["index"])
    internal_app.include_router(api.sample.router, tags=["sample"])
    internal_app.include_router(api.update.router, tags=["update"])
    internal_app.include_router(api.download.router, tags=["download"])
    internal_app.include_router(api.statistics.router, tags=["statistics"])
    return internal_app


external_app = external("v1")
internal_app = internal("v1")
