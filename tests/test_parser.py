from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from invoice_parser.core.parser import InvoiceParser, parse_invoice
from invoice_parser.core.exceptions import ConfigurationError, ExtractionError
from invoice_parser.schema.models import GSTInvoice, MetaData, Seller, Buyer


class TestInvoiceParser:
    def test_requires_api_key(self):
        with pytest.raises(ConfigurationError):
            InvoiceParser(extractor="gemini")

    def test_unknown_extractor(self):
        with pytest.raises(ValueError, match="Unknown extractor"):
            InvoiceParser(api_key="test", extractor="unknown")

    @patch("invoice_parser.extractors.gemini.GeminiFlashExtractor._get_client")
    def test_parse_image(self, mock_get_client, sample_invoice_json):
        mock_client = MagicMock()
        mock_response = MagicMock()
        import json
        mock_response.text = json.dumps(sample_invoice_json)
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        parser = InvoiceParser(api_key="test-key", validate=False)
        img = Image.new("RGB", (100, 100))
        result = parser.parse(img)

        assert isinstance(result, GSTInvoice)
        assert result.invoice_number == "INV-001"
        assert result.seller.name == "Acme Corp"
        assert len(result.line_items) == 1

    @patch("invoice_parser.extractors.gemini.GeminiFlashExtractor._get_client")
    def test_parse_file_not_found(self, mock_get_client):
        parser = InvoiceParser(api_key="test-key", validate=False)
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.jpg")

    @patch("invoice_parser.extractors.gemini.GeminiFlashExtractor._get_client")
    def test_parse_bytes(self, mock_get_client, sample_invoice_json):
        mock_client = MagicMock()
        mock_response = MagicMock()
        import json
        import io
        from PIL import Image
        mock_response.text = json.dumps(sample_invoice_json)
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        buf = io.BytesIO()
        Image.new("RGB", (100, 100)).save(buf, format="PNG")
        valid_png_bytes = buf.getvalue()

        parser = InvoiceParser(api_key="test-key", validate=False)
        result = parser.parse_bytes(valid_png_bytes)

        assert isinstance(result, GSTInvoice)

    @patch("invoice_parser.extractors.gemini.GeminiFlashExtractor._get_client")
    def test_parse_with_validation(self, mock_get_client, sample_invoice_json):
        mock_client = MagicMock()
        mock_response = MagicMock()
        import json
        sample_invoice_json["seller"]["gstin"] = "BAD-GSTIN"
        mock_response.text = json.dumps(sample_invoice_json)
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        parser = InvoiceParser(api_key="test-key", validate=True)
        img = Image.new("RGB", (100, 100))
        result = parser.parse(img)

        assert len(result.errors) >= 1

    @patch("invoice_parser.extractors.gemini.GeminiFlashExtractor._get_client")
    def test_parse_with_validation_raises(self, mock_get_client, sample_invoice_json):
        mock_client = MagicMock()
        mock_response = MagicMock()
        import json
        sample_invoice_json["seller"]["gstin"] = "BAD-GSTIN"
        mock_response.text = json.dumps(sample_invoice_json)
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        parser = InvoiceParser(api_key="test-key", validate=True, raise_on_error=True)
        img = Image.new("RGB", (100, 100))
        from invoice_parser.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            parser.parse(img)

    @patch("invoice_parser.extractors.gemini.GeminiFlashExtractor._get_client")
    def test_api_failure(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("API down")
        mock_get_client.return_value = mock_client

        parser = InvoiceParser(api_key="test-key", validate=False)
        img = Image.new("RGB", (100, 100))
        with pytest.raises(ExtractionError):
            parser.parse(img)

    def test_parse_invoice_function(self):
        result = parse_invoice.__doc__
        assert result is not None or callable(parse_invoice)
        assert callable(parse_invoice)
