from pydantic import BaseModel


class BatchLoadModel(BaseModel):
    result_file: str
    multiqc_report: str
    segmental_calls: str


class UserLoadModel(BaseModel):
    email: str
    name: str
    role: str
