# invoice-parser

Indian GST invoice parser — extracted structured data from invoices using Gemini Flash 2.0 vision.

```python
from invoice_parser import InvoiceParser

parser = InvoiceParser()
invoice = parser.parse("invoice.pdf")
print(invoice.to_json())
```

## Features

- **Vision-based extraction** — reads scanned PDFs, photos, digital invoices
- **GST validation** — validates GSTIN, PAN, HSN codes, CGST/SGST/IGST math
- **Sync + async** — works with CLI scripts and FastAPI web apps
- **Pydantic models** — type-safe, serializable, well-documented
- **Pluggable extractors** — Gemini now, Azure Doc Intelligence coming

## Install

```bash
# Core
pip install invoice-parser

# With Gemini extraction + PDF support
pip install "invoice-parser[gemini,pdf]"
```

## License

MIT
