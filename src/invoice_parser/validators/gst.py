import re
from typing import Optional

GSTIN_PATTERN = re.compile(r"^[0-3][0-9][A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
PAN_PATTERN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
HSN_PATTERN = re.compile(r"^\d{4,8}$")
SAC_PATTERN = re.compile(r"^\d{6,8}$")

STATE_CODES: dict[str, str] = {
    "01": "Jammu and Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "25": "Daman and Diu", "26": "Dadra and Nagar Haveli",
    "27": "Maharashtra", "28": "Andhra Pradesh (old)",
    "29": "Karnataka", "30": "Goa", "31": "Lakshadweep",
    "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
    "35": "Andaman and Nicobar", "36": "Telangana",
    "37": "Andhra Pradesh (new)", "38": "Ladakh",
}


def validate_gstin(gstin: str) -> tuple[bool, Optional[str]]:
    if not gstin or not gstin.strip():
        return False, "GSTIN is empty"
    gstin = gstin.strip().upper()
    if not GSTIN_PATTERN.match(gstin):
        return False, f"GSTIN '{gstin}' does not match format (2 state + 10 PAN + 3 chars)"
    state_code = gstin[:2]
    if state_code not in STATE_CODES:
        return False, f"Invalid state code '{state_code}' in GSTIN"
    return True, None


def validate_pan(pan: str) -> tuple[bool, Optional[str]]:
    if not pan or not pan.strip():
        return False, "PAN is empty"
    pan = pan.strip().upper()
    if not PAN_PATTERN.match(pan):
        return False, f"PAN '{pan}' does not match format (5 letters + 4 digits + 1 letter)"
    return True, None


def validate_hsn(code: str) -> tuple[bool, Optional[str]]:
    if not code or not code.strip():
        return False, "HSN/SAC code is empty"
    code = code.strip()
    if HSN_PATTERN.match(code) or SAC_PATTERN.match(code):
        return True, None
    return False, f"HSN/SAC '{code}' should be 4-8 digits"


def validate_state_code(code: str) -> tuple[bool, Optional[str]]:
    if code in STATE_CODES:
        return True, None
    return False, f"Unknown Indian state code: '{code}'"
