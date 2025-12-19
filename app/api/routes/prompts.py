from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import PromptRequest, PromptResponse
from app.models.db import PromptHistory
from app.services.anonymizer import AnonymizerService
from app.services.llm_engine import rewrite_prompt
from app.services.impact_calculator import ImpactCalculator

router = APIRouter()

# Instantiate services
anonymizer_service = AnonymizerService()

impact_calculator = ImpactCalculator()

@router.post("/generate", response_model=PromptResponse)
async def generate_prompt(request: PromptRequest, db: Session = Depends(get_db)):
    """
    Main pipeline:
    1. Anonymize user intent (remove PII).
    2. Optimize prompt via LLM Engine (mock).
    3. Calculate Green Score & Sovereignty.
    4. Save to Database.
    5. Return result.
    """
    
    # 1. Anonymize
    scrubbed_intent = anonymizer_service.scrub_pii(request.input_text)
    
    # 2. Optimize
    optimized_text = await rewrite_prompt(scrubbed_intent, request.target_model)
    
    # 3. Calculate Impact
    # We use the length of the SCRUBBED intent for calculation to be consistent with what the model actually sees,
    # or the original to reflect user effort. Let's use scrubbed to be safe, or original based on "user typing effort".
    # Let's use the actual length effectively processed.
    original_len = len(request.input_text)
    optimized_len = len(optimized_text)
    
    impact_data = impact_calculator.calculate_green_impact(original_len, optimized_len)
    sovereignty = impact_calculator.get_sovereignty(request.target_model)
    
    # 4. Save History to DB
    new_prompt = PromptHistory(
        input_text=scrubbed_intent, 
        optimized_prompt=optimized_text,
        ai_model_used=request.target_model,
        green_score=impact_data["tokens_saved"],
        sovereignty_location=sovereignty
    )
    
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    # 5. Return Response
    return PromptResponse(
        original_text=scrubbed_intent, # Returning scrubbed as 'original' for display to show what was used
        optimized_prompt=optimized_text,
        ai_model_used=request.target_model,
        green_score=impact_data["tokens_saved"], # The float field in schema matches this
        sovereignty_location=sovereignty
    )
