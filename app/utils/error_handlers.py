from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from gotrue.errors import AuthApiError


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
