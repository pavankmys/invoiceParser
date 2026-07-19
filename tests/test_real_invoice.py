import os
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_PATH = FIXTURES / "sample_invoice.jpg"


def test_sample_invoice_image_exists():
    assert SAMPLE_PATH.exists(), f"Download sample invoice first: {SAMPLE_PATH}"
    assert SAMPLE_PATH.stat().st_size > 0


def test_real_extraction():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("Set GEMINI_API_KEY to run this test")

    from invoice_parser import InvoiceParser

    parser = InvoiceParser(api_key=api_key, validate=True)
    invoice = parser.parse(str(SAMPLE_PATH))

    print(f"\nInvoice #: {invoice.invoice_number}")
    print(f"Seller: {invoice.seller}")
    print(f"Line items: {len(invoice.line_items)}")
    print(f"Total: {invoice.totals}")
    print(f"Errors: {invoice.errors}")

    assert invoice.invoice_number is not None, "Should extract invoice number"
    assert invoice.seller is not None, "Should extract seller"
    assert invoice.totals is not None, "Should extract totals"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "-s"]))
