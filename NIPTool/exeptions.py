from typing import Optional


class NIPToolError(Exception):
    def __init__(self, message: str, code: Optional[int]=None):
        self.message = message
        self.code = code


class MissingResultsError(NIPToolError):
    pass


class InvalidFileError(NIPToolError):
    pass


class FileValidationError(NIPToolError):
    pass


class InsertError(NIPToolError):
    pass
