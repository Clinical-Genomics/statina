from pydantic import BaseModel

class DatabaseUser(BaseModel):
    email: str
    name: str
    role: str
