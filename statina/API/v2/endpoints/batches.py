from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, Form, Query, Security, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

import statina.crud.find.plots.fetal_fraction_plot_data as get_fetal_fraction
from statina.adapter import StatinaAdapter
from statina.API.external.constants import TRISOMI_TRESHOLDS
from statina.API.v2.endpoints.user import get_current_active_user
from statina.config import get_nipt_adapter
from statina.crud import update
from statina.crud.delete import delete_batch
from statina.crud.find import find
from statina.crud.find.plots.coverage_plot_data import (
    get_box_data_for_coverage_plot,
    get_scatter_data_for_coverage_plot,
)
from statina.crud.find.plots.zscore_plot_data import (
    get_tris_control_abnormal,
    get_tris_control_normal,
    get_tris_samples,
)
from statina.crud.insert import insert_batch, insert_samples
from statina.crud.utils import zip_dir
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.batch import PaginatedBatchResponse
from statina.models.server.load import BatchRequestBody
from statina.models.server.plots.coverage import CoveragePlotSampleData
from statina.models.server.plots.fetal_fraction import (
    FetalFractionControlAbNormal,
    FetalFractionSamples,
)
from statina.models.server.plots.fetal_fraction_sex import SexChromosomeThresholds
from statina.models.server.sample import Sample, PaginatedSampleResponse
from statina.parse.batch import get_batch, get_samples, validate_file_path

router = APIRouter(prefix="/v2")


@router.get("/batches", response_model=PaginatedBatchResponse)
def batches(
    page_size: Optional[int] = Query(5),
    page_num: Optional[int] = Query(0),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """List of all batches"""
    batches: List[Batch] = find.batches(adapter=adapter, page_size=page_size, page_num=page_num)
    document_count = find.count_batches(adapter=adapter)
    return JSONResponse(
        content=jsonable_encoder(
            PaginatedBatchResponse(document_count=document_count, documents=batches),
            by_alias=False,
        )
    )


@router.delete("/batch/{batch_id}")
async def batch_delete(
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
):
    await delete_batch(adapter=adapter, batch_id=batch_id)
    return JSONResponse(content=f"Deleted batch {batch_id}", status_code=200)


@router.post("/batch", response_model=Batch)
def load_batch(
    batch_files: BatchRequestBody,
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Function to load batch data into the database with rest"""
    nipt_results = Path(batch_files.result_file)
    if not nipt_results.exists():
        return JSONResponse(content="Results file missing", status_code=422)
    samples: List[DataBaseSample] = get_samples(nipt_results)
    batch: Batch = get_batch(nipt_results)
    if find.batch(adapter=adapter, batch_id=batch.batch_id):
        return JSONResponse(content="Batch already in database!", status_code=422)
    insert_batch(adapter=adapter, batch=batch, batch_files=batch_files)
    insert_samples(adapter=adapter, samples=samples, segmental_calls=batch_files.segmental_calls)
    inserted_batch = find.batch(adapter=adapter, batch_id=batch.batch_id)
    return JSONResponse(content=jsonable_encoder(inserted_batch, by_alias=False), status_code=200)


@router.get("/batch/{batch_id}", response_model=Batch)
def get_batch(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with table of all samples in the batch."""
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    if not batch:
        return JSONResponse("Not found", 404)

    return JSONResponse(
        jsonable_encoder(batch, by_alias=False),
        status_code=200,
    )


@router.get("/batch/{batch_id}/samples", response_model=PaginatedSampleResponse)
def batch_samples(
    batch_id: str,
    page_size: Optional[int] = Query(5),
    page_num: Optional[int] = Query(0),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with table of all samples in the batch."""
    samples = find.batch_samples(
        batch_id=batch_id, adapter=adapter, page_size=page_size, page_num=page_num
    )
    validated_samples: List[Sample] = [Sample(**sample_obj.dict()) for sample_obj in samples]
    document_count: int = find.count_batch_samples(adapter=adapter, batch_id=batch_id)
    return JSONResponse(
        content=jsonable_encoder(
            PaginatedSampleResponse(document_count=document_count, documents=validated_samples),
            by_alias=False,
        ),
        status_code=200,
    )


@router.get("/batch/{batch_id}/download/{file_id}")
def batch_download(
    batch_id: str,
    file_id: Literal["result_file", "multiqc_report", "segmental_calls"],
    file_name: Optional[str] = Query(...),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Download files, media type application/text or application/octet-stream"""
    batch: dict = find.batch(adapter=adapter, batch_id=batch_id).dict()
    file_path = batch.get(file_id)
    if not validate_file_path(file_path):
        return JSONResponse(content="File not found", status_code=404)

    path = Path(file_path)
    if path.is_dir():
        file_obj = zip_dir(source_dir=file_path)
        response = StreamingResponse(file_obj, media_type="application/octet-stream")
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        return response

    return FileResponse(
        str(path.absolute()),
        media_type="application/octet-stream",
        filename=file_name or path.name,
    )


@router.get("/batch/{batch_id}/zscore_plot")
def zscore_plot(
    batch_id: str,
    ncv: Literal["13", "18", "21"] = Query(...),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with with Zscore plot"""

    return JSONResponse(
        content=jsonable_encoder(
            dict(
                tris_thresholds=TRISOMI_TRESHOLDS,
                chromosomes=[ncv],
                ncv_chrom_data={ncv: get_tris_samples(adapter=adapter, chr=ncv, batch_id=batch_id)},
                normal_data={ncv: get_tris_control_normal(adapter, ncv)},
                abnormal_data={ncv: get_tris_control_abnormal(adapter, ncv, 0)},
            ),
            by_alias=False,
        ),
    )


@router.get("/batch/{batch_id}/fetal_fraction_XY")
def fetal_fraction_XY(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with fetal fraction (X against Y) plot"""

    cases = get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id)
    control: FetalFractionSamples = get_fetal_fraction.samples(
        batch_id=batch_id, adapter=adapter, control_samples=True
    )
    abnormal: FetalFractionControlAbNormal = get_fetal_fraction.control_abnormal(adapter)
    abnormal_dict = abnormal.dict(
        exclude_none=True,
        exclude={
            "X0": {"status_data_"},
            "XXX": {"status_data_"},
            "XXY": {"status_data_"},
            "XYY": {"status_data_"},
        },
    )

    x_max = max(control.FFX + cases.FFX) + 1
    x_min = min(control.FFX + cases.FFX) - 1

    sex_thresholds = SexChromosomeThresholds(x_min=x_min, x_max=x_max)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                sex_thresholds={
                    "XY_fetal_fraction_y": sex_thresholds.XY_fetal_fraction_y(),
                    "XX_lower": sex_thresholds.XX_lower(),
                    "XX_upper": sex_thresholds.XX_upper(),
                    "XY_upper": sex_thresholds.XY_upper(),
                    "XY_lower": sex_thresholds.XY_lower(),
                    "XXY": sex_thresholds.XXY(),
                },
                control=control,
                abnormal=abnormal_dict,
                cases=cases,
                max_x=x_max,
                min_x=x_min,
            ),
            by_alias=False,
        ),
    )


