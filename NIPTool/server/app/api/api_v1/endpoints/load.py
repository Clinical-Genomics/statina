from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, requests
from NIPTool.load.batch import load_batch, load_samples
from NIPTool.parse.batch import get_samples, get_batch
from NIPTool.adapter.plugin import NiptAdapter

from NIPTool.load.user import load_user
from NIPTool.schemas.batch import Batch, InBatch
from NIPTool.schemas.sample import Sample
from NIPTool.server.app.api.deps import get_nipt_adapter
from NIPTool.server.app import schemas
from NIPTool.exeptions import NIPToolError, MissingResultsError

router = APIRouter()


@router.post("/batch")
def batch(batch_files: InBatch, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Function to load batch data into the database with rest"""
    nipt_results = Path(batch_files.result_file)

    if not nipt_results.exists():
        return {"message": "Results file missing.", "status_code": 422}
    samples: List[Sample] = get_samples(nipt_results)
    batch: Batch = get_batch(nipt_results)
    batch.result_file = batch_files.result_file
    if batch_files.multiqc_report:
        if not Path(batch_files.multiqc_report).exists():
            return {"message": "MultiQC file does not exist.", "status_code": 422}
        batch.multiqc_report = batch_files.multiqc_report
    if batch_files.segmental_calls:
        if not Path(batch_files.segmental_calls).exists():
            return {"message": "Segmental calls file does not exist.", "status_code": 422}
        batch.segmental_calls = batch_files.segmental_calls

    try:
        load_batch(adapter=adapter, batch_id=samples[0].SampleProject, batch=batch)
        load_samples(adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls)
    except NIPToolError as e:
        return {"message": e.message, "status_code": 422}

    message = "Data loaded into database"
    return {"message": message, "status_code": 200}


@router.post("/user")
def user(user: schemas.User, adapter: NiptAdapter = Depends(get_nipt_adapter)):
    """Function to load user into the database with rest"""

    try:
        load_user(adapter, user.email, user.name, user.role)
    except NIPToolError as e:
        return {"message": e.message, "status_code": 422}

    message = "Data loaded into database"
    return {"message": message, "status_code": 200}
