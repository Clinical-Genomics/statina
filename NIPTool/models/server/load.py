from pydantic import BaseModel


class BatchRequestBody(BaseModel):
    result_file: str
    multiqc_report: str
    segmental_calls: str


class UserRequestBody(BaseModel):
    email: str
    name: str
    role: str
