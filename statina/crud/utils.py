import io
from pathlib import Path
from typing import Tuple, Union, Any
from zipfile import ZipFile, ZIP_DEFLATED


def paginate(page_size: int, page_num: int) -> Tuple[int, int]:
    """Calculate number of documents to skip"""
    if not page_size:
        return 0, 0
    if not page_num:
        return 0, page_size
    skip = page_size * (page_num - 1)
    return skip, page_size


def zip_dir(source_dir: Union[str, Path]) -> io.BytesIO:
    """Function for zipping"""
    src_path = Path(source_dir).expanduser().resolve(strict=True)
    len_src_path = len(src_path.as_posix())
    file_obj = io.BytesIO()
    file_obj.seek(0)
    with ZipFile(file=file_obj, mode="a", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for file in src_path.rglob("*"):
            zf.write(filename=file.as_posix(), arcname=file.as_posix()[len_src_path:])
    file_obj.seek(0)
    return file_obj


def get_trisomy_metadata(dataset: Any) -> dict:
    return {
        "soft_max": {
            "Zscore": dataset.trisomy_soft_max,
            "color": "orange",
            "text": f"Warning threshold = {dataset.trisomy_soft_max}",
        },
        "hard_max": {
            "Zscore": dataset.trisomy_hard_max,
            "color": "red",
            "text": f"Threshold = {dataset.trisomy_hard_max}",
        },
        "hard_min": {
            "Zscore": dataset.trisomy_hard_min,
            "color": "red",
            "text": f"Threshold = {dataset.trisomy_hard_min}",
        },
    }
