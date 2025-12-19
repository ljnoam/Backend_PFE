from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine_kwargs = {}

if SQLALCHEMY_DATABASE_URL:
    # Render provides 'postgres://', but SQLAlchemy requires 'postgresql://'
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Production / Supabase checks
    engine_kwargs["pool_pre_ping"] = True
    
    # Force SSL for Supabase if needed
    if "supabase" in SQLALCHEMY_DATABASE_URL or "render" in SQLALCHEMY_DATABASE_URL:
        engine_kwargs["connect_args"] = {"sslmode": "require"}
else:
    # Fallback to local SQLite for development
    SQLALCHEMY_DATABASE_URL = "sqlite:///./local_dev.db"
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, **engine_kwargs
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
