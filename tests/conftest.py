import pytest

from invoice_parser.schema.models import (
    GSTInvoice,
    LineItem,
    Seller,
    Buyer,
    Totals,
    MetaData,
)


@pytest.fixture
def valid_gstin() -> str:
    return "27AABCU9603R1ZM"


@pytest.fixture
def invalid_gstin() -> str:
    return "INVALID123"


@pytest.fixture
def valid_pan() -> str:
    return "AABCU9603R"


@pytest.fixture
def sample_line_item() -> LineItem:
    return LineItem(
        description="Widget A",
        hsn_code="73269099",
        quantity=10,
        unit="Nos",
        rate=500.00,
        taxable_value=5000.00,
        gst_rate=18,
        cgst_amount=450.00,
        sgst_amount=450.00,
        igst_amount=None,
        total=5900.00,
    )


@pytest.fixture
def sample_invoice(sample_line_item: LineItem) -> GSTInvoice:
    return GSTInvoice(
        meta=MetaData(source_type="image", confidence=0.95),
        invoice_number="INV-001",
        invoice_date="2024-06-15",
        seller=Seller(
            name="Acme Corp",
            gstin="27AABCU9603R1ZM",
            address="Mumbai",
        ),
        buyer=Buyer(name="Buyer Inc", gstin="29AABCB1234E1ZP"),
        line_items=[sample_line_item],
        totals=Totals(
            taxable_amount=5000.00,
            cgst_total=450.00,
            sgst_total=450.00,
            grand_total=5900.00,
            total_tax=900.00,
        ),
    )


@pytest.fixture
def sample_invoice_json() -> dict:
    return {
        "invoice_number": "INV-001",
        "invoice_date": "2024-06-15",
        "seller": {"name": "Acme Corp", "gstin": "27AABCU9603R1ZM", "address": "Mumbai", "pan": None},
        "buyer": {"name": "Buyer Inc", "gstin": "29AABCB1234E1ZP", "address": None, "state_code": None},
        "line_items": [
            {
                "description": "Widget A",
                "hsn_code": "73269099",
                "quantity": 10, "unit": "Nos", "rate": 500.00,
                "taxable_value": 5000.00, "gst_rate": 18,
                "cgst_amount": 450.00, "sgst_amount": 450.00,
                "igst_amount": None, "total": 5900.00,
            }
        ],
        "totals": {
            "taxable_amount": 5000.00, "cgst_total": 450.00, "sgst_total": 450.00,
            "igst_total": None, "total_tax": 900.00, "grand_total": 5900.00,
            "round_off": None,
        },
    }
