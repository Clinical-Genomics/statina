from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends
from NIPTool.load.batch import load_batch, load_samples
from NIPTool.parse.batch import get_samples, get_batch
from NIPTool.adapter.plugin import NiptAdapter

from NIPTool.load.user import load_user
from NIPTool.schemas import db_models
from NIPTool.schemas.server import load

from NIPTool.server.app.api.deps import get_nipt_adapter
from NIPTool.exeptions import NIPToolError

router = APIRouter()


@router.post("/batch")
def batch(batch_files: load.BatchLoadModel, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Function to load batch data into the database with rest"""

    nipt_results = Path(batch_files.result_file)

    if not nipt_results.exists():
        return {"message": "Results file missing.", "status_code": 422}
    samples: List[db_models.SampleModel] = get_samples(nipt_results)
    batch: db_models.BatchModel = get_batch(nipt_results)

    try:
        load_batch(adapter=adapter, batch=batch, batch_files=batch_files)
        load_samples(adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls)
    except NIPToolError as e:
        return {"message": e.message, "status_code": 422}

    message = "Data loaded into database"
    return {"message": message, "status_code": 200}


@router.post("/user")
def user(user: load.UserLoadModel, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Function to load user into the database with rest"""

    try:
        load_user(adapter, user.email, user.name, user.role)
    except NIPToolError as e:
        return {"message": e.message, "status_code": 422}

    message = "Data loaded into database"
    return {"message": message, "status_code": 200}
