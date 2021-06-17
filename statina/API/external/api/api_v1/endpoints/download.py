from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse

from statina.adapter.plugin import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.config import get_nipt_adapter
from statina.crud.find import find
from statina.models.database import User, DataBaseSample
from statina.parse.batch import validate_file_path
from zipfile import ZIP_DEFLATED, ZipFile
from os import PathLike
from typing import Union, Optional

router = APIRouter()


# def zip_dir(zip_name: str, source_dir: Union[str, PathLike], suffix: Optional[str] = None):
# """Function for zipping"""
# src_path = Path(source_dir).expanduser().resolve(strict=True)
# with ZipFile(zip_name, "w", ZIP_DEFLATED) as zf:
#    for file in src_path.rglob("*"):
#        if suffix and file.suffix != suffix:
#            continue
#        zf.write(file, file.relative_to(src_path.parent))


@router.get("/batch_download/{batch_id}/{file_id}")
def batch_download(
    request: Request,
    batch_id: str,
    file_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
):
    """View for batch downloads"""
    batch: dict = find.batch(adapter=adapter, batch_id=batch_id).dict()
    file_path = batch.get(file_id)
    if not validate_file_path(file_path):
        return RedirectResponse(request.headers.get("referer"))

    path = Path(file_path)
    if path.is_dir():
        return RedirectResponse(request.headers.get("referer"))
        # needs to be fixed
        # zip_file_name = f"{batch_id}_segmental_calls.zip"
        # path = Path(zip_file_name)
        # zip_dir(zip_name=zip_file_name, source_dir=file_path, suffix="bed")
        # return FileResponse(
        #    str(path.absolute()),
        #    media_type="application/x-zip-compressed",
        #    headers={"Content-Disposition": f"attachment;filename={zip_file_name}"},
        # )

    return FileResponse(
        str(path.absolute()), media_type="application/octet-stream", filename=path.name
    )


@router.get("/sample_download/{sample_id}/{file_id}")
def sample_download(
    request: Request,
    sample_id: str,
    file_id: str,
    adapter: StatinaAdapter = Depends(get_nipt_adapter),
    user: User = Depends(get_current_user),
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
