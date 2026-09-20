from datetime import datetime, timedelta
from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, Request, status
# pyrefly: ignore [missing-import]
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.config import get_settings

# ---------------------------------------------------------------------------
# Password hashing (Argon2 via passlib)
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
# Used for OpenAPI /docs Authorize button and as Bearer fallback for tests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def create_access_token(subject: int, expires_minutes: Optional[int] = None) -> str:
    """Create a short-lived JWT access token."""
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes if expires_minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(subject), "type": "access", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: int) -> str:
    """Create a long-lived JWT refresh token."""
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _decode_token(token: str) -> Optional[int]:
    """Decode a JWT and return the user_id (sub), or None on failure."""
    try:
        settings = get_settings()
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            return None
        return int(user_id_str)
    except (JWTError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Auth dependency — reads HttpOnly cookie first, then Bearer header fallback
# ---------------------------------------------------------------------------
def get_current_user(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the authenticated user.

    Priority:
      1. Bearer Authorization header (explicitly provided — takes precedence)
      2. HttpOnly cookie ``access_token`` (browser / production path)

    Raises HTTP 401 if neither is present or the token is invalid/expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    settings = get_settings()

    # 1. Explicit Bearer header takes precedence (API clients, TestClient)
    token: Optional[str] = bearer_token

    # 2. Fall back to HttpOnly cookie (browser clients)
    if not token:
        token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)

    if not token:
        raise credentials_exception

    user_id = _decode_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
