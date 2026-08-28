from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any

import streamlit as st

AUTH_VERSION = "1.0"


def _hash_password(password: str, salt: str) -> str:
    """Create a PBKDF2 password hash."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    ).hex()


def create_password_record(password: str) -> dict[str, str]:
    """Create a salted password record."""
    salt = secrets.token_hex(16)

    return {
        "salt": salt,
        "password_hash": _hash_password(password, salt),
    }


def verify_password(
    password: str,
    salt: str,
    password_hash: str,
) -> bool:
    """Safely verify a password."""
    calculated = _hash_password(password, salt)

    return hmac.compare_digest(
        calculated,
        password_hash,
    )


def _get_users() -> dict[str, Any]:
    """Read authentication users from Streamlit secrets."""
    try:
        users = st.secrets["users"]
    except KeyError:
        return {}

    if not hasattr(users, "items"):
        return {}

    return dict(users)


def authenticate(username: str, password: str) -> bool:
    """Authenticate a user using Streamlit secrets."""
    users = _get_users()

    if username not in users:
        return False

    record = users[username]

    return verify_password(
        password,
        str(record["salt"]),
        str(record["password_hash"]),
    )


def get_user_role(username: str) -> str | None:
    """Return the authenticated user's role."""
    users = _get_users()

    if username not in users:
        return None

    return str(
        users[username].get(
            "role",
            "unknown",
        )
    )


def login_form() -> bool:
    """Render a Streamlit login form."""
    if st.session_state.get(
        "authenticated",
        False,
    ):
        return True

    st.subheader("Einstein AI V2 — Secure Login")

    username = st.text_input(
        "Username",
        key="auth_username",
    )

    password = st.text_input(
        "Password",
        type="password",
        key="auth_password",
    )

    if st.button(
        "Login",
        type="primary",
    ):
        if authenticate(
            username,
            password,
        ):
            st.session_state["authenticated"] = True

            st.session_state["username"] = username

            st.session_state["role"] = get_user_role(username)

            st.success("Authentication successful.")

            st.rerun()

        st.error("Invalid username or password.")

    return False


def require_role(required_role: str) -> bool:
    """Require an authenticated user with a specific role."""
    if not st.session_state.get(
        "authenticated",
        False,
    ):
        return False

    return st.session_state.get("role") == required_role


def logout() -> None:
    """Log out the current user."""
    st.session_state.clear()
    st.rerun()
