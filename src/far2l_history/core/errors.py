"""Custom exceptions used across parsing/serialization services."""


class ParseError(Exception):
    """Raised when an .hst file cannot be parsed into structured fields."""


class SchemaError(Exception):
    """Raised when JSON data does not match the expected schema for a service."""


class RoundtripError(Exception):
    """Raised when we cannot faithfully re-serialize parsed data back to .hst."""


class UnknownHeaderError(Exception):
    """Raised when a file header doesn't match any registered service."""
