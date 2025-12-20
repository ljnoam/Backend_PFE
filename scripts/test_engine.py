import asyncio
from app.services.llm_engine import rewrite_prompt

async def test_prompts():
    test_input = "Je veux créer une application de gestion de budget."
    
    targets = ["chatgpt", "midjourney", "mistral", "claude", "gemini"]
    
    print(f"--- TEST INPUT: '{test_input}' ---\n")
    
    for target in targets:
        print(f"Testing Target: {target.upper()}...")
        try:
            result = await rewrite_prompt(test_input, target)
            print(f"--- RESULT ({target}) ---")
            print(result[:200] + "..." if len(result) > 200 else result)
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"ERROR ({target}): {e}\n")

if __name__ == "__main__":
    asyncio.run(test_prompts())
