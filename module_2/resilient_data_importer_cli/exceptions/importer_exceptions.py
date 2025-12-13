class ImporterError(Exception):
    """Base exception for importer errors."""


class FileFormatError(ImporterError):
    """Raised when the CSV format is invalid."""


class MissingFieldError(ImporterError):
    """Raised when a required CSV field is missing."""


class DuplicateUserError(ImporterError):
    """Raised when a user already exists in the repository."""
