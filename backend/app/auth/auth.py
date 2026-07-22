import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "shopease-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given password."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if the plain password matches the hashed one."""
    return pwd_context.verify(plain, hashed)


def create_access_token(email: str, role: str) -> str:
    """Create a signed JWT containing the user's email and role."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _make_credentials_error() -> HTTPException:
    """Return a 401 HTTPException for invalid or missing credentials."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="We couldn't verify your identity. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the JWT and return the matching User, or raise 401."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise _make_credentials_error()
    except JWTError:
        raise _make_credentials_error()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise _make_credentials_error()
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Raise 403 if the authenticated user is not an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available to our team. Please contact support if you need help.",
        )
    return current_user


async def require_customer(current_user: User = Depends(get_current_user)) -> User:
    """Raise 403 if the authenticated user is not a customer."""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available to customers.",
        )
    return current_user
