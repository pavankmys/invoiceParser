import time
from decimal import Decimal
from pathlib import Path
from typing import Optional

from PIL import Image

from invoice_parser.config import get_gemini_api_key
from invoice_parser.core.exceptions import ExtractionError, ValidationError
from invoice_parser.core.image_preprocessor import enhance_image, image_to_bytes, load_image
from invoice_parser.extractors import Extractor, GeminiFlashExtractor
from invoice_parser.schema.models import GSTInvoice
from invoice_parser.validators import validate_tax_math, validate_totals, validate_gstin


class InvoiceParser:
    def __init__(
        self,
        api_key: Optional[str] = None,
        extractor: str = "gemini",
        validate: bool = True,
        raise_on_error: bool = False,
        vertexai: bool = False,
        project: Optional[str] = None,
        location: str = "us-central1",
        tax_tolerance: float = 0.50,
        total_tolerance: float = 0.50,
        max_retries: int = 1,
    ):
        self.validate_output = validate
        self.raise_on_error = raise_on_error
        self.tax_tolerance = Decimal(str(tax_tolerance))
        self.total_tolerance = Decimal(str(total_tolerance))
        self.max_retries = max_retries
        self._extractor = self._build_extractor(extractor, api_key, vertexai, project, location)

    def _build_extractor(
        self,
        name: str,
        api_key: Optional[str],
        vertexai: bool = False,
        project: Optional[str] = None,
        location: str = "us-central1",
    ) -> Extractor:
        if name == "gemini":
            key = api_key or get_gemini_api_key()
            return GeminiFlashExtractor(
                api_key=key,
                vertexai=vertexai,
                project=project,
                location=location,
            )
        raise ValueError(f"Unknown extractor: {name}. Supported: gemini")

    @property
    def extractor(self) -> Extractor:
        return self._extractor

    def _process(self, image: Image.Image) -> GSTInvoice:
        start = time.monotonic()
        image = enhance_image(image)
        invoice = self._extractor.analyze(image)
        invoice.meta.processing_time_ms = int((time.monotonic() - start) * 1000)
        if self.validate_output:
            errors = self._run_validation(invoice)
            invoice.errors = errors
            if errors and self.max_retries > 0:
                invoice = self._auto_correct(image, invoice, errors)
        return invoice

    async def _process_async(self, image: Image.Image) -> GSTInvoice:
        start = time.monotonic()
        image = enhance_image(image)
        invoice = await self._extractor.analyze_async(image)
        invoice.meta.processing_time_ms = int((time.monotonic() - start) * 1000)
        if self.validate_output:
            errors = self._run_validation(invoice)
            invoice.errors = errors
            if errors and self.max_retries > 0:
                invoice = await self._auto_correct_async(image, invoice, errors)
        return invoice

    def _auto_correct(self, image: Image.Image, invoice: GSTInvoice, errors: list[str]) -> GSTInvoice:
        previous_json = invoice.model_dump_json(indent=2, exclude_none=True)
        corrected = self._extractor.analyze_with_reprompt(image, previous_json, errors)
        corrected.meta.processing_time_ms = invoice.meta.processing_time_ms
        corrected.meta.confidence = invoice.meta.confidence
        new_errors = self._run_validation(corrected)
        corrected.errors = new_errors
        return corrected

    async def _auto_correct_async(self, image: Image.Image, invoice: GSTInvoice, errors: list[str]) -> GSTInvoice:
        previous_json = invoice.model_dump_json(indent=2, exclude_none=True)
        corrected = await self._extractor.analyze_with_reprompt_async(image, previous_json, errors)
        corrected.meta.processing_time_ms = invoice.meta.processing_time_ms
        corrected.meta.confidence = invoice.meta.confidence
        new_errors = self._run_validation(corrected)
        corrected.errors = new_errors
        return corrected

    def _run_validation(self, invoice: GSTInvoice) -> list[str]:
        all_errors: list[str] = []
        if invoice.seller and invoice.seller.gstin:
            valid, msg = validate_gstin(invoice.seller.gstin)
            if not valid:
                all_errors.append(f"Seller GSTIN: {msg}")
        if invoice.buyer and invoice.buyer.gstin:
            valid, msg = validate_gstin(invoice.buyer.gstin)
            if not valid:
                all_errors.append(f"Buyer GSTIN: {msg}")
        for i, item in enumerate(invoice.line_items):
            for err in validate_tax_math(item, self.tax_tolerance):
                all_errors.append(f"Line {i + 1}: {err}")
        for err in validate_totals(invoice, self.total_tolerance):
            all_errors.append(err)
        if all_errors and self.raise_on_error:
            raise ValidationError("Invoice validation failed", field_errors=all_errors)
        return all_errors

    def parse(self, source: str | Path | bytes | Image.Image) -> GSTInvoice:
        image = load_image(source)
        return self._process(image)

    async def aparse(self, source: str | Path | bytes | Image.Image) -> GSTInvoice:
        image = load_image(source)
        return await self._process_async(image)

    def parse_bytes(self, data: bytes) -> GSTInvoice:
        return self.parse(data)

    def parse_file(self, path: str | Path) -> GSTInvoice:
        return self.parse(path)


def parse_invoice(
    source: str | Path | bytes | Image.Image,
    api_key: Optional[str] = None,
    validate: bool = True,
    raise_on_error: bool = False,
    vertexai: bool = False,
    project: Optional[str] = None,
    location: str = "us-central1",
) -> GSTInvoice:
    parser = InvoiceParser(
        api_key=api_key,
        validate=validate,
        raise_on_error=raise_on_error,
        vertexai=vertexai,
        project=project,
        location=location,
    )
    return parser.parse(source)
