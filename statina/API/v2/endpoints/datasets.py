import logging
from typing import List

from fastapi import APIRouter, Security, Depends
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError
from starlette import status
from starlette.responses import JSONResponse

from statina.API.v2.endpoints.user import get_current_active_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter
from statina.crud.find.datasets import query_datasets, count_query_datasets
from statina.models.database import User
from statina.models.database.dataset import Dataset
from statina.models.query_params import DatasetsQuery
from statina.models.server.dataset import DatasetForm, PaginatedDatasetResponse

LOG = logging.getLogger(__name__)
router = APIRouter(prefix="/v2")


@router.get("/datasets", response_model=List[PaginatedDatasetResponse])
def get_datasets(
    query: DatasetsQuery = Depends(DatasetsQuery),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
):
    """Get datasets"""

    return JSONResponse(
        content=jsonable_encoder(
            PaginatedDatasetResponse(
                document_count=count_query_datasets(
                    adapter=adapter, query_string=query.query_string
                ),
                documents=query_datasets(adapter=adapter, **query.dict()),
            ),
            by_alias=True,
        )
    )


@router.get("/dataset_options", response_model=List)
def list_datasets(
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
):
    """Get dataset names"""
    return [
        dataset.get("name")
        for dataset in adapter.dataset_collection.find({}, {"name": 1, "_id": 0})
    ]


@router.get("/dataset/{name}", response_model=Dataset)
def get_dataset_by_name(
    name: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
):
    """Get dataset by name"""

    return adapter.dataset_collection.find_one({"name": name})


@router.post("/dataset/{name}", response_model=Dataset)
def create_dataset(
    name: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    dataset_form: DatasetForm = Depends(DatasetForm.as_form),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Get dataset by name"""
    try:
        dataset_form.name = name
        adapter.dataset_collection.insert_one(dataset_form.dict())
    except DuplicateKeyError:
        return JSONResponse(
            f"Dataset with name '{name}' already exists",
            status_code=status.HTTP_409_CONFLICT,
        )
    return dataset_form


@router.delete("/dataset/{name}", response_model=Dataset)
def delete_dataset(
    name: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Get dataset by name"""
    if name == "default":
        return JSONResponse(
            "Not allowed to remove the default dataset", status_code=status.HTTP_406_NOT_ACCEPTABLE
        )
    dataset = adapter.dataset_collection.find({"name": name})
    if not dataset:
        return JSONResponse(
            f"Dataset with name '{name}' does not exist", status_code=status.HTTP_400_BAD_REQUEST
        )
    adapter.dataset_collection.delete_one({"name": name})
    adapter.batch_collection.update_many({"dataset": name}, {"$set": {"dataset": "default"}})
    return JSONResponse(
        f"Dataset with name '{name}' deleted successfully", status_code=status.HTTP_200_OK
    )


@router.patch("/dataset/{name}", response_model=Dataset)
def update_dataset(
    name: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    dataset_form: DatasetForm = Depends(DatasetForm.as_form),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update dataset"""
    adapter.dataset_collection.update_one({"name": name}, {"$set": dataset_form.dict()})
    return adapter.dataset_collection.find_one({"name": name})
