from pydantic import BaseModel, Field
from datetime import datetime


class TemplateCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    template_text: str = Field(..., min_length=1, max_length=4000)
    target_model: str = "mistral_2"
    category: str = "general"
    is_public: bool = False


class TemplateRead(BaseModel):
    id: int
    title: str
    description: str | None
    template_text: str
    target_model: str
    category: str
    is_public: bool
    is_mine: bool
    usage_count: int
    created_at: datetime
