from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
try:
    from gotrue.errors import AuthApiError
except ImportError:
    try:
        from supabase_auth.errors import AuthApiError
    except ImportError:
        # Fallback for other potential import paths if needed
        from supabase.auth.errors import AuthApiError



def register_error_handlers(app: FastAPI):
    @app.exception_handler(AuthApiError)
    async def supabase_auth_error_handler(request: Request, exc: AuthApiError):
        msg = str(exc)
        if "User already registered" in msg:
            return JSONResponse(status_code=400, content={"detail": "Email already registered"})
        if "Invalid login credentials" in msg:
            return JSONResponse(status_code=401, content={"detail": "Invalid email or password"})
        if "Email not confirmed" in msg:
            return JSONResponse(status_code=403, content={"detail": "Email not verified"})
        return JSONResponse(status_code=400, content={"detail": msg})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
