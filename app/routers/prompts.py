from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from supabase import Client

from app.dependencies import get_supabase, get_current_user
from app.limiter import limiter
from app.schemas.prompts import PromptRequest, PromptResponse, PromptHistoryRead, UserStatsResponse
from app.services import anonymizer, llm_engine, impact_calculator

router = APIRouter()


@limiter.limit("20/minute")
@router.post("/generate", response_model=PromptResponse)
async def generate_prompt(
    request: Request,
    data: PromptRequest,
    user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Main route: anonymize PII → optimize with Mistral → calculate Green IT & sovereignty → save to history."""
    # 1. Anonymize PII
    anonymized_text = anonymizer.scrub_pii(data.input_text)

    # 2. Optimize prompt via LLM
    llm_result = await llm_engine.rewrite_prompt(anonymized_text, data.target_model)
    optimized_prompt = llm_result["optimized_prompt"]
    reasoning = llm_result["reasoning"]

    # 3. Calculate green impact
    # Green impact is measured from the original (pre-anonymization) intent.
    # This reflects the real user intent length, not the PII-redacted version.
    green_data = impact_calculator.calculate_green_impact(
        original_text=data.input_text,
        optimized_text=optimized_prompt,
        model_name=data.target_model.value,
    )

    # 4. Get sovereignty data
    sovereignty_data = impact_calculator.get_sovereignty_data(data.target_model.value)

    # 5. Save to history
    try:
        supabase.table("prompt_history").insert({
            "user_id": str(user.id),
            "original_intent": data.input_text,
            "optimized_prompt": optimized_prompt,
            "target_model": data.target_model.value,
            "green_data": green_data.model_dump(),
            "sovereignty_data": sovereignty_data.model_dump(),
            "ai_reasoning": reasoning,
        }).execute()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to save prompt to history."
        )

    return PromptResponse(
        original_intent=data.input_text,
        optimized_prompt=optimized_prompt,
        target_model=data.target_model.value,
        green_data=green_data,
        sovereignty_data=sovereignty_data,
        ai_reasoning=reasoning,
    )


@router.get("/history", response_model=list[PromptHistoryRead])
async def get_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Return user's prompt history, newest first."""
    result = (
        supabase.table("prompt_history")
        .select("*")
        .eq("user_id", str(user.id))
        .order("created_at", desc=True)
        .range(skip, skip + limit - 1)
        .execute()
    )
    return result.data


@router.get("/stats", response_model=UserStatsResponse)
async def get_stats(
    user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Return aggregated statistics for the authenticated user."""
    result = (
        supabase.table("prompt_history")
        .select("green_data,target_model")
        .eq("user_id", str(user.id))
        .execute()
    )
    rows = result.data

    total_prompts = len(rows)
    total_tokens_saved = 0
    total_co2_saved = 0.0
    model_usage: dict[str, int] = {}

    for row in rows:
        green = row.get("green_data") or {}
        total_tokens_saved += green.get("tokens_saved", 0)
        total_co2_saved += green.get("co2_saved_g", 0.0)
        model = row.get("target_model", "unknown")
        model_usage[model] = model_usage.get(model, 0) + 1

    return UserStatsResponse(
        total_prompts=total_prompts,
        total_tokens_saved=total_tokens_saved,
        total_co2_saved=round(total_co2_saved, 4),
        model_usage=model_usage,
    )
