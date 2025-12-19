from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas import PromptRequest, PromptResponse, PromptHistoryRead, UserStatsResponse
from app.models.db import PromptHistory
from app.models.user import User
from app.services.anonymizer import AnonymizerService
from app.services.llm_engine import rewrite_prompt
from app.services.impact_calculator import ImpactCalculator
from app.core.security import get_current_user

router = APIRouter()

# Instantiate services
anonymizer_service = AnonymizerService()
impact_calculator = ImpactCalculator()

@router.post("/generate", response_model=PromptResponse)
async def generate_prompt(
    request: PromptRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Main pipeline:
    1. Anonymize user intent (remove PII).
    2. Optimize prompt via LLM Engine.
    3. Calculate Green Score & Sovereignty.
    4. Save to Database linked to user.
    5. Return result.
    """
    
    # 1. Anonymize
    scrubbed_intent = anonymizer_service.scrub_pii(request.input_text)
    
    # 2. Optimize
    optimized_text = await rewrite_prompt(scrubbed_intent, request.target_model)
    
    # 3. Calculate Impact
    original_len = len(request.input_text)
    optimized_len = len(optimized_text)
    
    impact_data = impact_calculator.calculate_green_impact(original_len, optimized_len)
    # impact_data example: {"tokens_saved": 0.5, "co2_avoided": ...}
    
    sovereignty = impact_calculator.get_sovereignty(request.target_model)
    # sovereignty example: "UE" -> we might want to wrap this in a dict for consistency with JSON schema if needed,
    # but existing code returned a string. The DB wants JSON. Let's wrap it.
    sovereignty_data = {"location": sovereignty}
    
    # 4. Save History to DB
    new_prompt = PromptHistory(
        user_id=current_user.id,
        original_intent=scrubbed_intent, 
        optimized_prompt=optimized_text,
        target_model=request.target_model,
        green_data=impact_data,
        sovereignty_data=sovereignty_data
    )
    
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    # 5. Return Response
    return PromptResponse(
        original_intent=scrubbed_intent,
        optimized_prompt=optimized_text,
        target_model=request.target_model,
        green_data=impact_data,
        sovereignty_data=sovereignty_data
    )

@router.get("/history", response_model=List[PromptHistoryRead])
def get_history(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve prompt history for the current user.
    """
    prompts = db.query(PromptHistory)\
        .filter(PromptHistory.user_id == current_user.id)\
        .order_by(PromptHistory.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return prompts

@router.get("/stats", response_model=UserStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Calculate global statistics for the current user.
    """
    prompts = db.query(PromptHistory).filter(PromptHistory.user_id == current_user.id).all()
    
    total_prompts = len(prompts)
    total_tokens_saved = 0
    total_co2_saved = 0.0
    model_usage = {}
    
    for p in prompts:
        # Aggregate Green Data
        if p.green_data:
            # Check if green_data is a dict (json type) or string (if db migration failed)
            # Assuming standard behavior of SQLModel/Pydantic with JSON column
            data = p.green_data
            if isinstance(data, dict):
                total_tokens_saved += data.get("tokens_saved", 0)
                total_co2_saved += data.get("co2_saved_g", 0.0)
        
        # Aggregate Model Usage
        model = p.target_model
        if model:
             model_usage[model] = model_usage.get(model, 0) + 1
             
    return UserStatsResponse(
        total_prompts=total_prompts,
        total_tokens_saved=total_tokens_saved,
        total_co2_saved=round(total_co2_saved, 4),
        model_usage=model_usage
    )
