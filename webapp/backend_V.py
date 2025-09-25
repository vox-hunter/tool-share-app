import streamlit as st
from supabase import create_client, Client
from typing import Any, cast, Optional

DEFAULT_REDIRECT_URL = "https://geargrid.streamlit.app"


@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase: Client = init_connection()
_auth = cast(Any, supabase.auth)

def _ok(data):
    return {"data": data, "error": None}

def _err(message: str, code: Optional[str] = None):
    return {"data": None, "error": {"message": message, "code": code}}

def sign_in_with_oauth(provider: str, redirect_to: Optional[str] = None, flow_type: str = "pkce"):
    options = {"flow_type": flow_type, "redirect_to": DEFAULT_REDIRECT_URL}
    if redirect_to:
        options["redirect_to"] = redirect_to
    res = _auth.sign_in_with_oauth({"provider": provider, "options": options})
    url = None
    if isinstance(res, dict):
        url = res.get("data", {}).get("url") or res.get("url")
    else:
        url = getattr(getattr(res, "data", None), "url", None) or getattr(res, "url", None)
    return _ok({"url": url or ""})

def exchange_code_for_session(auth_code: str, code_verifier: Optional[str] = None, redirect_to: Optional[str] = None):
    if code_verifier and redirect_to:
        res = _auth.exchange_code_for_session({"auth_code": auth_code, "code_verifier": code_verifier, "redirect_to": redirect_to})
    else:
        res = _auth.exchange_code_for_session({"auth_code": auth_code})
    return _ok({
        "session": getattr(res, "session", None),
        "user": getattr(res, "user", None),
    })

def get_user():
    res = _auth.get_user()
    return _ok(getattr(res, "user", getattr(res, "data", res)))

def sign_out():
    """Signs out current session."""
    _auth.sign_out()
    return _ok({"signed_out": True})

# --- Additional helpers to enforce required fields and phone verification ---

def sign_up_traditional(email: str, phone: str, password: str, first_name: str, last_name: str, age: int):
    """Traditional signup requiring email, phone, password, first_name, last_name, age.

    - Creates user with email/password and stores profile metadata.
    - Triggers email verification (via Supabase settings).
    - Sets phone on the user to trigger SMS verification.
    """
    if not all([email, phone, password, first_name, last_name]) or age is None:
        return _err("All fields are required: email, phone, password, first_name, last_name, age")
    try:
        age_int = int(age)
    except (ValueError, TypeError):
        return _err("Age must be an integer")
    # Create user with email/password and required metadata
    res = _auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "email_redirect_to": DEFAULT_REDIRECT_URL,
            "data": {
                "first_name": first_name,
                "last_name": last_name,
                "age": age_int,
                "phone": phone,
            }
        }
    })
    # Attach phone to current session user to trigger SMS verification when possible
    phone_otp_sent = False
    session = getattr(res, "session", None)
    if session:
        try:
            _auth.update_user({"phone": phone})
            phone_otp_sent = True
        except Exception:  # pragma: no cover - Supabase may require verified session
            phone_otp_sent = False
    return _ok({
        "user": getattr(res, "user", None),
        "session": getattr(res, "session", None),
        "next_steps": {
            "verify_email": True,
            "verify_phone": phone_otp_sent or False,
        }
    })

def update_missing_fields(first_name: Optional[str] = None, last_name: Optional[str] = None, age: Optional[int] = None):
    """Update user profile metadata for any missing mandatory fields."""
    data: dict[str, Any] = {}
    if first_name is not None:
        data["first_name"] = first_name
    if last_name is not None:
        data["last_name"] = last_name
    if age is not None:
        data["age"] = int(age)
    if not data:
        return _err("No fields to update")
    res = _auth.update_user({"data": data})
    return _ok(getattr(res, "user", getattr(res, "data", res)))

def request_phone_verification(phone: str):
    """Set phone on current user to trigger SMS OTP for verification."""
    if not phone:
        return _err("Phone is required")
    res = _auth.update_user({"phone": phone})
    return _ok(getattr(res, "user", getattr(res, "data", res)))

def get_completion_status():
    """Return missing mandatory fields and verification requirements for current user."""
    ures = _auth.get_user()
    user = getattr(ures, "user", getattr(ures, "data", ures))
    if not user:
        return _err("No active user session")
    # Access fields safely
    email_confirmed_at = getattr(user, "email_confirmed_at", None) or (user.get("email_confirmed_at") if isinstance(user, dict) else None)
    phone_confirmed_at = getattr(user, "phone_confirmed_at", None) or (user.get("phone_confirmed_at") if isinstance(user, dict) else None)
    phone_val = getattr(user, "phone", None) or (user.get("phone") if isinstance(user, dict) else None)
    meta = getattr(user, "user_metadata", None) or (user.get("user_metadata") if isinstance(user, dict) else {}) or {}
    first_name = meta.get("first_name") if isinstance(meta, dict) else None
    last_name = meta.get("last_name") if isinstance(meta, dict) else None
    age = meta.get("age") if isinstance(meta, dict) else None

    missing = []
    if not first_name:
        missing.append("first_name")
    if not last_name:
        missing.append("last_name")
    if age is None:
        missing.append("age")
    if not phone_val:
        missing.append("phone")

    needs_email_verification = email_confirmed_at is None
    needs_phone_verification = (phone_val is None) or (phone_confirmed_at is None)

    return _ok({
        "missing_fields": missing,
        "needs_email_verification": needs_email_verification,
        "needs_phone_verification": needs_phone_verification,
        "user": user,
    })

def verify_phone_sms(phone: str, token: str):
    """Verify phone via an SMS OTP code for current user."""
    if not phone or not token:
        return _err("Phone and token are required")
    res = _auth.verify_otp({"phone": phone, "token": token, "type": "sms"})
    return _ok({
        "session": getattr(res, "session", None),
        "user": getattr(res, "user", None),
    })