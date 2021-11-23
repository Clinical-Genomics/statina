from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Form, Query, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse

from statina.adapter import StatinaAdapter
from statina.API.v2.endpoints.user import get_current_active_user
from statina.config import get_nipt_adapter
from statina.constants import sample_status_options
from statina.crud import update
from statina.crud.find import samples as find_samples
from statina.crud.find import batches as find_batches
from statina.crud.find.plots import zscore_plot_data
from statina.models.database import DataBaseSample, User, DatabaseBatch
from statina.models.query_params import SamplesQuery
from statina.models.server.plots.ncv import Zscore131821, ZscoreSamples
from statina.models.server.sample import (
    Sample,
    PaginatedSampleResponse,
    SampleValidator,
)

from statina.parse.batch import validate_file_path

router = APIRouter(prefix="/v2")


@router.get("/samples", response_model=PaginatedSampleResponse)
def samples(
    sample_query: SamplesQuery = Depends(SamplesQuery),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get samples"""
    database_samples: List[DataBaseSample] = find_samples.query_samples(
        **sample_query.dict(), adapter=adapter
    )
    validated_samples: List[SampleValidator] = [
        SampleValidator(**sample.dict()) for sample in database_samples
    ]
    samples: List[Sample] = [Sample(**sample.dict()) for sample in validated_samples]

    document_count: int = find_samples.count_query_samples(
        adapter=adapter, batch_id=sample_query.batch_id, query_string=sample_query.query_string
    )
    return JSONResponse(
        content=jsonable_encoder(
            PaginatedSampleResponse(document_count=document_count, documents=samples), by_alias=True
        )
    )


@router.get("/sample/{sample_id}", response_model=Sample)
def sample(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get sample with id"""

    database_sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    batch: DatabaseBatch = find_batches.batch(batch_id=database_sample.batch_id, adapter=adapter)

    if not database_sample:
        return JSONResponse("Not found", status_code=404)

    validated_sample = SampleValidator(**database_sample.dict())
    sample_view_data = Sample(
        sequencing_date=batch.SequencingDate,
        **validated_sample.dict(exclude_none=True),
    )

    return JSONResponse(
        content=jsonable_encoder(
            sample_view_data,
            by_alias=True,
        )
    )


@router.get("/sample/{sample_id}/tris")
def sample_tris(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Sample view with trisomi plot."""

    database_sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    abnormal_data: Dict[str, ZscoreSamples] = zscore_plot_data.get_abn_for_samp_tris_plot(
        adapter=adapter
    )
    normal_data: Zscore131821 = zscore_plot_data.get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data: ZscoreSamples = zscore_plot_data.get_sample_for_samp_tris_plot(database_sample)

    return JSONResponse(
        content=jsonable_encoder(
            dict(
                normal_data=normal_data.dict(exclude_none=True, by_alias=True),
                abnormal_data=abnormal_data,
                sample_data=sample_data,
            ),
            by_alias=False,
        ),
    )


@router.put("/sample/{sample_id}/status/13")
async def set_sample_status_13(
    sample_id: str,
    status: sample_status_options = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.status_13 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_13 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status/18")
async def set_sample_status_18(
    sample_id: str,
    status: sample_status_options = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.status_18 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_18 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status/21")
async def set_sample_status_21(
    sample_id: str,
    status: sample_status_options = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.status_21 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_21 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status/x0")
async def set_sample_status_x0(
    sample_id: str,
    status: sample_status_options = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.status_X0 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_X0 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status/xxy")
async def set_sample_status_xxy(
    sample_id: str,
    status: sample_status_options = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XXY = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XXY = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status/xxx")
async def set_sample_status_xxx(
    sample_id: str,
    status: sample_status_options = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XXX = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XXX = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status/xyy")
async def set_sample_status_xyy(
    sample_id: str,
    status: sample_status_options = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XYY = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XYY = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/comment")
async def sample_comment(
    sample_id: str,
    comment: Optional[str] = Form(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update sample comment"""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.comment = comment
    update.sample(adapter=adapter, sample=sample)

    return JSONResponse(content="Sample comment updated", status_code=200)


@router.put("/sample/{sample_id}/include")
async def sample_include(
    sample_id: str,
    include: bool = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Include sample in plots"""

    sample: DataBaseSample = find_samples.sample(sample_id=sample_id, adapter=adapter)
    sample.include = include
    update.sample(adapter=adapter, sample=sample)

    return JSONResponse(content="Sample inclusion status updated", status_code=200)


@router.get("/sample/{sample_id}/download/segmental_calls")
def sample_segmental_calls_download(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """View for sample downloads"""

    sample: DataBaseSample = find_samples.sample(adapter=adapter, sample_id=sample_id)
    file_path = sample.dict().get("segmental_calls")
    if not validate_file_path(file_path):
        # warn file missing!
        JSONResponse(content="File missing on disk", status_code=404)

    file = Path(file_path)
    response = FileResponse(
        str(file.absolute()), media_type="application/octet-stream", filename=file.name
    )
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response
