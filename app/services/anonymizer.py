import re

# Pre-compiled regex patterns for PII detection
_PATTERNS = [
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[EMAIL]"),
    (re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*"), "[URL]"),
    (re.compile(r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}"), "[PHONE]"),
    (re.compile(r"\b(?:\d[\s-]*){13,19}\b"), "[CREDIT_CARD]"),
    (re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,}\b"), "[IBAN]"),
    (re.compile(r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}(?:\s?\d{2})?\b"), "[SSN]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[IP_ADDRESS]"),
]


def scrub_pii(text: str) -> str:
    """Detect and mask PII in text using pre-compiled regex patterns."""
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text
