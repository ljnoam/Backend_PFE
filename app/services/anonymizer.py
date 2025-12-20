import re

class AnonymizerService:
    def scrub_pii(self, text: str) -> str:
        """
        Detects and masks Personal Identifiable Information (PII) 
        like emails, phone numbers, and URLs.
        """
        # 1. Mask Emails (Improved pattern)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text = re.sub(email_pattern, '[EMAIL]', text)

        # 2. Mask URLs (http/https)
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        text = re.sub(url_pattern, '[URL]', text)

        # 3. Mask Phone Numbers (FR/INTL formats)
        # Matches 06 12 34 56 78, +33 6, etc.
        phone_pattern = r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}'
        text = re.sub(phone_pattern, '[PHONE]', text)

        # 4. Mask Credit Cards (Basic 16 digits, with spaces or dashes)
        # Ex: 1234 5678 1234 5678
        cc_pattern = r'\b(?:\d{4}[ -]?){3}\d{4}\b'
        text = re.sub(cc_pattern, '[CREDIT_CARD]', text)

        # 5. Mask French Social Security Number (NIR)
        # Ex: 1 85 05 75 123 456 78
        ssn_pattern = r'\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}(?:\s?\d{2})?\b'
        text = re.sub(ssn_pattern, '[SSN]', text)

        return text

# Simple local test if run directly
if __name__ == "__main__":
    service = AnonymizerService()
    test_text = "Contacte-moi au 06 12 34 56 78 ou sur mon.email@test.com. Visite https://mon-site.fr"
    print(f"Original: {test_text}")
    print(f"Scrubbed: {service.scrub_pii(test_text)}")
