import streamlit as st

st.title("Secrets Test")

try:
    # Test accessing google_sheet_id
    sheet_id = st.secrets["google_sheet_id"]
    st.success(f"✅ Successfully loaded google_sheet_id: {sheet_id}")
except Exception as e:
    st.error(f"❌ Error loading google_sheet_id: {str(e)}")

try:
    # Test accessing gcp_service_account
    gcp = st.secrets["gcp_service_account"]
    st.success(f"✅ Successfully loaded gcp_service_account")
except Exception as e:
    st.error(f"❌ Error loading gcp_service_account: {str(e)}")

# Show all available secrets keys
st.write("Available secrets keys:")
st.write(list(st.secrets.keys()))
