from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, status, Response
from NIPTool.load.batch import load_batch, load_samples
from NIPTool.parse.batch import get_samples, get_batch
from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.load.user import load_user
from NIPTool.schemas import db_models
from NIPTool.schemas.server import load
from NIPTool.server.load.api.deps import get_nipt_adapter
from NIPTool.exeptions import NIPToolError


router = APIRouter()


@router.post("/batch")
def batch(
    response: Response,
    batch_files: load.BatchLoadModel,
    adapter: NiptAdapter = Depends(get_nipt_adapter),
):
    """Function to load batch data into the database with rest"""

    nipt_results = Path(batch_files.result_file)
    if not nipt_results.exists():
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "Results file missing."}
    samples: List[db_models.SampleModel] = get_samples(nipt_results)
    batch: db_models.BatchModel = get_batch(nipt_results)
    try:
        load_batch(adapter=adapter, batch=batch, batch_files=batch_files)
        load_samples(adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls)
    except NIPToolError as e:
        return {"message": e.message, "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY}
    message = "Data loaded into database"
    response.status_code = status.HTTP_200_OK
    return {"message": message}


@router.post("/user")
def user(
    response: Response, user: load.UserLoadModel, adapter: NiptAdapter = Depends(get_nipt_adapter)
):
    """Function to load user into the database with rest"""

    try:
        load_user(adapter, user)
    except NIPToolError as e:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": e.message}

    message = "Data loaded into database"
    response.status_code = status.HTTP_200_OK
    return {"message": message}
