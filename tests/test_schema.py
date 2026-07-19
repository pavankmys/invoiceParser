import pytest
from pydantic import ValidationError

from invoice_parser.schema.models import (
    GSTInvoice,
    LineItem,
    Seller,
    Buyer,
    Totals,
)


class TestGSTInvoice:
    def test_create_minimal(self):
        invoice = GSTInvoice()
        assert invoice.is_valid()
        assert invoice.line_items == []
        assert invoice.errors == []

    def test_to_dict(self, sample_invoice: GSTInvoice):
        d = sample_invoice.to_dict()
        assert d["invoice_number"] == "INV-001"
        assert d["seller"]["name"] == "Acme Corp"
        assert d["seller"]["gstin"] == "27AABCU9603R1ZM"

    def test_to_json(self, sample_invoice: GSTInvoice):
        j = sample_invoice.to_json()
        assert "INV-001" in j
        assert "Widget A" in j


class TestSeller:
    def test_gstin_uppercased(self):
        s = Seller(name="Test", gstin="27aabcU9603R1zm")
        assert s.gstin == "27AABCU9603R1ZM"

    def test_minimal_seller(self):
        s = Seller(name="Test")
        assert s.gstin is None
        assert s.pan is None


class TestLineItem:
    def test_minimal_line_item(self):
        item = LineItem(description="Item")
        assert item.description == "Item"
        assert item.quantity is None

    def test_bad_gst_rate_string(self):
        with pytest.raises(ValidationError):
            LineItem(description="X", gst_rate="not-a-number")
