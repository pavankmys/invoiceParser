# HOWTO Guide — invoice-parser

## Installation

```bash
# Core (schema + validators only)
pip install invoice-parser

# With Gemini Flash extractor
pip install invoice-parser[gemini]

# With PDF support
pip install invoice-parser[pdf]

# Everything
pip install invoice-parser[all]
```

## Quick Start

### 1. Set your API key

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

### 2. Parse an invoice

```python
from invoice_parser import InvoiceParser

parser = InvoiceParser()
invoice = parser.parse("path/to/invoice.pdf")

print(invoice.invoice_number)   # INV-2024-00123
print(invoice.seller.name)      # Acme Corp
print(invoice.seller.gstin)     # 27AABCU9603R1ZM

for item in invoice.line_items:
    print(f"{item.description}: {item.total}")

print(invoice.totals.grand_total)
```

### 3. Handle errors

```python
# Errors are collected — inspect them
if not invoice.is_valid():
    for err in invoice.errors:
        print(f"Validation: {err}")

# Or raise on first error
parser = InvoiceParser(raise_on_error=True)
```

### 4. Use in a web app (FastAPI)

```python
from fastapi import FastAPI, UploadFile
from invoice_parser import InvoiceParser

app = FastAPI()
parser = InvoiceParser()

@app.post("/parse-invoice")
async def parse(file: UploadFile):
    data = await file.read()
    invoice = await parser.aparse(data)
    return invoice.to_dict()
```

### 5. JSON output

```python
# As dict
d = invoice.to_dict()

# As JSON string
j = invoice.to_json(indent=2)
```

## Configuration

```python
# Pass key directly (overrides env var)
parser = InvoiceParser(api_key="your-key")

# Disable validation
parser = InvoiceParser(validate=False)

# Change model
from invoice_parser.extractors import GeminiFlashExtractor
parser = InvoiceParser(extractor=GeminiFlashExtractor(api_key="..."))
```

## Supported Inputs

- JPEG, PNG, BMP, TIFF, WebP
- PDF (via `pip install invoice-parser[pdf]`)
- Raw bytes (for web uploads)
- PIL Image objects

## Supported Extractors

| Extractor | Status | Install |
|---|---|---|
| Gemini Flash 2.0 | ✅ Ready | `invoice-parser[gemini]` |
| Azure Doc Intelligence | 🔧 Planned | `invoice-parser[azure]` |

## Output Schema

See `src/invoice_parser/schema/models.py` for the full `GSTInvoice` model.

Key fields:
- `invoice_number`, `invoice_date`, `supply_type`
- `seller.gstin`, `buyer.gstin`
- `line_items[].{hsn_code, gst_rate, cgst_amount, sgst_amount, igst_amount}`
- `totals.{taxable_amount, cgst_total, sgst_total, igst_total, grand_total}`
- `errors[]` — validation messages
