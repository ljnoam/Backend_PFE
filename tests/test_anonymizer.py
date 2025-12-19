import unittest
from app.services.anonymizer import AnonymizerService

class TestAnonymizerService(unittest.TestCase):
    def setUp(self):
        self.service = AnonymizerService()

    def test_scrub_email(self):
        text = "Mon email est test.user@example.com."
        expected = "Mon email est [EMAIL]."
        self.assertEqual(self.service.scrub_pii(text), expected)

    def test_scrub_phone(self):
        text = "Appelle-moi au 0612345678."
        expected = "Appelle-moi au [PHONE]."
        self.assertEqual(self.service.scrub_pii(text), expected)
        
        text_spaces = "Ou au 06 12 34 56 78."
        expected_spaces = "Ou au [PHONE]."
        self.assertEqual(self.service.scrub_pii(text_spaces), expected_spaces)

    def test_scrub_url(self):
        text = "Clique sur https://www.google.com pour chercher."
        expected = "Clique sur [URL] pour chercher."
        self.assertEqual(self.service.scrub_pii(text), expected)

    def test_scrub_mixed(self):
        text = "Infos: 01 23 45 67 89, admin@site.org."
        expected = "Infos: [PHONE], [EMAIL]."
        self.assertEqual(self.service.scrub_pii(text), expected)

if __name__ == '__main__':
    unittest.main()
