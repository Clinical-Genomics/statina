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
    external_app = FastAPI(
        servers=[
            {"url": "https://nipttol-stage.scilifelab.se", "description": "Staging environment"}
        ],
        root_path_in_servers=False,
    )

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

    external_app.include_router(external_api_v2.login.router, prefix="v2", tags=["login", "v2"])
    external_app.include_router(
        external_api_v2.batches.router,
        prefix="v2",
        tags=["batches", "v2"],
    )
    external_app.include_router(external_api_v2.sample.router, prefix="v2", tags=["sample", "v2"])
    external_app.include_router(external_api_v2.update.router, prefix="v2", tags=["update", "v2"])
    external_app.include_router(
        external_api_v2.download.router, prefix="v2", tags=["download", "v2"]
    )
    external_app.include_router(
        external_api_v2.statistics.router, prefix="v2", tags=["statistics", "v2"]
    )
    external_app.include_router(external_api_v2.user.router, prefix="v2", tags=["user", "v2"])
    return external_app


def internal(version: str) -> FastAPI:
    internal_app = FastAPI()
    internal_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    internal_app.include_router(external_api_v2.login.router)
    internal_app.include_router(
        external_api_v2.batches.router,
        tags=["batches"],
    )
    internal_app.include_router(external_api_v2.sample.router, tags=["sample"])
    internal_app.include_router(external_api_v2.update.router, tags=["update"])
    internal_app.include_router(external_api_v2.download.router, tags=["download"])
    internal_app.include_router(external_api_v2.statistics.router, tags=["statistics"])
    internal_app.include_router(external_api_v2.user.router, tags=["user"])
    return internal_app


external_app = external("v1")
internal_app = internal("v1")
