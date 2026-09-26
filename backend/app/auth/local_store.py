"""SQLite user + API-key store. No Redis. No SQLAlchemy graph."""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import jwt

try:
    from passlib.context import CryptContext
    _pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    _pwd = None

_lock = threading.Lock()
_DB = Path(os.getenv("AUTH_DB_PATH") or Path(__file__).resolve().parents[3] / "auth_users.db")

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-long-random-string")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
MAX_FAILS = 5
LOCK_MINUTES = 15
PASSWORD_MIN = 12
PASSWORD_MAX = 72
OTP_TTL_MIN = 10
OTP_RESEND_SEC = 60
OTP_MAX_ATTEMPTS = 5


def password_issues(password: str) -> list:
    issues = []
    if not password or len(password) < PASSWORD_MIN:
        issues.append(f"At least {PASSWORD_MIN} characters")
    if len(password or "") > PASSWORD_MAX:
        issues.append(f"At most {PASSWORD_MAX} characters")
    if not any(c.islower() for c in password or ""):
        issues.append("One lowercase letter")
    if not any(c.isupper() for c in password or ""):
        issues.append("One uppercase letter")
    if not any(c.isdigit() for c in password or ""):
        issues.append("One number")
    if not any(c in "!@#$%^&*()_+-=[]{}|;:',.<>?/`~\\\"" for c in password or ""):
        issues.append("One special character (!@#$%^&* etc.)")
    return issues


def password_policy() -> dict:
    from .delivery import delivery_status

    d = delivery_status()
    return {
        "min_length": PASSWORD_MIN,
        "max_length": PASSWORD_MAX,
        "require_lowercase": True,
        "require_uppercase": True,
        "require_number": True,
        "require_special": True,
        "otp_ttl_minutes": OTP_TTL_MIN,
        "otp_resend_seconds": OTP_RESEND_SEC,
        "email_verification": True,
        "sms_optional": True,
        **d,
    }


