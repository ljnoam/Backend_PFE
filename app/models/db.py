from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class PromptHistory(Base):
    __tablename__ = "prompt_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_intent = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=False)
    target_model = Column(String, nullable=False)  # ex: 'gpt-4', 'mistral-large'
    green_data = Column(JSON, nullable=True)     # Stores {"green_score": 0.8, "tokens_saved": ...}
    sovereignty_data = Column(JSON, nullable=True) # Stores {"location": "UE", ...}
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="prompts")
