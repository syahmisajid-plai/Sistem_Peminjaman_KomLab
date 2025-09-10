import streamlit as st

# Dummy user untuk contoh (sebaiknya simpan di DB)
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}


def login(username: str, password: str):
    """Validasi login user."""
    user = USERS.get(username)
    if user and user["password"] == password:
        st.session_state["user"] = username
        st.session_state["role"] = user["role"]
        return True
    return False


def logout():
    """Hapus sesi login."""
    if "user" in st.session_state:
        del st.session_state["user"]
    if "role" in st.session_state:
        del st.session_state["role"]


def is_authenticated():
    """Cek apakah user sudah login."""
    return "user" in st.session_state
