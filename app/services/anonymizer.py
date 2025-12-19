import re

class AnonymizerService:
    def scrub_pii(self, text: str) -> str:
        """
        Detects and masks Personal Identifiable Information (PII) 
        like emails, phone numbers, and URLs.
        """
        # 1. Mask Emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        text = re.sub(email_pattern, '[EMAIL]', text)

        # 2. Mask URLs (http/https)
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
        text = re.sub(url_pattern, '[URL]', text)

        # 3. Mask Phone Numbers (Simple variant for FR/INTL formats)
        # Matches formats like 06 12 34 56 78, +33 6 12 34 56 78, 06.12.34.56.78
        phone_pattern = r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}'
        text = re.sub(phone_pattern, '[PHONE]', text)

        return text

# Simple local test if run directly
if __name__ == "__main__":
    service = AnonymizerService()
    test_text = "Contacte-moi au 06 12 34 56 78 ou sur mon.email@test.com. Visite https://mon-site.fr"
    print(f"Original: {test_text}")
    print(f"Scrubbed: {service.scrub_pii(test_text)}")
