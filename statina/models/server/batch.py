from typing import List

from pydantic import BaseModel

from statina.models.database import Batch


class PaginatedBatchResponse(BaseModel):
    document_count: int
    documents: List[Batch]
