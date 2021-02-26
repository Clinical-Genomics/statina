from fastapi import FastAPI

from NIPTool.server.app.api.api_v1.endpoints import load


app = FastAPI()

app.include_router(load.router, prefix="/api/v1/load", tags=["load"])
