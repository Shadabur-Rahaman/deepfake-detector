"""Authentication routes backed by the local SQLite user store."""

import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator

from . import local_store as store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    remember_me: bool = False


class UserRegister(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: str
    full_name: str
    phone: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v is None or v == "":
            return v
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        issues = store.password_issues(v)
        if issues:
            raise ValueError("Password must include: " + "; ".join(issues))
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict
    refresh_token: Optional[str] = None


class RefreshBody(BaseModel):
    refresh_token: str


def _tokens(user: dict) -> TokenResponse:
    tokens = store.create_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type="bearer",
        expires_in=tokens["expires_in"],
        refresh_token=tokens.get("refresh_token"),
        user=tokens["user"],
    )


def _user_from_header(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = store.decode_access(authorization.split(" ", 1)[1].strip())
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = store.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


class VerifyBody(BaseModel):
    signup_id: Optional[str] = None
    challenge_id: Optional[str] = None
    email_code: str
    sms_code: Optional[str] = None


class ResendBody(BaseModel):
    signup_id: Optional[str] = None
    challenge_id: Optional[str] = None
    channel: str = "email"


class ForgotBody(BaseModel):
    email: EmailStr


class ResetBody(BaseModel):
    reset_id: str
    code: str
    new_password: str


@router.get("/policy")
async def auth_policy():
    return store.password_policy()


@router.post("/register")
async def register(user_data: UserRegister):
    username = user_data.username or str(user_data.email).split("@")[0]
    try:
        started = store.start_signup(
            str(user_data.email),
            username,
            user_data.full_name,
            user_data.password,
            user_data.phone,
        )
        return {"needs_verification": True, **started}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Registration error: %s", e)
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}") from e


@router.post("/register/verify", response_model=TokenResponse)
async def register_verify(body: VerifyBody):
    try:
        tokens = store.confirm_signup(body.signup_id, body.email_code, body.sms_code)
        return TokenResponse(
            access_token=tokens["access_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            refresh_token=tokens.get("refresh_token"),
            user=tokens["user"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/register/resend")
async def register_resend(body: ResendBody):
    try:
        return store.resend_signup_otp(body.signup_id, body.channel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/login")
async def login(user_credentials: UserLogin):
    try:
        return store.start_login(
            user_credentials.password,
            email=str(user_credentials.email) if user_credentials.email else None,
            phone=user_credentials.phone,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    except Exception as e:
        logger.error("Login error: %s", e)
        raise HTTPException(status_code=500, detail=f"Login failed: {e}") from e


@router.post("/login/verify", response_model=TokenResponse)
async def login_verify(body: VerifyBody):
    cid = body.challenge_id or body.signup_id
    if not cid:
        raise HTTPException(status_code=400, detail="Missing challenge_id")
    try:
        tokens = store.confirm_login(cid, body.email_code, body.sms_code)
        return TokenResponse(
            access_token=tokens["access_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            refresh_token=tokens.get("refresh_token"),
            user=tokens["user"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/login/resend")
async def login_resend(body: ResendBody):
    cid = body.challenge_id or body.signup_id
    if not cid:
        raise HTTPException(status_code=400, detail="Missing challenge_id")
    try:
        return store.resend_login_otp(cid, body.channel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/password/forgot")
async def password_forgot(body: ForgotBody):
    try:
        return store.start_password_reset(str(body.email))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/password/reset")
async def password_reset(body: ResetBody):
    try:
        return store.confirm_password_reset(body.reset_id, body.code, body.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/refresh")
async def refresh(body: RefreshBody):
    try:
        tokens = store.rotate_refresh(body.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.get("/me")
async def me(authorization: Optional[str] = Header(None)):
    return _user_from_header(authorization)


@router.post("/logout")
async def logout(body: Optional[RefreshBody] = None, authorization: Optional[str] = Header(None)):
    _user_from_header(authorization)
    if body and body.refresh_token:
        store.revoke_refresh(body.refresh_token)
    return {"message": "Successfully logged out"}


class ApiKeyBody(BaseModel):
    name: str = "default"


@router.post("/api-keys")
async def create_api_key(body: ApiKeyBody, authorization: Optional[str] = Header(None)):
    user = _user_from_header(authorization)
    return store.create_api_key(user["id"], body.name)


@router.get("/api-keys")
async def list_api_keys(authorization: Optional[str] = Header(None)):
    user = _user_from_header(authorization)
    return {"keys": store.list_api_keys(user["id"])}


@router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: str, authorization: Optional[str] = Header(None)):
    user = _user_from_header(authorization)
    if not store.delete_api_key(user["id"], key_id):
        raise HTTPException(status_code=404, detail="Key not found")
    return {"deleted": True}


@router.get("/health")
async def auth_health():
    store.init_db()
    return {"status": "healthy", "service": "authentication"}
