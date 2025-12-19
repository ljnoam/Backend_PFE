from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Prompt Schemas ---
class PromptRequest(BaseModel):
    input_text: str
    target_model: str = "gpt-3.5-turbo" # Default model

class PromptResponse(BaseModel):
    original_intent: str
    optimized_prompt: str
    target_model: str
    green_data: Optional[dict] = None
    sovereignty_data: Optional[dict] = None

class PromptHistoryRead(PromptResponse):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    total_prompts: int
    total_tokens_saved: int
    total_co2_saved: float
    model_usage: dict
