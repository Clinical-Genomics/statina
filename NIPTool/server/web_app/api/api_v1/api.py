from fastapi import FastAPI

from NIPTool.server.web_app.api.api_v1.endpoints import batches, index, sample, update, download, statistics, login

app = FastAPI()

app.include_router(login.router, prefix="/api/v1/login", tags=["login"])
app.include_router(batches.router, prefix="/api/v1/batches", tags=["batches"])
app.include_router(index.router, prefix="/api/v1", tags=["index"])
app.include_router(sample.router, prefix="/api/v1", tags=["sample"])
app.include_router(update.router, prefix="/api/v1", tags=["update"])
app.include_router(download.router, prefix="/api/v1", tags=["download"])
app.include_router(statistics.router, prefix="/api/v1", tags=["statistics"])
