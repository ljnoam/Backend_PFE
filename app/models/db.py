from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PromptHistory(Base):
    __tablename__ = "prompt_history"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=False)
    ai_model_used = Column(String, nullable=False)  # ex: 'gpt-4', 'mistral-large'
    green_score = Column(Float, nullable=True)     # ex: 0.8 (saved 80% tokens vs retry)
    sovereignty_location = Column(String, nullable=True) # ex: 'UE', 'USA'
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Link to user if we have auth later
    # user_id = Column(Integer, ForeignKey("users.id"))
    # owner = relationship("User", back_populates="prompts")
