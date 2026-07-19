from decimal import Decimal
from typing import Optional

from invoice_parser.schema.models import GSTInvoice, LineItem


TAX_SLABS = {0, 0.25, 1, 1.5, 3, 5, 6, 7.5, 9, 12, 13.5, 15, 18, 24, 28}
DEFAULT_EPSILON = Decimal("0.50")
DEFAULT_TOTALS_EPSILON = Decimal("0.50")


def validate_tax_math(item: LineItem, epsilon: Decimal = DEFAULT_EPSILON) -> list[str]:
    errors: list[str] = []
    if item.taxable_value is None or item.gst_rate is None:
        return errors

    expected_tax = item.taxable_value * item.gst_rate / Decimal("100")

    if item.cgst_amount is not None and item.sgst_amount is not None:
        total_gst = item.cgst_amount + item.sgst_amount
        if abs(total_gst - expected_tax) > epsilon:
            errors.append(
                f"CGST+SGST ({total_gst}) != {item.gst_rate}% of taxable ({expected_tax})"
            )
        if abs(item.cgst_amount - item.sgst_amount) > epsilon:
            errors.append(
                f"CGST ({item.cgst_amount}) != SGST ({item.sgst_amount}) "
                f"— intra-state CGST and SGST must be equal"
            )
    elif item.igst_amount is not None:
        if abs(item.igst_amount - expected_tax) > epsilon:
            errors.append(
                f"IGST ({item.igst_amount}) != {item.gst_rate}% of taxable ({expected_tax})"
            )
    else:
        errors.append("Neither CGST+SGST nor IGST found for line item")

    return errors


def validate_totals(invoice: GSTInvoice, epsilon: Decimal = DEFAULT_TOTALS_EPSILON) -> list[str]:
    errors: list[str] = []
    if not invoice.line_items:
        return errors
    if invoice.totals is None:
        return errors

    if invoice.totals.total_tax is not None and invoice.totals.grand_total is not None:
        expected_grand = (invoice.totals.taxable_amount or Decimal("0")) + invoice.totals.total_tax
        if invoice.totals.round_off is not None:
            expected_grand += invoice.totals.round_off
        if abs(invoice.totals.grand_total - expected_grand) > epsilon:
            errors.append(
                f"Grand total ({invoice.totals.grand_total}) != "
                f"taxable ({invoice.totals.taxable_amount}) + tax ({invoice.totals.total_tax})"
            )

    return errors


def is_valid_tax_slab(rate: Decimal) -> bool:
    return float(rate) in TAX_SLABS
