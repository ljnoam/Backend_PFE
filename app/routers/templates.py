from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.dependencies import get_supabase, get_current_user
from app.schemas.templates import TemplateCreate, TemplateRead

router = APIRouter()


@router.get("/templates", response_model=list[TemplateRead])
async def list_templates(
    category: str | None = Query(default=None),
    mine_only: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Get templates: own + public (via RLS), with optional category filter."""
    query = supabase.table("prompt_templates").select("*")

    if mine_only:
        query = query.eq("user_id", str(user.id))
    # If not mine_only, RLS policy handles filtering (own + public)

    if category:
        query = query.eq("category", category)

    try:
        result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch templates."
        )

    return [
        {**row, "is_mine": row.get("user_id") == str(user.id)}
        for row in result.data
    ]


@router.post("/templates", response_model=TemplateRead, status_code=201)
async def create_template(
    data: TemplateCreate,
    user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Create a new prompt template for the authenticated user."""
    result = supabase.table("prompt_templates").insert({
        "user_id": str(user.id),
        "title": data.title,
        "description": data.description,
        "template_text": data.template_text,
        "target_model": data.target_model.value,
        "category": data.category,
        "is_public": data.is_public,
    }).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to create template."
        )

    row = result.data[0]
    return {**row, "is_mine": True}


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    """Delete own template. Returns 404 if not found or not owned by user."""
    # Check ownership first
    check = (
        supabase.table("prompt_templates")
        .select("id")
        .eq("id", template_id)
        .eq("user_id", str(user.id))
        .execute()
    )
    if not check.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    delete_result = supabase.table("prompt_templates").delete().eq("id", template_id).execute()
    if not delete_result.data:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to delete template."
        )
