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
    original_text: str
    optimized_prompt: str
    ai_model_used: str
    green_score: float
    sovereignty_location: str

class PromptHistoryRead(PromptResponse):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
