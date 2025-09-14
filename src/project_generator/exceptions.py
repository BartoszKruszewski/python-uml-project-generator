class CustomException(Exception):
    pass


class XmiParserException(CustomException):
    pass


class NoAttribute(XmiParserException):
    pass


class NoElement(XmiParserException):
    pass


class ImportMapperException(CustomException):
    pass


class NonMappedClass(ImportMapperException):
    pass
