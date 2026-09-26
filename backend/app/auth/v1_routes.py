"""Production auth routes: register, login, refresh, me, API keys."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from . import local_store as store

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    full_name: str = Field(min_length=2, max_length=120)
    username: Optional[str] = None
    phone: Optional[str] = None


class LoginBody(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    remember_me: bool = False


class RefreshBody(BaseModel):
    refresh_token: str


class ApiKeyBody(BaseModel):
    name: str = Field(default="default", max_length=80)


def _bearer_user(authorization: Optional[str]) -> dict:
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
async def policy():
    return store.password_policy()


@router.post("/register")
async def register(body: RegisterBody):
    username = (body.username or body.email.split("@")[0]).lower()
    try:
        started = store.start_signup(body.email, username, body.full_name, body.password, body.phone)
        return {"needs_verification": True, **started}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/register/verify")
async def register_verify(body: VerifyBody):
    sid = body.signup_id or body.challenge_id
    try:
        return store.confirm_signup(sid, body.email_code, body.sms_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/register/resend")
async def register_resend(body: ResendBody):
    sid = body.signup_id or body.challenge_id
    try:
        return store.resend_signup_otp(sid, body.channel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/login")
async def login(body: LoginBody, request: Request):
    try:
        return store.start_login(body.password, email=str(body.email) if body.email else None, phone=body.phone)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.post("/login/verify")
async def login_verify(body: VerifyBody):
    cid = body.challenge_id or body.signup_id
    try:
        return store.confirm_login(cid, body.email_code, body.sms_code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/login/resend")
async def login_resend(body: ResendBody):
    cid = body.challenge_id or body.signup_id
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
        return store.rotate_refresh(body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.post("/logout")
async def logout(body: Optional[RefreshBody] = None, authorization: Optional[str] = Header(None)):
    _bearer_user(authorization)
    if body and body.refresh_token:
        store.revoke_refresh(body.refresh_token)
    return {"message": "Logged out"}


@router.get("/me")
async def me(authorization: Optional[str] = Header(None)):
    return _bearer_user(authorization)


@router.post("/api-keys")
async def create_key(body: ApiKeyBody, authorization: Optional[str] = Header(None)):
    user = _bearer_user(authorization)
    created = store.create_api_key(user["id"], body.name)
    return created


@router.get("/api-keys")
async def list_keys(authorization: Optional[str] = Header(None)):
    user = _bearer_user(authorization)
    return {"keys": store.list_api_keys(user["id"])}


@router.delete("/api-keys/{key_id}")
async def delete_key(key_id: str, authorization: Optional[str] = Header(None)):
    user = _bearer_user(authorization)
    if not store.delete_api_key(user["id"], key_id):
        raise HTTPException(status_code=404, detail="Key not found")
    return {"deleted": True}
