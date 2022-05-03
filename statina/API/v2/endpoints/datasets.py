import logging
from typing import List

from fastapi import APIRouter, Security, Depends
from pymongo.errors import DuplicateKeyError
from starlette import status
from starlette.responses import JSONResponse

from statina.API.v2.endpoints.user import get_current_active_user
from statina.adapter import StatinaAdapter
from statina.config import get_nipt_adapter
from statina.crud.find.datasets import query_datasets, get_dataset
from statina.models.database import User
from statina.models.database.dataset import Dataset
from statina.models.query_params import DatasetsQuery
from statina.models.server.dataset import DatasetForm

LOG = logging.getLogger(__name__)
router = APIRouter(prefix="/v2")


@router.get("/datasets", response_model=List[Dataset])
def get_datasets(
    query: DatasetsQuery = Depends(DatasetsQuery),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
):
    """Get datasets"""

    return query_datasets(adapter=adapter, **query.dict())


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


@router.get("/dataset", response_model=Dataset)
def get_dataset(
    name: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
):
    """Get dataset by name"""

    return get_dataset(adapter=adapter, name=name)


@router.post("/dataset", response_model=Dataset)
def create_dataset(
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    dataset_form: DatasetForm = Depends(DatasetForm.as_form),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Get dataset by name"""
    try:
        adapter.dataset_collection.insert_one(dataset_form.dict())
    except DuplicateKeyError:
        return JSONResponse(
            f"Dataset with name '{dataset_form.name}' already exists",
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
