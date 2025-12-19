import asyncio
from app.services.llm_engine import rewrite_prompt

async def main():
    user_intent = "Je veux une image de chat cyberpunk"
    targets = ["mistral", "chatgpt", "midjourney"]

    print(f"--- Test Start: '{user_intent}' ---\n")

    for target in targets:
        print(f"Testing target: {target.upper()}...")
        try:
            result = await rewrite_prompt(user_intent, target)
            print(f"Result:\n{result}\n")
            print("-" * 50)
        except Exception as e:
            print(f"Error testing {target}: {e}")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
