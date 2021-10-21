import io
from pathlib import Path
from typing import Tuple, Union
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
    file_obj = io.BytesIO()
    file_obj.seek(0)
    with ZipFile(file=file_obj, mode="a", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for file in src_path.iterdir():
            zf.write(filename=file.as_posix(), arcname=file.name)
    file_obj.seek(0)
    return file_obj