def normalize_phone(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    digits = "".join(ch for ch in raw.strip() if ch.isdigit() or ch == "+")
    if not digits:
        return None
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    if digits.startswith("+"):
        rest = "".join(c for c in digits if c.isdigit())
        if len(rest) < 10 or len(rest) > 15:
            raise ValueError("Enter a valid mobile number with country code")
        return "+" + rest
    only = "".join(c for c in digits if c.isdigit())
    if len(only) == 10:
        return "+91" + only
    if len(only) == 11 and only.startswith("0"):
        return "+91" + only[1:]
    if len(only) == 12 and only.startswith("91"):
        return "+" + only
    raise ValueError("Enter a valid mobile number (10 digits or +country code)")


def _conn() -> sqlite3.Connection:
    _DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_DB), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with _lock:
        con = _conn()
        try:
            con.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    roles TEXT NOT NULL DEFAULT 'user',
                    failed_logins INTEGER NOT NULL DEFAULT 0,
                    locked_until TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT
                );
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    prefix TEXT NOT NULL,
                    key_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    last_used TEXT
                );
                CREATE TABLE IF NOT EXISTS login_challenges (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    email_code_hash TEXT,
                    sms_code_hash TEXT,
                    email_sent_at TEXT,
                    sms_sent_at TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS password_resets (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    code_hash TEXT NOT NULL,
                    sent_at TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pending_signups (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    phone TEXT,
                    username TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    email_code_hash TEXT,
                    sms_code_hash TEXT,
                    email_sent_at TEXT,
                    sms_sent_at TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    email_ok INTEGER NOT NULL DEFAULT 0,
                    sms_ok INTEGER NOT NULL DEFAULT 0,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            cols = {r[1] for r in con.execute("PRAGMA table_info(users)")}
            if "email_verified" not in cols:
                con.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 1")
            if "phone" not in cols:
                con.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            if "phone_verified" not in cols:
                con.execute("ALTER TABLE users ADD COLUMN phone_verified INTEGER NOT NULL DEFAULT 0")
            con.commit()
        finally:
            con.close()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.astimezone(timezone.utc).isoformat() if dt else None


def hash_password(password: str) -> str:
    password = (password or "")[:72]
    if _pwd:
        return _pwd.hash(password)
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2${salt.hex()}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    password = (password or "")[:72]
    if hashed.startswith("pbkdf2$"):
        _, salt_hex, dk_hex = hashed.split("$", 2)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 200_000)
        return secrets.compare_digest(dk.hex(), dk_hex)
    if _pwd:
        try:
            return bool(_pwd.verify(password, hashed))
        except Exception:
            return False
    return False


def _has(row: sqlite3.Row, key: str) -> bool:
    return key in row.keys()


def _row_user(row: sqlite3.Row) -> Dict[str, Any]:
    roles = [r for r in (row["roles"] or "user").split(",") if r]
    email_verified = bool(row["email_verified"]) if _has(row, "email_verified") else True
    phone = row["phone"] if _has(row, "phone") else None
    phone_verified = bool(row["phone_verified"]) if _has(row, "phone_verified") else False
    return {
        "id": row["id"],
        "email": row["email"],
        "username": row["username"],
        "full_name": row["full_name"],
        "fullName": row["full_name"],
        "phone": phone,
        "is_active": bool(row["is_active"]),
        "email_verified": email_verified,
        "phone_verified": phone_verified,
        "roles": roles,
        "permissions": ["detection:create", "detection:read", "try:access"]
        + (["admin:access", "user:manage"] if "admin" in roles else []),
        "created_at": row["created_at"],
        "last_login": row["last_login"],
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    init_db()
    con = _conn()
    try:
        row = con.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
        return dict(row) if row else None
    finally:
        con.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    con = _conn()
    try:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _row_user(row) if row else None
    finally:
        con.close()


def create_user(
    email: str,
    username: str,
    full_name: str,
    password: str,
    roles: str = "user",
    *,
    hashed_password: Optional[str] = None,
    phone: Optional[str] = None,
    email_verified: bool = False,
    phone_verified: bool = False,
) -> Dict[str, Any]:
    init_db()
    issues = password_issues(password) if hashed_password is None else []
    if issues:
        raise ValueError("Password must include: " + "; ".join(issues))
    email = email.lower().strip()
    username = username.lower().strip()
    if get_user_by_email(email):
        raise ValueError("Email already registered")
    uid = str(uuid.uuid4())
    hp = hashed_password or hash_password(password)
    with _lock:
        con = _conn()
        try:
            existing = con.execute(
                "SELECT id FROM users WHERE email = ? OR username = ?", (email, username)
            ).fetchone()
            if existing:
                raise ValueError("Email or username already registered")
            if phone:
                taken = con.execute(
                    "SELECT id FROM users WHERE phone = ? AND phone_verified = 1", (phone,)
                ).fetchone()
                if taken:
                    raise ValueError("Mobile number already registered")
            con.execute(
                """INSERT INTO users (id, email, username, full_name, hashed_password, is_active, roles,
                   failed_logins, created_at, email_verified, phone, phone_verified)
                   VALUES (?, ?, ?, ?, ?, 1, ?, 0, ?, ?, ?, ?)""",
                (
                    uid,
                    email,
                    username,
                    full_name.strip(),
                    hp,
                    roles,
                    _iso(_now()),
                    1 if email_verified else 0,
                    phone,
                    1 if phone_verified else 0,
                ),
            )
            con.commit()
        finally:
            con.close()
    return get_user_by_id(uid)


def record_login_failure(email: str) -> None:
    init_db()
    with _lock:
        con = _conn()
        try:
            row = con.execute("SELECT failed_logins FROM users WHERE email = ?", (email.lower(),)).fetchone()
            if not row:
                return
            fails = int(row["failed_logins"]) + 1
            locked = _iso(_now() + timedelta(minutes=LOCK_MINUTES)) if fails >= MAX_FAILS else None
            con.execute(
                "UPDATE users SET failed_logins = ?, locked_until = ? WHERE email = ?",
                (fails, locked, email.lower()),
            )
            con.commit()
        finally:
            con.close()


def authenticate(email: str, password: str) -> Dict[str, Any]:
    init_db()
    con = _conn()
    try:
        row = con.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
    finally:
        con.close()
    if not row:
        raise ValueError("Incorrect email or password")
    if row["locked_until"]:
        try:
            until = datetime.fromisoformat(row["locked_until"])
            if until > _now():
                raise ValueError("Account temporarily locked. Try again later.")
        except ValueError as e:
            if "locked" in str(e).lower():
                raise
    if not row["is_active"]:
        raise ValueError("Account is deactivated")
    if "email_verified" in row.keys() and not row["email_verified"]:
        raise ValueError("Verify your email before signing in. Check your inbox for the code.")
    if not verify_password(password, row["hashed_password"]):
        record_login_failure(email)
        raise ValueError("Incorrect email or password")
    with _lock:
        con = _conn()
        try:
            con.execute(
                "UPDATE users SET failed_logins = 0, locked_until = NULL, last_login = ? WHERE id = ?",
                (_iso(_now()), row["id"]),
            )
            con.commit()
        finally:
            con.close()
    return get_user_by_id(row["id"])


def create_tokens(user: Dict[str, Any]) -> Dict[str, Any]:
    now = _now()
    access_exp = now + timedelta(minutes=ACCESS_MIN)
    refresh_exp = now + timedelta(days=REFRESH_DAYS)
    access = jwt.encode({"sub": user["id"], "email": user["email"], "roles": user["roles"], "exp": access_exp, "typ": "access"}, SECRET_KEY, algorithm=ALGORITHM)
    refresh_raw = secrets.token_urlsafe(48)
    refresh_hash = hashlib.sha256(refresh_raw.encode()).hexdigest()
    init_db()
    with _lock:
        con = _conn()
        try:
            con.execute(
                "INSERT INTO refresh_tokens (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
                (refresh_hash, user["id"], _iso(refresh_exp)),
            )
            con.commit()
        finally:
            con.close()
    return {
        "access_token": access,
        "refresh_token": refresh_raw,
        "token_type": "bearer",
        "expires_in": ACCESS_MIN * 60,
        "user": user,
    }


def decode_access(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("typ") not in (None, "access"):
            return None
        return payload
    except jwt.PyJWTError:
        return None


def rotate_refresh(refresh_token: str) -> Dict[str, Any]:
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    init_db()
    with _lock:
        con = _conn()
        try:
            row = con.execute("SELECT * FROM refresh_tokens WHERE token_hash = ?", (token_hash,)).fetchone()
            if not row:
                raise ValueError("Invalid refresh token")
            if datetime.fromisoformat(row["expires_at"]) < _now():
                con.execute("DELETE FROM refresh_tokens WHERE token_hash = ?", (token_hash,))
                con.commit()
                raise ValueError("Refresh token expired")
            con.execute("DELETE FROM refresh_tokens WHERE token_hash = ?", (token_hash,))
            con.commit()
            user_id = row["user_id"]
        finally:
            con.close()
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")
    return create_tokens(user)


def revoke_refresh(refresh_token: str) -> None:
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    init_db()
    with _lock:
        con = _conn()
        try:
            con.execute("DELETE FROM refresh_tokens WHERE token_hash = ?", (token_hash,))
            con.commit()
        finally:
            con.close()


def create_api_key(user_id: str, name: str) -> Dict[str, Any]:
    raw = "ifk_" + secrets.token_urlsafe(32)
    prefix = raw[:10]
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    kid = str(uuid.uuid4())
    init_db()
    with _lock:
        con = _conn()
        try:
            con.execute(
                """INSERT INTO api_keys (id, user_id, name, prefix, key_hash, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (kid, user_id, name.strip() or "default", prefix, key_hash, _iso(_now())),
            )
            con.commit()
        finally:
            con.close()
    return {"id": kid, "name": name, "prefix": prefix, "api_key": raw, "created_at": _iso(_now())}


def list_api_keys(user_id: str) -> List[Dict[str, Any]]:
    init_db()
    con = _conn()
    try:
        rows = con.execute(
            "SELECT id, name, prefix, created_at, last_used FROM api_keys WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def delete_api_key(user_id: str, key_id: str) -> bool:
    init_db()
    with _lock:
        con = _conn()
        try:
            cur = con.execute("DELETE FROM api_keys WHERE id = ? AND user_id = ?", (key_id, user_id))
            con.commit()
            return cur.rowcount > 0
        finally:
            con.close()


def user_from_api_key(raw_key: str) -> Optional[Dict[str, Any]]:
    if not raw_key or not raw_key.startswith("ifk_"):
        return None
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    init_db()
    con = _conn()
    try:
        row = con.execute("SELECT user_id FROM api_keys WHERE key_hash = ?", (key_hash,)).fetchone()
        if not row:
            return None
        user_id = row["user_id"]
        con.execute("UPDATE api_keys SET last_used = ? WHERE key_hash = ?", (_iso(_now()), key_hash))
        con.commit()
    finally:
        con.close()
    return get_user_by_id(user_id)


def resolve_identity(authorization: Optional[str], x_api_key: Optional[str]) -> Optional[Dict[str, Any]]:
    env_key = (os.getenv("PUBLIC_API_KEY") or "").strip()
    if x_api_key:
        if env_key and secrets.compare_digest(x_api_key, env_key):
            return {"id": "env", "email": "api-key", "roles": ["service"], "full_name": "Service"}
        user = user_from_api_key(x_api_key)
        if user:
            return user
    if authorization and authorization.lower().startswith("bearer "):
        payload = decode_access(authorization.split(" ", 1)[1].strip())
        if payload and payload.get("sub"):
            return get_user_by_id(payload["sub"])
    return None


def _otp_hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _new_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if len(local) <= 2:
        shown = local[:1] + "*"
    else:
        shown = local[:2] + "*" * (len(local) - 2)
    return f"{shown}@{domain}"


def _mask_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    return "+" + "*" * max(0, len(digits) - 4) + digits[-4:]


def start_signup(email: str, username: str, full_name: str, password: str, phone: Optional[str] = None) -> Dict[str, Any]:
    from .delivery import send_email_otp, send_sms_otp, smtp_configured, twilio_configured

    issues = password_issues(password)
    if issues:
        raise ValueError("Password must include: " + "; ".join(issues))
    email = email.lower().strip()
    username = (username or email.split("@")[0]).lower().strip()
    full_name = (full_name or "").strip()
    if len(full_name) < 2:
        raise ValueError("Enter your full name")
    phone_n = normalize_phone(phone) if phone and phone.strip() else None
    if get_user_by_email(email):
        raise ValueError("Email already registered")
    if not smtp_configured():
        raise ValueError(
            "This server cannot send Gmail/inbox verification yet. "
            "Add SMTP_USER and SMTP_PASSWORD (Gmail App Password) to config.env, then restart the API."
        )
    sms_enabled = bool(phone_n and twilio_configured())
    if phone_n and not sms_enabled:
        logger.warning("Twilio is not configured; skipping SMS OTP and verifying Gmail only")

    signup_id = str(uuid.uuid4())
    email_code = _new_otp()
    sms_code = _new_otp() if sms_enabled else None
    now = _now()
    expires = now + timedelta(minutes=OTP_TTL_MIN)
    init_db()
    with _lock:
        con = _conn()
        try:
            con.execute("DELETE FROM pending_signups WHERE email = ? OR datetime(expires_at) < datetime(?)", (email, _iso(now)))
            con.execute(
                """INSERT INTO pending_signups
                   (id, email, phone, username, full_name, hashed_password, email_code_hash, sms_code_hash,
                    email_sent_at, sms_sent_at, attempts, email_ok, sms_ok, expires_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?)""",
                (
                    signup_id,
                    email,
                    phone_n,
                    username,
                    full_name,
                    hash_password(password),
                    _otp_hash(email_code),
                    _otp_hash(sms_code) if sms_code else None,
                    _iso(now),
                    _iso(now) if sms_code else None,
                    1 if not sms_code else 0,
                    _iso(expires),
                    _iso(now),
                ),
            )
            con.commit()
        finally:
            con.close()

    send_email_otp(email, email_code, full_name)
    if phone_n and sms_code:
        send_sms_otp(phone_n, sms_code)

    return {
        "signup_id": signup_id,
        "email_masked": _mask_email(email),
        "phone_masked": _mask_phone(phone_n) if sms_code else None,
        "sms_required": bool(sms_code),
        "expires_in": OTP_TTL_MIN * 60,
        "resend_in": OTP_RESEND_SEC,
        "message": "Enter the 6-digit code we sent to your Gmail inbox"
        + (" and mobile" if sms_code else "")
        + ".",
    }


def resend_signup_otp(signup_id: str, channel: str = "email") -> Dict[str, Any]:
    from .delivery import send_email_otp, send_sms_otp

    init_db()
    con = _conn()
    try:
        row = con.execute("SELECT * FROM pending_signups WHERE id = ?", (signup_id,)).fetchone()
    finally:
        con.close()
    if not row:
        raise ValueError("Signup session expired. Start again.")
    if datetime.fromisoformat(row["expires_at"]) < _now():
        raise ValueError("Codes expired. Start registration again.")
    channel = (channel or "email").lower()
    sent_col = "email_sent_at" if channel == "email" else "sms_sent_at"
    last = row[sent_col]
    if last:
        last_dt = datetime.fromisoformat(last)
        wait = OTP_RESEND_SEC - int((_now() - last_dt).total_seconds())
        if wait > 0:
            raise ValueError(f"Wait {wait} seconds before requesting another code")
    code = _new_otp()
    now = _now()
    with _lock:
        con = _conn()
        try:
            if channel == "sms":
                if not row["phone"]:
                    raise ValueError("No mobile number on this signup")
                con.execute(
                    "UPDATE pending_signups SET sms_code_hash = ?, sms_sent_at = ?, sms_ok = 0 WHERE id = ?",
                    (_otp_hash(code), _iso(now), signup_id),
                )
            else:
                con.execute(
                    "UPDATE pending_signups SET email_code_hash = ?, email_sent_at = ?, email_ok = 0 WHERE id = ?",
                    (_otp_hash(code), _iso(now), signup_id),
                )
            con.commit()
        finally:
            con.close()
    if channel == "sms":
        send_sms_otp(row["phone"], code)
    else:
        send_email_otp(row["email"], code, row["full_name"])
    return {"ok": True, "resend_in": OTP_RESEND_SEC, "channel": channel}


def confirm_signup(signup_id: str, email_code: str, sms_code: Optional[str] = None) -> Dict[str, Any]:
    init_db()
    email_code = (email_code or "").strip()
    sms_code = (sms_code or "").strip() or None
    with _lock:
        con = _conn()
        try:
            row = con.execute("SELECT * FROM pending_signups WHERE id = ?", (signup_id,)).fetchone()
            if not row:
                raise ValueError("Signup session expired. Start again.")
            if datetime.fromisoformat(row["expires_at"]) < _now():
                con.execute("DELETE FROM pending_signups WHERE id = ?", (signup_id,))
                con.commit()
                raise ValueError("Codes expired. Start registration again.")
            attempts = int(row["attempts"]) + 1
            if attempts > OTP_MAX_ATTEMPTS:
                con.execute("DELETE FROM pending_signups WHERE id = ?", (signup_id,))
                con.commit()
                raise ValueError("Too many incorrect codes. Start registration again.")
            email_ok = secrets.compare_digest(row["email_code_hash"] or "", _otp_hash(email_code))
            sms_needed = bool(row["sms_code_hash"])
            sms_ok = True
            if sms_needed:
                if not sms_code:
                    raise ValueError("Enter the SMS code sent to your mobile")
                sms_ok = secrets.compare_digest(row["sms_code_hash"] or "", _otp_hash(sms_code))
            if not email_ok or not sms_ok:
                con.execute("UPDATE pending_signups SET attempts = ? WHERE id = ?", (attempts, signup_id))
                con.commit()
                left = OTP_MAX_ATTEMPTS - attempts
                raise ValueError(f"Incorrect verification code. {left} attempt(s) left.")
            payload = dict(row)
            con.execute("DELETE FROM pending_signups WHERE id = ?", (signup_id,))
            con.commit()
        finally:
            con.close()

    user = create_user(
        payload["email"],
        payload["username"],
        payload["full_name"],
        password="x",
        hashed_password=payload["hashed_password"],
        phone=payload["phone"],
        email_verified=True,
        phone_verified=bool(payload["sms_code_hash"]),
    )
    return create_tokens(user)


def _load_user_row(*, email: Optional[str] = None, phone: Optional[str] = None) -> sqlite3.Row:
    init_db()
    con = _conn()
    try:
        if email:
            row = con.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
        else:
            phone_n = normalize_phone(phone)
            row = con.execute("SELECT * FROM users WHERE phone = ?", (phone_n,)).fetchone()
        return row
    finally:
        con.close()


def start_login(password: str, email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
    from .delivery import send_email_otp, send_sms_otp, smtp_configured, twilio_configured

    if not email and not phone:
        raise ValueError("Enter your Gmail or mobile number")
    row = _load_user_row(email=email, phone=phone)
    if not row:
        raise ValueError("Incorrect email/mobile or password")
    if row["locked_until"]:
        try:
            until = datetime.fromisoformat(row["locked_until"])
            if until > _now():
                raise ValueError("Account temporarily locked. Try again later.")
        except ValueError as e:
            if "locked" in str(e).lower():
                raise
    if not row["is_active"]:
        raise ValueError("Account is deactivated")
    if "email_verified" in row.keys() and not row["email_verified"]:
        raise ValueError("Verify your email before signing in.")
    if not verify_password(password, row["hashed_password"]):
        record_login_failure(row["email"])
        raise ValueError("Incorrect email/mobile or password")
    if not smtp_configured():
        raise ValueError(
            "Sign-in requires Gmail inbox verification. Set SMTP_USER and SMTP_PASSWORD "
            "(Gmail App Password) in config.env, then restart the API."
        )
    user = _row_user(row)
    sms_needed = bool(user.get("phone") and user.get("phone_verified") and twilio_configured())
    challenge_id = str(uuid.uuid4())
    email_code = _new_otp()
    sms_code = _new_otp() if sms_needed else None
    now = _now()
    init_db()
    with _lock:
        con = _conn()
        try:
            con.execute("DELETE FROM login_challenges WHERE user_id = ? OR datetime(expires_at) < datetime(?)", (user["id"], _iso(now)))
            con.execute(
                """INSERT INTO login_challenges
                   (id, user_id, email_code_hash, sms_code_hash, email_sent_at, sms_sent_at, attempts, expires_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)""",
                (
                    challenge_id,
                    user["id"],
                    _otp_hash(email_code),
                    _otp_hash(sms_code) if sms_code else None,
                    _iso(now),
                    _iso(now) if sms_code else None,
                    _iso(now + timedelta(minutes=OTP_TTL_MIN)),
                    _iso(now),
                ),
            )
            con.commit()
        finally:
            con.close()
    send_email_otp(user["email"], email_code, user.get("full_name") or "")
    if sms_needed and sms_code:
        send_sms_otp(user["phone"], sms_code)
    return {
        "needs_verification": True,
        "challenge_id": challenge_id,
        "signup_id": challenge_id,
        "email_masked": _mask_email(user["email"]),
        "phone_masked": _mask_phone(user["phone"]) if sms_needed else None,
        "sms_required": sms_needed,
        "expires_in": OTP_TTL_MIN * 60,
        "resend_in": OTP_RESEND_SEC,
        "message": "Enter the 6-digit code we sent to your Gmail"
        + (" and mobile" if sms_needed else "")
        + ".",
    }


def resend_login_otp(challenge_id: str, channel: str = "email") -> Dict[str, Any]:
    from .delivery import send_email_otp, send_sms_otp

    init_db()
    con = _conn()
    try:
        row = con.execute("SELECT * FROM login_challenges WHERE id = ?", (challenge_id,)).fetchone()
    finally:
        con.close()
    if not row:
        raise ValueError("Sign-in session expired. Start again.")
    if datetime.fromisoformat(row["expires_at"]) < _now():
        raise ValueError("Codes expired. Sign in again.")
    user = get_user_by_id(row["user_id"])
    if not user:
        raise ValueError("User not found")
    channel = (channel or "email").lower()
    sent_col = "email_sent_at" if channel == "email" else "sms_sent_at"
    last = row[sent_col]
    if last:
        wait = OTP_RESEND_SEC - int((_now() - datetime.fromisoformat(last)).total_seconds())
        if wait > 0:
            raise ValueError(f"Wait {wait} seconds before requesting another code")
    code = _new_otp()
    now = _now()
    with _lock:
        con = _conn()
        try:
            if channel == "sms":
                if not user.get("phone"):
                    raise ValueError("No mobile number on this account")
                con.execute(
                    "UPDATE login_challenges SET sms_code_hash = ?, sms_sent_at = ? WHERE id = ?",
                    (_otp_hash(code), _iso(now), challenge_id),
                )
            else:
                con.execute(
                    "UPDATE login_challenges SET email_code_hash = ?, email_sent_at = ? WHERE id = ?",
                    (_otp_hash(code), _iso(now), challenge_id),
                )
            con.commit()
        finally:
            con.close()
    if channel == "sms":
        send_sms_otp(user["phone"], code)
    else:
        send_email_otp(user["email"], code, user.get("full_name") or "")
    return {"ok": True, "resend_in": OTP_RESEND_SEC, "channel": channel}


def confirm_login(challenge_id: str, email_code: str, sms_code: Optional[str] = None) -> Dict[str, Any]:
    init_db()
    email_code = (email_code or "").strip()
    sms_code = (sms_code or "").strip() or None
    with _lock:
        con = _conn()
        try:
            row = con.execute("SELECT * FROM login_challenges WHERE id = ?", (challenge_id,)).fetchone()
            if not row:
                raise ValueError("Sign-in session expired. Start again.")
            if datetime.fromisoformat(row["expires_at"]) < _now():
                con.execute("DELETE FROM login_challenges WHERE id = ?", (challenge_id,))
                con.commit()
                raise ValueError("Codes expired. Sign in again.")
            attempts = int(row["attempts"]) + 1
            if attempts > OTP_MAX_ATTEMPTS:
                con.execute("DELETE FROM login_challenges WHERE id = ?", (challenge_id,))
                con.commit()
                raise ValueError("Too many incorrect codes. Sign in again.")
            email_ok = secrets.compare_digest(row["email_code_hash"] or "", _otp_hash(email_code))
            sms_needed = bool(row["sms_code_hash"])
            sms_ok = True
            if sms_needed:
                if not sms_code:
                    raise ValueError("Enter the SMS code sent to your mobile")
                sms_ok = secrets.compare_digest(row["sms_code_hash"] or "", _otp_hash(sms_code))
            if not email_ok or not sms_ok:
                con.execute("UPDATE login_challenges SET attempts = ? WHERE id = ?", (attempts, challenge_id))
                con.commit()
                left = OTP_MAX_ATTEMPTS - attempts
                raise ValueError(f"Incorrect verification code. {left} attempt(s) left.")
            user_id = row["user_id"]
            con.execute("DELETE FROM login_challenges WHERE id = ?", (challenge_id,))
            con.execute("UPDATE users SET failed_logins = 0, locked_until = NULL, last_login = ? WHERE id = ?", (_iso(_now()), user_id))
            con.commit()
        finally:
            con.close()
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")
    return create_tokens(user)


def start_password_reset(email: str) -> Dict[str, Any]:
    from .delivery import send_email_otp, smtp_configured

    if not smtp_configured():
        raise ValueError("Password reset needs Gmail SMTP in config.env.")
    row = _load_user_row(email=email)
    if not row:
        return {"ok": True, "message": "If that inbox exists, a reset code was sent."}
    user = _row_user(row)
    code = _new_otp()
    rid = str(uuid.uuid4())
    now = _now()
    init_db()
    with _lock:
        con = _conn()
        try:
            con.execute("DELETE FROM password_resets WHERE user_id = ?", (user["id"],))
            con.execute(
                """INSERT INTO password_resets (id, user_id, code_hash, sent_at, attempts, expires_at, created_at)
                   VALUES (?, ?, ?, ?, 0, ?, ?)""",
                (rid, user["id"], _otp_hash(code), _iso(now), _iso(now + timedelta(minutes=OTP_TTL_MIN)), _iso(now)),
            )
            con.commit()
        finally:
            con.close()
    send_email_otp(user["email"], code, user.get("full_name") or "")
    return {
        "ok": True,
        "reset_id": rid,
        "email_masked": _mask_email(user["email"]),
        "resend_in": OTP_RESEND_SEC,
        "message": "Enter the 6-digit code we sent to your Gmail, then set a new password.",
    }


def confirm_password_reset(reset_id: str, code: str, new_password: str) -> Dict[str, Any]:
    issues = password_issues(new_password)
    if issues:
        raise ValueError("Password must include: " + "; ".join(issues))
    init_db()
    with _lock:
        con = _conn()
        try:
            row = con.execute("SELECT * FROM password_resets WHERE id = ?", (reset_id,)).fetchone()
            if not row:
                raise ValueError("Reset session expired.")
            if datetime.fromisoformat(row["expires_at"]) < _now():
                con.execute("DELETE FROM password_resets WHERE id = ?", (reset_id,))
                con.commit()
                raise ValueError("Reset code expired.")
            attempts = int(row["attempts"]) + 1
            if attempts > OTP_MAX_ATTEMPTS:
                con.execute("DELETE FROM password_resets WHERE id = ?", (reset_id,))
                con.commit()
                raise ValueError("Too many incorrect codes.")
            if not secrets.compare_digest(row["code_hash"], _otp_hash((code or "").strip())):
                con.execute("UPDATE password_resets SET attempts = ? WHERE id = ?", (attempts, reset_id))
                con.commit()
                raise ValueError("Incorrect reset code.")
            user_id = row["user_id"]
            con.execute("UPDATE users SET hashed_password = ?, failed_logins = 0, locked_until = NULL WHERE id = ?", (hash_password(new_password), user_id))
            con.execute("DELETE FROM password_resets WHERE id = ?", (reset_id,))
            con.commit()
        finally:
            con.close()
    return {"ok": True, "message": "Password updated. Sign in with your new password."}
