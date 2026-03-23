from fastapi import APIRouter, Depends, HTTPException, Request, status
from supabase import Client

from app.dependencies import get_supabase, get_supabase_admin, get_current_user
from app.config import settings
from app.limiter import limiter
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)

router = APIRouter()


@limiter.limit("5/minute")
@router.post("/register", status_code=201, response_model=MessageResponse)
async def register(request: Request, data: RegisterRequest, supabase: Client = Depends(get_supabase)):
    """Register a new user. Supabase sends verification email automatically."""
    supabase.auth.sign_up({"email": data.email, "password": data.password})
    return {"message": "Registration successful. Please check your email to verify your account."}


@limiter.limit("10/minute")
@router.post("/login", response_model=TokenResponse)
async def login(request: Request, data: LoginRequest, supabase: Client = Depends(get_supabase)):
    """Login with email + password. Returns Supabase JWT tokens."""
    response = supabase.auth.sign_in_with_password({"email": data.email, "password": data.password})
    session = response.session
    user_obj = response.user
    if not session or not user_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return TokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type="bearer",
        expires_in=session.expires_in,
        user={"id": str(user_obj.id), "email": user_obj.email},
    )


@limiter.limit("10/minute")
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, data: RefreshRequest, supabase: Client = Depends(get_supabase)):
    """Renew access token using refresh token."""
    try:
        response = supabase.auth.refresh_session(data.refresh_token)
        session = response.session
        return TokenResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer",
            expires_in=session.expires_in,
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post("/logout", response_model=MessageResponse)
async def logout(
    user=Depends(get_current_user),
    supabase_admin: Client = Depends(get_supabase_admin),
):
    """Logout — invalidates session on Supabase side."""
    try:
        supabase_admin.auth.admin.sign_out(str(user.id))
    except Exception:
        pass
    return {"message": "Logged out successfully"}


@limiter.limit("3/minute")
@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: Request, data: ForgotPasswordRequest, supabase: Client = Depends(get_supabase)):
    """Request password reset email. Always returns 200 to prevent enumeration."""
    try:
        supabase.auth.reset_password_email(
            data.email,
            {"redirect_to": f"{settings.FRONTEND_URL}/reset-password"},
        )
    except Exception:
        pass
    return {"message": "If this email is registered, you will receive a reset link."}


@limiter.limit("5/minute")
@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: Request, data: ResetPasswordRequest, supabase: Client = Depends(get_supabase)):
    """Reset password using tokens from Supabase redirect URL fragment."""
    try:
        supabase.auth.set_session(data.access_token, data.refresh_token)
        supabase.auth.update_user({"password": data.new_password})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    return {"message": "Password updated successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(user=Depends(get_current_user)):
    """Return currently authenticated user info."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        created_at=user.created_at if user.created_at else None,
    )


@router.delete("/me", status_code=204)
async def delete_account(
    user=Depends(get_current_user),
    supabase_admin: Client = Depends(get_supabase_admin),
):
    """Delete account. CASCADE removes all data from profiles, history, templates."""
    try:
        supabase_admin.auth.admin.delete_user(str(user.id))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete account.")
