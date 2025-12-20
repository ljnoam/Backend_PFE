from app.services.anonymizer import AnonymizerService
from app.services.impact_calculator import ImpactCalculator

def test_services():
    # --- Test Anonymizer ---
    print("\n--- Testing Anonymizer ---")
    anon = AnonymizerService()
    
    test_cases = [
        "Mon email est test.user@example.com et mon site est https://monsite.com",
        "Appelle-moi au 06 12 34 56 78",
        "Voici ma CB : 1234 5678 1234 5678 pour le paiement",
        "Mon numéro sécu est le 1 85 05 75 123 456 78"
    ]
    
    for text in test_cases:
        print(f"Original: {text}")
        print(f"Scrubbed: {anon.scrub_pii(text)}")
        print("-" * 30)

    # --- Test Impact Calculator ---
    print("\n--- Testing Impact Calculator (Sovereignty) ---")
    calc = ImpactCalculator()
    
    models = ["Mistral-Large", "gpt-4", "Claude-3-Opus", "Gemini-Pro", "Unknown-Model"]
    
    for m in models:
        region = calc.get_sovereignty(m)
        print(f"Model: {m.ljust(15)} -> Region: {region}")

if __name__ == "__main__":
    test_services()
