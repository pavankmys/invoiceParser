import json
import time
from typing import Optional

from PIL import Image

from invoice_parser.core.exceptions import ConfigurationError, ExtractionError
from invoice_parser.extractors.base import Extractor
from invoice_parser.schema.models import (
    GSTInvoice,
    LineItem,
    MetaData,
    Seller,
    Buyer,
    Totals,
)

PROMPT = """You are an Indian tax invoice parser. Extract all fields from this invoice image as JSON.
Return ONLY valid JSON. No markdown, no explanations, no code fences.

Use this exact structure — use null for any missing field:
{
    "invoice_number": null,
    "invoice_date": "YYYY-MM-DD",
    "due_date": null,
    "place_of_supply": null,
    "supply_type": null,
    "seller": {"name": null, "gstin": null, "address": null, "pan": null},
    "buyer": {"name": null, "gstin": null, "address": null, "state_code": null},
    "line_items": [
        {
            "description": null, "hsn_code": null,
            "quantity": null, "unit": null, "rate": null,
            "taxable_value": null, "gst_rate": null,
            "cgst_amount": null, "sgst_amount": null,
            "igst_amount": null, "total": null
        }
    ],
    "totals": {
        "taxable_amount": null, "cgst_total": null, "sgst_total": null,
        "igst_total": null, "total_tax": null, "grand_total": null,
        "round_off": null
    }
}

Rules:
- All amounts as numbers (not strings)
- Dates in YYYY-MM-DD format
- Extract HSN/SAC codes from line items
- Supply type: one of "B2B", "B2C", "SEZ", "EXPORT" or null
- For intra-state, CGST and SGST should each be half of total GST
- For inter-state, only IGST should be present
"""


class GeminiFlashExtractor(Extractor):
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-2.0-flash",
        vertexai: bool = False,
        project: str | None = None,
        location: str = "us-central1",
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.vertexai = vertexai
        self.project = project
        self.location = location
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from google import genai
        except ImportError:
            raise ConfigurationError(
                "google-genai is required. Install with: pip install invoice-parser[gemini]"
            )
        if self.vertexai:
            self._client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location,
            )
        else:
            if not self.api_key:
                raise ConfigurationError(
                    "Gemini API key required. Set GEMINI_API_KEY env var "
                    "or use vertexai=True with a service account."
                )
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _parse_response(self, text: str, elapsed: int) -> GSTInvoice:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ExtractionError(f"Failed to parse LLM response as JSON: {e}")

        line_items = []
        for item_data in data.get("line_items", []):
            if item_data.get("description"):
                line_items.append(LineItem(**item_data))

        seller_data = data.get("seller")
        buyer_data = data.get("buyer")
        totals_data = data.get("totals")

        return GSTInvoice(
            meta=MetaData(
                source_type="image",
                processing_time_ms=elapsed,
                raw_response=text,
            ),
            invoice_number=data.get("invoice_number"),
            invoice_date=data.get("invoice_date"),
            due_date=data.get("due_date"),
            place_of_supply=data.get("place_of_supply"),
            supply_type=data.get("supply_type"),
            seller=Seller(**seller_data) if seller_data else None,
            buyer=Buyer(**buyer_data) if buyer_data else None,
            line_items=line_items,
            totals=Totals(**totals_data) if totals_data else None,
        )

    def analyze(self, image: Image.Image) -> GSTInvoice:
        client = self._get_client()
        start = time.monotonic()
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=[PROMPT, image],
            )
            elapsed = int((time.monotonic() - start) * 1000)
            return self._parse_response(response.text, elapsed)
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            raise ExtractionError(f"Gemini API call failed after {elapsed}ms", cause=e)

    async def analyze_async(self, image: Image.Image) -> GSTInvoice:
        client = self._get_client()
        start = time.monotonic()
        try:
            from google.genai import types
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=[PROMPT, image],
            )
            elapsed = int((time.monotonic() - start) * 1000)
            return self._parse_response(response.text, elapsed)
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            raise ExtractionError(f"Gemini API call failed after {elapsed}ms", cause=e)
