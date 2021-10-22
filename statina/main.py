from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from statina.exeptions import CredentialsError

import statina.API.external.api.api_v1.endpoints as external_api_v1
import statina.API.internal.api.api_v1.endpoints as internal_api_v1
import statina.API.v2.endpoints as external_api_v2

external_versions = {"v1": external_api_v1}
internal_versions = {"v1": internal_api_v1}


def external(version: str) -> FastAPI:
    api = external_versions[version]
    external_app = FastAPI()

    @external_app.exception_handler(CredentialsError)
    async def exception_handler(request: Request, exc: CredentialsError) -> Response:
        return RedirectResponse(url="/")

    external_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    external_app.include_router(external_api_v2.base.router, tags=["base_v2"])
    external_app.include_router(external_api_v2.batches.router, tags=["batches_v2"])
    external_app.include_router(external_api_v2.sample.router, tags=["sample_v2"])
    external_app.include_router(external_api_v2.statistics.router, tags=["statistics_v2"])
    external_app.include_router(external_api_v2.user.router, tags=["user_v2"])
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
    return internal_app


external_app = external("v1")
internal_app = internal("v1")
