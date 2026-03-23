from app.services.anonymizer import scrub_pii


def test_scrub_email():
    assert scrub_pii("Contact me at john.doe@example.com") == "Contact me at [EMAIL]"


def test_scrub_url():
    result = scrub_pii("Visit https://www.example.com/page")
    assert "[URL]" in result


def test_scrub_phone_fr():
    result = scrub_pii("Call me at 06 12 34 56 78")
    assert "[PHONE]" in result


def test_scrub_ip_address():
    result = scrub_pii("Server at 192.168.1.1")
    assert "[IP_ADDRESS]" in result


def test_no_pii_unchanged():
    text = "Write me a professional email about salary negotiation"
    assert scrub_pii(text) == text


def test_multiple_pii_types():
    text = "Email john@test.com or call 0612345678"
    result = scrub_pii(text)
    assert "[EMAIL]" in result
    assert "[PHONE]" in result


def test_returns_string():
    assert isinstance(scrub_pii("hello world"), str)
