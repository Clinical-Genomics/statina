from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, Response, status

from statina.API.v2.endpoints.login import get_current_active_user
from statina.adapter.plugin import StatinaAdapter
from statina.config import get_nipt_adapter
from statina.crud.find import find
from statina.crud.insert import insert_batch, insert_samples
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.load import BatchRequestBody
from statina.parse.batch import get_batch, get_samples

router = APIRouter()


@router.post("/batch")
def batch(
    response: Response,
    batch_files: BatchRequestBody,
    current_user: User = Depends(get_current_active_user),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Function to load batch data into the database with rest"""
    nipt_results = Path(batch_files.result_file)
    if not nipt_results.exists():
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "Results file missing."}
    samples: List[DataBaseSample] = get_samples(nipt_results)
    batch: Batch = get_batch(nipt_results)
    if find.batch(adapter=adapter, batch_id=batch.batch_id):
        return "batch already in database"

    insert_batch(adapter=adapter, batch=batch, batch_files=batch_files)
    insert_samples(adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls)

    response.status_code = status.HTTP_200_OK
    return {"message": f"Batch {batch.batch_id} inserted to the database"}
