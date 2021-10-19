from typing import Tuple


def paginate(page_size: int, page_num: int) -> Tuple[int, int]:
    # Calculate number of documents to skip
    if not page_size:
        return 0, 0
    if not page_num:
        return 0, page_size
    skip = page_size * (page_num - 1)
    return skip, page_size
