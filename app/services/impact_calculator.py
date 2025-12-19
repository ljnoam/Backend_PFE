class ImpactCalculator:
    # --- Constants ---
    
    # Mapping Model -> Region
    SOVEREIGNTY_MAP = {
        "mistral": "EU",
        "gpt": "USA",
        "gpt-3.5": "USA",
        "gpt-4": "USA",
        "claude": "USA",
        "llama": "USA", # Meta
        "midjourney": "USA"
    }

    # CO2 Constants
    # Estimation: 0.04g CO2 per 1000 tokens (Hypothetical average for inference)
    CO2_PER_1000_TOKENS = 0.04 

    def get_sovereignty(self, model_name: str) -> str:
        """
        Returns the region of hosting for a given AI model.
        Defaults to 'Global/Unknown' if not found.
        """
        # Normalize key for lookup
        key = model_name.lower()
        
        # Simple substring matching for robustness
        for model_key, region in self.SOVEREIGNTY_MAP.items():
            if model_key in key:
                return region
        
        return "Global/Unknown"

    def calculate_green_impact(self, original_len: int, optimized_len: int):
        """
        Calculates the estimated savings in terms of tokens and CO2.
        Assumption: 1 optimized prompt saves 4 failed manual attempts.
        
        Returns:
            dict: {
                "tokens_saved": int,
                "co2_saved_g": float
            }
        """
        # 1. Estimate tokens (Approximation: 1 char ~= 0.25 tokens, or here just usage raw length as proxy for simplicity if preferred, 
        # but let's assume 'len' inputs are character counts, so we divide by 4 to get tokens roughly? 
        # The user prompt implies using 'len' directly in the formula: (4 * original_len) - optimized_len. 
        # We will stick strictly to the user's requested formula for 'tokens'.
        
        # Scenario without tool: User tries 4 times with the original vague prompt
        tokens_without_tool = 4 * original_len
        
        # Scenario with tool: User executes 1 optimized prompt
        tokens_with_tool = optimized_len
        
        tokens_saved = tokens_without_tool - tokens_with_tool
        
        # Avoid negative savings if optimized prompt is HUGE (though unlikely to exceed 4x original)
        if tokens_saved < 0:
            tokens_saved = 0

        # 2. Calculate CO2
        co2_saved = (tokens_saved / 1000) * self.CO2_PER_1000_TOKENS
        
        return {
            "tokens_saved": tokens_saved,
            "co2_saved_g": round(co2_saved, 5) # Round for clean output
        }

# Local Test
if __name__ == "__main__":
    calc = ImpactCalculator()
    
    model = "Mistral-Large"
    region = calc.get_sovereignty(model)
    print(f"Model: {model}, Region: {region}")
    
    # Example: User wrote 50 chars. Optimized is 100 chars.
    # Without tool: 4 * 50 = 200 tokens used.
    # With tool: 100 tokens used.
    # Saved: 100 tokens.
    impact = calc.calculate_green_impact(50, 100)
    print(f"Impact: {impact}")
