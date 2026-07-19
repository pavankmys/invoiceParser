from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Seller(BaseModel):
    name: str
    gstin: Optional[str] = None
    address: Optional[str] = None
    pan: Optional[str] = None

    @field_validator("gstin", "pan")
    @classmethod
    def coerce_and_upper(cls, v: Optional[str | int]) -> Optional[str]:
        if v is not None:
            return str(v).upper()
        return v

    @field_validator("address")
    @classmethod
    def coerce_str(cls, v: Optional[str | int]) -> Optional[str]:
        if v is not None and not isinstance(v, str):
            return str(v)
        return v


class Buyer(BaseModel):
    name: str
    gstin: Optional[str] = None
    address: Optional[str] = None
    state_code: Optional[str] = None

    @field_validator("state_code")
    @classmethod
    def coerce_state_code(cls, v: Optional[str | int]) -> Optional[str]:
        if v is not None:
            return str(v)
        return v


class LineItem(BaseModel):
    description: str
    hsn_code: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    rate: Optional[Decimal] = None
    taxable_value: Optional[Decimal] = None
    gst_rate: Optional[Decimal] = None
    cgst_amount: Optional[Decimal] = None
    sgst_amount: Optional[Decimal] = None
    igst_amount: Optional[Decimal] = None
    total: Optional[Decimal] = None

    @field_validator("hsn_code", "unit")
    @classmethod
    def coerce_str_fields(cls, v: Optional[str | int]) -> Optional[str]:
        if v is not None:
            return str(v)
        return v


class Totals(BaseModel):
    taxable_amount: Optional[Decimal] = None
    cgst_total: Optional[Decimal] = None
    sgst_total: Optional[Decimal] = None
    igst_total: Optional[Decimal] = None
    total_tax: Optional[Decimal] = None
    grand_total: Optional[Decimal] = None
    round_off: Optional[Decimal] = None


class MetaData(BaseModel):
    source_type: str = "unknown"
    page_count: int = 1
    processing_time_ms: Optional[int] = None
    confidence: Optional[float] = None
    raw_response: Optional[str] = None


class GSTInvoice(BaseModel):
    meta: MetaData = Field(default_factory=MetaData)
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    place_of_supply: Optional[str] = None
    supply_type: Optional[str] = None
    seller: Optional[Seller] = None
    buyer: Optional[Buyer] = None
    line_items: list[LineItem] = Field(default_factory=list)
    totals: Optional[Totals] = None
    errors: list[str] = Field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return self.model_dump(mode="json", exclude_none=True)

    def to_json(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent, exclude_none=True)
