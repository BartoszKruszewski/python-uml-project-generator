class CustomException(Exception):
    """"Base class for custom exceptions in the project generator domain."""


class XmiParserException(CustomException):
    """Base class for XMI parser related exceptions."""


class NoAttribute(XmiParserException):
    """Exception raised when an expected attribute is missing in an XMI element."""


class NoElement(XmiParserException):
    """Exception raised when an expected child element is missing in an XMI element."""


class ImportMapperException(CustomException):
    """Base class for import mapping related exceptions."""


class NonMappedClass(ImportMapperException):
    """Exception raised when a class name is not mapped to any import path."""
