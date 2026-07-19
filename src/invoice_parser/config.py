import os
from typing import Optional

from invoice_parser.core.exceptions import ConfigurationError


def get_gemini_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ConfigurationError(
            "GEMINI_API_KEY environment variable not set. "
            "Set it or pass api_key= directly to InvoiceParser."
        )
    return key
