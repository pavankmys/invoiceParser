from decimal import Decimal

import pytest

from invoice_parser.schema.models import LineItem, GSTInvoice, Totals
from invoice_parser.validators.tax import validate_tax_math, validate_totals


class TestValidateTaxMath:
    def test_intra_state_valid(self):
        item = LineItem(
            description="X",
            taxable_value=Decimal("1000"),
            gst_rate=Decimal("18"),
            cgst_amount=Decimal("90"),
            sgst_amount=Decimal("90"),
        )
        assert validate_tax_math(item) == []

    def test_intra_state_mismatch(self):
        item = LineItem(
            description="X",
            taxable_value=Decimal("1000"),
            gst_rate=Decimal("18"),
            cgst_amount=Decimal("50"),
            sgst_amount=Decimal("50"),
        )
        errors = validate_tax_math(item)
        assert len(errors) == 1
        assert "CGST+SGST" in errors[0]

    def test_cgst_sgst_not_equal(self):
        item = LineItem(
            description="X",
            taxable_value=Decimal("1000"),
            gst_rate=Decimal("18"),
            cgst_amount=Decimal("100"),
            sgst_amount=Decimal("80"),
        )
        errors = validate_tax_math(item)
        assert any("CGST" in e and "SGST" in e for e in errors)

    def test_inter_state_valid(self):
        item = LineItem(
            description="X",
            taxable_value=Decimal("1000"),
            gst_rate=Decimal("18"),
            igst_amount=Decimal("180"),
        )
        assert validate_tax_math(item) == []

    def test_inter_state_mismatch(self):
        item = LineItem(
            description="X",
            taxable_value=Decimal("1000"),
            gst_rate=Decimal("18"),
            igst_amount=Decimal("150"),
        )
        errors = validate_tax_math(item)
        assert len(errors) == 1
        assert "IGST" in errors[0]

    def test_no_tax_fields(self):
        item = LineItem(
            description="X",
            taxable_value=Decimal("1000"),
            gst_rate=Decimal("18"),
        )
        errors = validate_tax_math(item)
        assert any("CGST+SGST" in e or "IGST" in e for e in errors)

    def test_null_taxable_skips(self):
        item = LineItem(description="X")
        assert validate_tax_math(item) == []

    def test_tiny_rounding(self):
        item = LineItem(
            description="X",
            taxable_value=Decimal("100"),
            gst_rate=Decimal("5"),
            cgst_amount=Decimal("2.50"),
            sgst_amount=Decimal("2.50"),
        )
        assert validate_tax_math(item) == []


class TestValidateTotals:
    def test_totals_match(self, sample_invoice):
        assert validate_totals(sample_invoice) == []

    def test_totals_mismatch(self):
        invoice = GSTInvoice(
            line_items=[LineItem(description="X", taxable_value=Decimal("100"), gst_rate=Decimal("18"))],
            totals=Totals(
                taxable_amount=Decimal("100"),
                total_tax=Decimal("18"),
                grand_total=Decimal("200"),
            ),
        )
        errors = validate_totals(invoice)
        assert len(errors) >= 1

    def test_no_totals(self):
        invoice = GSTInvoice(line_items=[LineItem(description="X")])
        assert validate_totals(invoice) == []

    def test_round_off(self):
        invoice = GSTInvoice(
            line_items=[LineItem(description="X", taxable_value=Decimal("100"), gst_rate=Decimal("18"))],
            totals=Totals(
                taxable_amount=Decimal("100"),
                total_tax=Decimal("18"),
                grand_total=Decimal("118.00"),
                round_off=Decimal("0.00"),
            ),
        )
        assert validate_totals(invoice) == []
