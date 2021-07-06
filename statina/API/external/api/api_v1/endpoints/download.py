from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse
from starlette.responses import StreamingResponse

from statina.adapter.plugin import StatinaAdapter
from statina.API.external.api.deps import get_current_user
from statina.config import get_nipt_adapter
from statina.crud.find import find
from statina.models.database import User, DataBaseSample
from statina.parse.batch import validate_file_path
from zipfile import ZIP_DEFLATED, ZipFile
import io
import zipfile
from os import PathLike
from typing import Union, Optional

router = APIRouter()


def zip_dir(
    zip_name: str, source_dir: Union[str, PathLike], suffix: Optional[str] = None
) -> io.BytesIO:
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
    user: User = Depends(get_current_user),
):
    """View for batch downloads"""
    batch: dict = find.batch(adapter=adapter, batch_id=batch_id).dict()
    file_path = batch.get(file_id)
    if not validate_file_path(file_path):
        return RedirectResponse(request.headers.get("referer"))

    path = Path(file_path)
    if path.is_dir():
        zip_file_name = f"{batch_id}_segmental_calls.zip"
        file_obj = zip_dir(zip_name=zip_file_name, source_dir=file_path, suffix="bed")
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