@router.get("/batch/{batch_id}/fetal_fraction")
def fetal_fraction(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with fetal fraction plot"""
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                control=get_fetal_fraction.samples(
                    adapter=adapter, batch_id=batch_id, control_samples=True
                ),
                cases=get_fetal_fraction.samples(adapter=adapter, batch_id=batch_id),
            ),
            by_alias=False,
        ),
    )


@router.get("/batch/{batch_id}/coverage")
def coverage(
    batch_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Batch view with coverage plot"""
    db_samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    samples: List[Sample] = [Sample(**db_sample.dict()) for db_sample in db_samples]

    scatter_data: Dict[str, CoveragePlotSampleData] = get_scatter_data_for_coverage_plot(samples)
    box_data: Dict[int, List[float]] = get_box_data_for_coverage_plot(samples)
    return JSONResponse(
        content=jsonable_encoder(
            dict(
                x_axis=list(range(1, 23)),
                scatter_data=scatter_data,
                box_data=box_data,
            ),
            by_alias=False,
        ),
    )


@router.put("/batch/{batch_id}/comment")
async def batch_update_comment(
    batch_id: str,
    comment: Optional[str] = Form(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update batch comment"""

    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)
    batch.comment = comment
    update.update_batch(adapter=adapter, batch=batch)

    return JSONResponse(content="Batch comment updated", status_code=202)


@router.patch("/batch/{batch_id}/include_samples")
async def include_samples(
    batch_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update include status and comment for samples in batch"""
    samples: List[DataBaseSample] = find.batch_samples(adapter=adapter, batch_id=batch_id)
    for sample in samples:
        sample.include = True
        sample.change_include_date = (
            f'{current_user.username} {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}'
        )
        update.sample(adapter=adapter, sample=sample)

    return JSONResponse(content="All samples included in batch plots", status_code=200)
