from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, RedirectResponse
from starlette.requests import Request
from starlette.responses import StreamingResponse

from statina.API.external.constants import COLORS
from statina.adapter.plugin import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.config import get_nipt_adapter, templates
from statina.crud.find import find
from statina.crud.find.plots import fetal_fraction_plot_data as get_fetal_fraction
from statina.models.server.plots.fetal_fraction import (
    FetalFractionSamples,
    FetalFractionControlAbNormal,
)
from statina.models.server.plots.fetal_fraction_sex import SexChromosomeThresholds
from statina.models.server.sample import Sample
from zipfile import ZIP_DEFLATED, ZipFile
import io
from os import PathLike
from typing import Union, List
from statina.models.database import DataBaseSample, User, Batch
from statina.parse.batch import validate_file_path

router = APIRouter()
user = {}


def zip_dir(source_dir: Union[str, PathLike]) -> io.BytesIO:
    """Function for zipping"""
    src_path = Path(source_dir).expanduser().resolve(strict=True)
    file_obj = io.BytesIO()
    file_obj.seek(0)
    with ZipFile(file=file_obj, mode="a", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for file in src_path.iterdir():
            zf.write(filename=file.as_posix(), arcname=file.name)
    file_obj.seek(0)
    return file_obj


@router.get("/batch_download/{batch_id}/{file_id}/{file_name}")
def batch_download(
    request: Request,
    batch_id: str,
    file_id: str,
    file_name: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """View for batch downloads"""
    batch: dict = find.batch(adapter=adapter, batch_id=batch_id).dict()
    file_path = batch.get(file_id)
    if not validate_file_path(file_path):
        return RedirectResponse(request.headers.get("referer"))

    path = Path(file_path)
    if path.is_dir():
        file_obj = zip_dir(source_dir=file_path)
        return StreamingResponse(file_obj, media_type="application/text")

    return FileResponse(
        str(path.absolute()), media_type="application/octet-stream", filename=path.name
    )


@router.get("/sample_download/{sample_id}/{file_id}")
def sample_download(
    request: Request,
    sample_id: str,
    file_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """View for sample downloads"""

    sample: DataBaseSample = find.sample(adapter=adapter, sample_id=sample_id)
    file_path = sample.dict().get(file_id)
    if not validate_file_path(file_path):
        # warn file missing!
        return RedirectResponse(request.headers.get("referer"))

    file = Path(file_path)
    return FileResponse(
        str(file.absolute()), media_type="application/octet-stream", filename=file.name
    )


@router.get("/batches/{batch_id}/report/{file_name}")
def report(
    request: Request,
    batch_id: str,
    file_name: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
):
    """Report view, collecting all tables and plots from one batch."""

    samples: List[DataBaseSample] = find.batch_samples(batch_id=batch_id, adapter=adapter)
    batch: Batch = find.batch(batch_id=batch_id, adapter=adapter)

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

    template = templates.get_template("batch/report.html")
    output_from_parsed_template = template.render(
        # common
        request=request,
        current_user=user,
        batch=find.batch(batch_id=batch_id, adapter=adapter),
        # Fetal Fraction  XY
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
        colors=COLORS,
        max_x=x_max,
        min_x=x_min,
        # table
        sample_info=[Sample(**sample.dict()) for sample in samples],
    )

    in_mem_file = io.StringIO()
    in_mem_file.seek(0)

    in_mem_file.write(output_from_parsed_template)
    in_mem_file.seek(0)
    return StreamingResponse(in_mem_file, media_type="application/text")
