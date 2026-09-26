"""Real email (SMTP / Gmail) and SMS (Twilio) OTP delivery. No mock sends."""

from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Dict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv

    _root = Path(__file__).resolve().parents[3]
    for _env in (_root / "config.env", _root / ".env"):
        if _env.exists():
            load_dotenv(_env, override=False)
except Exception:
    pass


def _b(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def smtp_configured() -> bool:
    return bool(os.getenv("SMTP_USER", "").strip() and os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip())


def twilio_configured() -> bool:
    return bool(
        os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        and os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        and os.getenv("TWILIO_FROM_NUMBER", "").strip()
    )


def delivery_status() -> Dict[str, bool]:
    return {
        "email_ready": smtp_configured(),
        "sms_ready": twilio_configured(),
        "email_required": True,
        "sms_optional": True,
    }


def send_email_otp(to_email: str, code: str, full_name: str = "") -> None:
    if not smtp_configured():
        raise RuntimeError(
            "Email delivery is not configured. Set SMTP_USER and SMTP_PASSWORD "
            "(Gmail: enable 2-Step Verification, then create an App Password) in config.env."
        )
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()
    from_addr = os.getenv("SMTP_FROM", user).strip() or user
    starttls = _b("SMTP_STARTTLS", "true") if port != 465 else False

    greeting = f"Hi {full_name}," if full_name else "Hi,"
    msg = EmailMessage()
    msg["Subject"] = f"{code} is your iFake verification code"
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(
        f"{greeting}\n\n"
        f"Your iFake email verification code is: {code}\n\n"
        f"It expires in 10 minutes. If you did not create an account, ignore this email.\n\n"
        f"— iFake\n"
    )
    msg.add_alternative(
        f"<p>{greeting}</p>"
        f"<p>Your iFake email verification code is:</p>"
        f"<p style='font-size:28px;letter-spacing:6px;font-weight:700'>{code}</p>"
        f"<p>This code expires in <strong>10 minutes</strong>.</p>"
        f"<p>If you did not create an account, you can ignore this message.</p>",
        subtype="html",
    )

    try:
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=20) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=20) as smtp:
                smtp.ehlo()
                if starttls:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.ehlo()
                smtp.login(user, password)
                smtp.send_message(msg)
    except Exception as e:
        logger.error("SMTP send failed: %s", e)
        raise RuntimeError(
            "Could not send verification email. Check Gmail SMTP settings "
            "(smtp.gmail.com:587 + App Password, not your normal Gmail password)."
        ) from e
    logger.info("Verification email sent to %s", to_email)


def send_sms_otp(to_phone: str, code: str) -> None:
    if not twilio_configured():
        raise RuntimeError(
            "SMS delivery is not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
            "and TWILIO_FROM_NUMBER in config.env."
        )
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    body = urlencode(
        {
            "To": to_phone,
            "From": from_number,
            "Body": f"iFake verification code: {code}. Expires in 10 minutes. Do not share this code.",
        }
    ).encode()
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    req = Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    import base64

    basic = base64.b64encode(f"{sid}:{token}".encode()).decode()
    req.add_header("Authorization", f"Basic {basic}")
    try:
        with urlopen(req, timeout=20) as resp:
            if getattr(resp, "status", 200) >= 300:
                raise RuntimeError(f"Twilio HTTP {resp.status}")
    except Exception as e:
        logger.error("Twilio send failed: %s", e)
        raise RuntimeError("Could not send SMS verification. Check Twilio credentials and from-number.") from e
    logger.info("Verification SMS sent to %s", to_phone[-4:].rjust(len(to_phone), "*"))
