from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers import auth, prompts, models, templates
from app.utils.error_handlers import register_error_handlers

app = FastAPI(
    title="PromptOptim API",
    description="L'Architecte de Prompts Eco-efficient & Souverain",
    version="5.0.0",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please slow down."})

register_error_handlers(app)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(prompts.router, prefix="/api", tags=["Prompts"])
app.include_router(models.router, prefix="/api", tags=["Models"])
app.include_router(templates.router, prefix="/api", tags=["Templates"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "project": "PromptOptim", "version": "5.0.0"}
