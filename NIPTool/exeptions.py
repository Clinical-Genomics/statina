

class NIPToolError(Exception):
    def __init__(self, message):
        self.message = message

class MissingResultsError(NIPToolError):
    pass

class InvalidFileError(NIPToolError):
    pass

class FileValidationError(NIPToolError):
    pass
