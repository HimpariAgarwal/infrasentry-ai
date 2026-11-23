import os
import hmac
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token"
)

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30


def get_secret_key():
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=503,
            detail="JWT_SECRET_KEY is not configured securely."
        )
    return secret


def authenticate_user(username: str, password: str):
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        raise HTTPException(
            status_code=503,
            detail="Admin credentials are not configured."
        )

    username_valid = hmac.compare_digest(
        username.encode("utf-8"),
        admin_username.encode("utf-8")
    )

    password_valid = hmac.compare_digest(
        password.encode("utf-8"),
        admin_password.encode("utf-8")
    )

    if not (username_valid and password_valid):
        return False

    return True


def create_access_token(username: str):
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "iat": now,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=ALGORITHM
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            get_secret_key(),
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")

        if not username:
            raise credentials_exception

        return {"username": username}

    except jwt.InvalidTokenError:
        raise credentials_exception


@auth_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(form_data.username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60,
    }


@auth_router.get("/me")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "authenticated": True,
        "user": current_user["username"],
        "message": "JWT authentication successful.",
    }


@auth_router.get("/secure-check")
async def secure_check(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "message": "Protected endpoint accessed successfully.",
        "user": current_user["username"],
    }
