from pydantic import BaseModel



class Batch(BaseModel):
    result_file: str
    multiqc_report: str
    segmental_calls: str



class User(BaseModel):
    email: str
    name: str
    role: str