import streamlit as st
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

st.set_page_config(page_title="Auth Test", layout="wide")

# --- Load credentials ---
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- Initialize authenticator ---
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# --- Render login form ---
authenticator.login(location="main", fields={"Form name": "Login"})

# --- Access session values (new pattern for v0.4.x) ---
if st.session_state.get("authentication_status"):
    authenticator.logout(location="sidebar")
    st.sidebar.success(f"Welcome, {st.session_state['name']} 👋")

    st.title("✅ Logged In Successfully")
    st.write(f"**User:** {st.session_state['username']}")
    st.write(f"**Name:** {st.session_state['name']}")

elif st.session_state.get("authentication_status") is False:
    st.error("❌ Username or password is incorrect")

elif st.session_state.get("authentication_status") is None:
    st.info("👋 Please enter your username and password to log in.")
