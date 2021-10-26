from typing import Optional

from fastapi import status, HTTPException


class NIPToolError(Exception):
    def __init__(self, message: str):
        self.message = message


class MissingResultsError(NIPToolError):
    pass


class InvalidFileError(NIPToolError):
    pass


class FileValidationError(NIPToolError):
    pass


class MissMatchingPasswordError(NIPToolError):
    """Raise when password and confirmed password dont match"""

    pass


class EmailNotSentError(NIPToolError):
    pass


class NIPToolRestError(NIPToolError):
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(message)


class InsertError(NIPToolRestError):
    def __init__(self, message: str, code: Optional[int] = status.HTTP_405_METHOD_NOT_ALLOWED):
        self.message = message
        self.code = code
        super().__init__(message, code)


class CredentialsError(NIPToolError):
    def __init__(self, message: str, code: Optional[int] = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.code = code
        super().__init__(message)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

forbidden_access_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authorized to access this resource",
    headers={"WWW-Authenticate": "Bearer"},
)
