from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    MISTRAL_API_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"
    PORT: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()
