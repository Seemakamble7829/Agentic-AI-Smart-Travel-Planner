"""Authentication helpers for the Streamlit app.

Provides a tiny sidebar login helper. Credentials are intentionally simple for
the demo (do NOT use this in production). The helper stores the logged-in
username in `st.session_state['user']` and returns it.
"""
from typing import Optional
import streamlit as st


USERS = {
    "admin": "admin123",
    "user": "user123",
}


def login_sidebar() -> Optional[str]:
    """Render a small login box in the sidebar and return the username.

    Usage: call early in `main()` so the user identity is available to the
    rest of the app. The function will initialize `st.session_state['user']`
    when necessary.
    """
    if "user" not in st.session_state:
        st.session_state["user"] = "Guest"

    with st.sidebar:
        st.markdown("### Account")
        if st.session_state.get("user", "Guest") == "Guest":
            username = st.text_input("Username", key="auth_username")
            password = st.text_input("Password", type="password", key="auth_password")
            if st.button("Sign in", key="auth_signin"):
                if username in USERS and USERS[username] == password:
                    st.session_state["user"] = username
                    st.sidebar.success(f"Signed in as {username}")
                    return username
                else:
                    st.sidebar.error("Invalid credentials")
                    return None
        else:
            st.markdown(f"Signed in as **{st.session_state['user']}**")
            if st.button("Sign out", key="auth_signout"):
                st.session_state["user"] = "Guest"
                st.sidebar.info("Signed out")
                return "Guest"

    return st.session_state.get("user")
"""
auth.py (placeholder)

This file was intentionally cleared by an automated cleanup step. The app now
uses a simple sidebar login implemented directly in `app.py`. If you need the
old helpers, recover them from source control history.
"""

__all__ = []
