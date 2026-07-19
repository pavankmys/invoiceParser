# Indian GST Invoice Parser — Plan

## Goal
Build a pip-installable Python library that extracts structured data from Indian GST invoices using Gemini Flash 2.0 vision, then validates the extracted fields against GST rules.

## Architecture

```
User App → InvoiceParser.parse("invoice.pdf")
                ↓
         ImagePreprocessor (PDF→PNG, enhance)
                ↓
         GeminiFlashExtractor (vision prompt → JSON)
                ↓
         Validators (GSTIN, PAN, HSN, tax math)
                ↓
         GSTInvoice (Pydantic model)
```

## Design Decisions

| Decision | Choice | Why |
|---|---|---|
| Vision model | Gemini Flash 2.0 | Native image input, cheap, fast |
| Data modeling | Pydantic v2 | Validation, serialization, JSON schema |
| Build system | setuptools (PEP 621) | Zero-config, widely compatible |
| Async support | Yes (aparse, analyze_async) | For FastAPI/ASGI apps |
| PDF support | pdf2image (optional dep) | Keeps core light |

## Public API

```python
from invoice_parser import InvoiceParser

parser = InvoiceParser(api_key="...")
invoice = parser.parse("invoice.pdf")        # sync
invoice = await parser.aparse("invoice.pdf") # async
invoice = parser.parse_bytes(upload.read())  # web apps
```

## Test Plan

- **test_schema.py** — Pydantic model creation, serialization, validation
- **test_gst_validator.py** — GSTIN, PAN, HSN, state code pattern matching
- **test_tax_validator.py** — CGST+SGST=IGST, totals cross-check, edge cases
- **test_parser.py** — Mocked API calls, file handling, validation pipeline

## Git

- Private repo on GitHub
- Single initial commit
- `pyproject.toml` for pip install
