import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth import hash_password, verify_password, create_access_token, require_admin
from app.db.database import get_db
from app.db.models import PasswordResetToken, User
from app.models.schema import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    PromoteRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

RESET_TOKEN_EXPIRE_HOURS = 1


async def get_user_by_email(email: str, db: AsyncSession):
    """Return a User by email, or None if not found."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(data: UserCreate, db: AsyncSession) -> User:
    """Insert a new customer account with a hashed password and return the saved record."""
    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
        role="customer",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_reset_token(email: str, db: AsyncSession) -> PasswordResetToken:
    """Generate a secure reset token with a 1-hour expiry and persist it."""
    expires_at = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    record = PasswordResetToken(
        token=secrets.token_urlsafe(32),
        email=email,
        expires_at=expires_at,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def fetch_reset_token(token: str, db: AsyncSession):
    """Return the PasswordResetToken record for the given token, or None."""
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    )
    return result.scalar_one_or_none()


@router.post("/register", response_model=Token, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new customer account and return a JWT access token."""
    if await get_user_by_email(data.email, db):
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists. Please log in instead.",
        )
    user = await create_user(data, db)
    return Token(access_token=create_access_token(user.email, user.role))


@router.post("/login", response_model=Token, status_code=200)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Log in with email (username field) and password, and return a JWT token."""
    user = await get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="We couldn't log you in. Please check your email and password and try again.",
        )
    return Token(access_token=create_access_token(user.email, user.role))


@router.post("/forgot-password", response_model=ForgotPasswordResponse, status_code=200)
async def forgot_password(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Generate a password reset token. In production this token would be emailed."""
    user = await get_user_by_email(data.email, db)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="We couldn't find an account with that email. Please double-check and try again.",
        )
    record = await create_reset_token(data.email, db)
    return ForgotPasswordResponse(reset_token=record.token, expires_at=record.expires_at)


@router.post("/reset-password", response_model=Token, status_code=200)
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset the user's password with a valid token and return a fresh JWT."""
    record = await fetch_reset_token(data.token, db)
    if record is None or record.used:
        raise HTTPException(
            status_code=400,
            detail="This reset link is invalid or has already been used. Please request a new one.",
        )
    if record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="This reset link has expired. Please request a new one.",
        )
    user = await get_user_by_email(record.email, db)
    user.hashed_password = hash_password(data.new_password)
    record.used = True
    await db.commit()
    await db.refresh(user)
    return Token(access_token=create_access_token(user.email, user.role))


@router.post("/promote", response_model=UserResponse, status_code=200)
async def promote_user(
    data: PromoteRequest,
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Change a user's role — admin only."""
    user = await get_user_by_email(data.email, db)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail=f"We couldn't find an account for {data.email}. Please double-check the email and try again.",
        )
    user.role = data.role
    await db.commit()
    await db.refresh(user)
    return user
