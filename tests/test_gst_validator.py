import pytest

from invoice_parser.validators.gst import (
    validate_gstin,
    validate_pan,
    validate_hsn,
    validate_state_code,
)


class TestValidateGSTIN:
    def test_valid_gstin(self):
        valid, msg = validate_gstin("27AABCU9603R1ZM")
        assert valid is True
        assert msg is None

    def test_invalid_format(self):
        valid, msg = validate_gstin("ABC123")
        assert valid is False
        assert "format" in msg.lower()

    def test_empty(self):
        valid, msg = validate_gstin("")
        assert valid is False

    def test_whitespace(self):
        valid, msg = validate_gstin("   ")
        assert valid is False

    def test_bad_state_code(self):
        valid, msg = validate_gstin("99AABCU9603R1ZM")
        assert valid is False
        assert "format" in msg.lower()


class TestValidatePAN:
    def test_valid_pan(self):
        valid, msg = validate_pan("AABCU9603R")
        assert valid is True

    def test_invalid_pan(self):
        valid, msg = validate_pan("12345")
        assert valid is False

    def test_empty_pan(self):
        valid, msg = validate_pan("")
        assert valid is False

    def test_lowercase_pan(self):
        valid, msg = validate_pan("aabcu9603r")
        assert valid is True


class TestValidateHSN:
    def test_valid_4_digit(self):
        valid, msg = validate_hsn("7326")
        assert valid is True

    def test_valid_8_digit(self):
        valid, msg = validate_hsn("73269099")
        assert valid is True

    def test_invalid_hsn(self):
        valid, msg = validate_hsn("abc")
        assert valid is False

    def test_empty_hsn(self):
        valid, msg = validate_hsn("")
        assert valid is False


class TestValidateStateCode:
    def test_valid_code(self):
        valid, msg = validate_state_code("27")
        assert valid is True

    def test_invalid_code(self):
        valid, msg = validate_state_code("99")
        assert valid is False

    def test_new_andhra(self):
        valid, msg = validate_state_code("37")
        assert valid is True
