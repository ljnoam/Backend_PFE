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

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify backend status.
    """
    return {"status": "ok", "project": "PromptOptim"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
