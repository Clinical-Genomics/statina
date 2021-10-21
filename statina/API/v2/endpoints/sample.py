import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, Form, Query, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse

from statina.adapter import StatinaAdapter
from statina.API.v2.endpoints.user import get_current_active_user
from statina.config import get_nipt_adapter
from statina.crud import update
from statina.crud.find import find
from statina.crud.find.plots.zscore_plot_data import (
    get_abn_for_samp_tris_plot,
    get_normal_for_samp_tris_plot,
    get_sample_for_samp_tris_plot,
)
from statina.models.database import Batch, DataBaseSample, User
from statina.models.server.plots.ncv import Zscore131821, ZscoreSamples
from statina.models.server.sample import Sample
from statina.parse.batch import validate_file_path

router = APIRouter(prefix="/v2")


@router.get("/samples/", response_model=List[Sample])
def samples(
    page_size: Optional[int] = Query(5),
    page_num: Optional[int] = Query(0),
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get samples"""
    samples: List[DataBaseSample] = find.samples(
        adapter=adapter, page_size=page_size, page_num=page_num
    )
    validated_samples: List[Sample] = [Sample(**sample_obj.dict()) for sample_obj in samples]
    return JSONResponse(
        content=jsonable_encoder(
            validated_samples,
            by_alias=False,
        )
    )


@router.get("/sample/{sample_id}", response_model=Sample)
def sample(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Get sample with id"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    validated_sample: Sample = Sample(**sample.dict())

    return JSONResponse(
        content=jsonable_encoder(
            validated_sample,
            by_alias=False,
        )
    )


@router.get("/sample/{sample_id}/tris")
def sample_tris(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Sample view with trisomi plot."""
    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=sample.batch_id, adapter=adapter)
    abnormal_data: Dict[str, ZscoreSamples] = get_abn_for_samp_tris_plot(adapter=adapter)
    normal_data: Zscore131821 = get_normal_for_samp_tris_plot(adapter=adapter)
    sample_data: ZscoreSamples = get_sample_for_samp_tris_plot(sample)
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


@router.put("/sample/{sample_id}/status_13")
async def set_sample_status_13(
    sample_id: str,
    status: Literal[
        "Normal",
        "False Positive",
        "Suspected",
        "Verified",
        "Probable",
        "False Negative",
        "Other",
        "Failed",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_13 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_13 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status_18")
async def set_sample_status_18(
    sample_id: str,
    status: Literal[
        "Normal",
        "False Positive",
        "Suspected",
        "Verified",
        "Probable",
        "False Negative",
        "Other",
        "Failed",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_18 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_18 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status_21")
async def set_sample_status_21(
    sample_id: str,
    status: Literal[
        "Normal",
        "False Positive",
        "Suspected",
        "Verified",
        "Probable",
        "False Negative",
        "Other",
        "Failed",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_21 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_21 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status_X0")
async def set_sample_status_x0(
    sample_id: str,
    status: Literal[
        "Normal",
        "False Positive",
        "Suspected",
        "Verified",
        "Probable",
        "False Negative",
        "Other",
        "Failed",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_X0 = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_X0 = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status_XXY")
async def set_sample_status_xxy(
    sample_id: str,
    status: Literal[
        "Normal",
        "False Positive",
        "Suspected",
        "Verified",
        "Probable",
        "False Negative",
        "Other",
        "Failed",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XXY = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XXY = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status_XXX")
async def set_sample_status_xxx(
    sample_id: str,
    status: Literal[
        "Normal",
        "False Positive",
        "Suspected",
        "Verified",
        "Probable",
        "False Negative",
        "Other",
        "Failed",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.status_XXX = status
    time_stamp: str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sample.status_change_XXX = f"{current_user.username} {time_stamp}"
    update.sample(adapter=adapter, sample=sample)
    return JSONResponse(content="Sample field updated", status_code=200)


@router.put("/sample/{sample_id}/status_XYY")
async def set_sample_status_xyy(
    sample_id: str,
    status: Literal[
        "Normal",
        "False Positive",
        "Suspected",
        "Verified",
        "Probable",
        "False Negative",
        "Other",
        "Failed",
    ] = Query(...),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    current_user: User = Security(get_current_active_user, scopes=["RW"]),
):
    """Update the manualy interpreted chromosome abnormality status for a sample."""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
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

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
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
    """Update sample comment"""

    sample: DataBaseSample = find.sample(sample_id=sample_id, adapter=adapter)
    sample.include = include
    update.sample(adapter=adapter, sample=sample)

    return JSONResponse(content="Sample comment updated", status_code=200)


@router.get("/sample/{sample_id}/download/segmental_calls")
def sample_segmental_calls_download(
    sample_id: str,
    current_user: User = Security(get_current_active_user, scopes=["R"]),
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """View for sample downloads"""

    sample: DataBaseSample = find.sample(adapter=adapter, sample_id=sample_id)
    file_path = sample.dict().get("segmental_calls")
    if not validate_file_path(file_path):
        # warn file missing!
        JSONResponse(content="File missing on disk", status_code=404)

    file = Path(file_path)
    return FileResponse(
        str(file.absolute()), media_type="application/octet-stream", filename=file.name
    )
