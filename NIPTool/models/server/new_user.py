from pydantic import BaseModel, EmailStr, validator

from NIPTool.exeptions import MissMatchingPasswordError
from NIPTool.config import EmailSettings


class NewUser(BaseModel):
    email: EmailStr
    username: str
    password_repeated: str
    password: str

    @validator("password", always=True)
    def validate_password(cls, v, values: dict) -> str:
        print(values)
        if v != values["password_repeated"]:
            raise MissMatchingPasswordError
        return v


class NewUserRequestEmail(EmailSettings):
    admin_email: EmailStr = "maya.brandi@scilifelab.se"
    subject: str = "NIPTool User Request"
    user_email: EmailStr
    message: str

    @validator("message", always=True)
    def make_message(cls, v, values: dict) -> str:
        return f"User request from {v}. Give the user proper credentials and send an email to {values['user_email']} when done."
