from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.routes import prompts, auth

# Create DB Tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PromptOptim API",
    description="API for optimizing prompts, anonymizing PII, and calculating Green Score.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(prompts.router, prefix="/api", tags=["Prompts"])
app.include_router(auth.router, tags=["Authentication"])

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify backend status and database connectivity.
    """
    try:
        # Perform a simple query to check DB connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "project": "PromptOptim", "database": "connected"}
    except Exception as e:
        # Log the error (in a real app, use a logger)
        print(f"Health Check Failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
