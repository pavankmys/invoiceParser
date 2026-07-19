class InvoiceParserError(Exception):
    pass


class ExtractionError(InvoiceParserError):
    def __init__(self, message: str, cause: Exception | None = None):
        self.cause = cause
        super().__init__(message)


class ValidationError(InvoiceParserError):
    def __init__(self, message: str, field_errors: list[str] | None = None):
        self.field_errors = field_errors or []
        super().__init__(message)


class ConfigurationError(InvoiceParserError):
    pass


class UnsupportedFormatError(InvoiceParserError):
    pass
