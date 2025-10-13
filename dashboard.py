# ============================================================
# 🧤 MetaFlex Glove Internal Operations System
# Google Sheets → Streamlit Integration
# ============================================================

import streamlit as st
from google.oauth2 import service_account
import gspread
import pandas as pd
import os
import datetime
import plotly.express as px
import yaml
import streamlit_authenticator as stauth
import traceback

# ============================================================
# 🔐 AUTHENTICATION (v0.4.2 compatible + MetaFlex styling)
# ============================================================

with open("config.yaml") as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
)

# --- Centered, branded login UI ---
st.markdown(
    """
    <style>
    /* --- Center layout --- */
    .centered-login {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 85vh;
        background: linear-gradient(180deg, #0a4d4d 0%, #0d5757 100%);
    }

    /* --- Login form box --- */
    .stForm {
        width: 360px !important;
        margin: auto;
        border-radius: 14px;
        padding: 2rem 1.75rem 2.25rem;
        background-color: #ffffff;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        border-top: 6px solid #d4ff00;
        text-align: center;
    }

    /* --- Title inside form --- */
    .stForm h3 {
        color: #0a4d4d !important;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    /* --- Input fields --- */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1.8px solid #0a4d4d !important;
        background-color: #f9f9f9;
        font-weight: 500;
        color: #0a4d4d;
    }

    /* --- Button --- */
    .stButton button {
        width: 100%;
        background-color: #d4ff00 !important;
        color: #0a4d4d !important;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #c4ff00 !important;
        box-shadow: 0 4px 12px rgba(212, 255, 0, 0.3);
        transform: translateY(-2px);
    }

    /* --- Logout button --- */
    [data-testid="stSidebar"] .stButton button {
        background-color: #d4ff00 !important;
        color: #0a4d4d !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --- Render login ---
with st.container():
    st.markdown("<div class='centered-login'>", unsafe_allow_html=True)
    name, authentication_status, username = authenticator.login(
        "MetaFlex Login", location="main"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- Auth logic ---
if authentication_status is False:
    st.error("Username or password is incorrect")
    st.stop()
elif authentication_status is None:
    st.info("Please enter your username and password")
    st.stop()
elif authentication_status:
    authenticator.logout("Logout", location="sidebar")


CACHE_TTL = 30  # seconds
WORKSHEET_NAME = "Otter_Tasks"

# ============================================================
# 🎨 CUSTOM META FLEX STYLING
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .main { background-color: #ffffff; padding: 2rem; }
    h1 { color: #0a4d4d; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem; }
    h2, h3 { color: #0a4d4d; font-weight: 600; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a4d4d 0%, #0d5757 100%);
        border-right: 3px solid #d4ff00;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; font-weight: 600; }
    .stButton button {
        background-color: #d4ff00; color: #0a4d4d; border-radius: 8px;
        border: none; padding: 0.5rem 1.5rem; font-weight: 700; transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #c4ff00; box-shadow: 0 4px 12px rgba(212,255,0,0.3);
        transform: translateY(-2px);
    }
    hr { margin: 2rem 0; border: none; border-top: 2px solid #d4ff00; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔄 LOAD DATA (SECURELY FROM STREAMLIT SECRETS)
# ============================================================
@st.cache_data(ttl=CACHE_TTL)
def load_data():
    """Load data from Google Sheets with automatic authentication and cleaning"""
    try:
        # Authenticate using Streamlit Secrets
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]

        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )

        client = gspread.authorize(creds)
        sheet = client.open_by_url(st.secrets["google_sheets"]["SHEET_URL"]).worksheet(WORKSHEET_NAME)
        data = sheet.get_all_values()

        if len(data) < 2:
            st.warning("No rows found in Google Sheet.")
            return pd.DataFrame()

        headers = [h.strip() for h in data[0] if h.strip() != ""]
        rows = [r[:len(headers)] for r in data[1:] if any(cell.strip() for cell in r)]

        df = pd.DataFrame(rows, columns=headers)

        # Clean & format
        if "Due Date" in df.columns:
            df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce")
        if "Progress %" in df.columns:
            df["Progress %"] = (
                df["Progress %"].astype(str).str.replace("%", "", regex=False).replace("", "0")
            )
            df["Progress %"] = pd.to_numeric(df["Progress %"], errors="coerce").fillna(0)

        return df

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.code(traceback.format_exc())
        return pd.DataFrame()

# ============================================================
# 🧩 DASHBOARD HEADER
# ============================================================
st.title("MetaFlex Glove Internal Operations System")
st.markdown(
    "<p style='color: #0a4d4d; font-size: 1rem; font-weight: 500;'>Real-time task tracking and team management</p>",
    unsafe_allow_html=True,
)
st.divider()

# ============================================================
# LOAD DATA
# ============================================================
df = load_data()
if df.empty:
    st.warning("⚠️ No data available. Please check your Google Sheets connection.")
    st.stop()

st.caption(f"🔄 Last synced: {datetime.datetime.now().strftime('%I:%M %p')} | Auto-refresh: {CACHE_TTL}s")

# ============================================================
# SIDEBAR VIEW SELECTOR
# ============================================================
st.sidebar.header("Dashboard View")
view_type = st.sidebar.radio("Select View:", ["Ops Manager", "Personal View", "Project View"])
st.sidebar.divider()

# ============================================================
# OPS MANAGER VIEW
# ============================================================
if view_type == "Ops Manager":
    st.sidebar.header("Filters")

    all_projects = ['All'] + sorted(df['Project'].dropna().unique().tolist()) if 'Project' in df.columns else ['All']
    selected_project = st.sidebar.selectbox("Project", all_projects)
    all_status = ['All'] + sorted(df['Status'].dropna().unique().tolist()) if 'Status' in df.columns else ['All']
    selected_status = st.sidebar.selectbox("Status", all_status)
    all_emails = ['All'] + sorted(df['Emails'].dropna().unique().tolist()) if 'Emails' in df.columns else ['All']
    selected_email = st.sidebar.selectbox("Assigned Email", all_emails)

    filtered_df = df.copy()
    if selected_project != 'All' and 'Project' in df.columns:
        filtered_df = filtered_df[filtered_df['Project'] == selected_project]
    if selected_status != 'All' and 'Status' in df.columns:
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    if selected_email != 'All' and 'Emails' in df.columns:
        filtered_df = filtered_df[filtered_df['Emails'] == selected_email]

    st.sidebar.caption(f"📊 Showing {len(filtered_df)} of {len(df)} tasks")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tasks", len(filtered_df))
    with col2:
        st.metric("Open", len(filtered_df[filtered_df['Status'] == 'Open']) if 'Status' in df.columns else 0)
    with col3:
        done_tasks = len(filtered_df[filtered_df['Status'] == 'Done']) if 'Status' in df.columns else 0
        st.metric("Done", done_tasks)
    with col4:
        percent_done = (done_tasks / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric("Completion Rate", f"{percent_done:.0f}%")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tasks by Status")
        if 'Status' in df.columns:
            status_counts = filtered_df['Status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color=status_counts.index,
                color_discrete_map={'Open': '#e74c3c', 'Working on it': '#f39c12', 'Done': '#d4ff00'},
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Tasks by Project")
        if 'Project' in df.columns:
            project_counts = filtered_df['Project'].value_counts()
            fig = px.bar(
                x=project_counts.index,
                y=project_counts.values,
                color_discrete_sequence=['#0a4d4d']
            )
            fig.update_layout(xaxis_title="Project", yaxis_title="Tasks", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("All Tasks")
    st.dataframe(filtered_df, use_container_width=True, height=450)

# ============================================================
# PERSONAL VIEW
# ============================================================
elif view_type == "Personal View":
    st.sidebar.header("Select Team Member")
    if 'Emails' not in df.columns:
        st.warning("⚠️ No 'Emails' column found in your data.")
        st.stop()

    selected_email = st.sidebar.selectbox("View tasks for:", sorted(df['Emails'].dropna().unique().tolist()))
    personal_df = df[df['Emails'] == selected_email]

    st.header(f"Welcome, {selected_email}")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("My Tasks", len(personal_df))
    with col2:
        st.metric("Open", len(personal_df[personal_df['Status'] == 'Open']) if 'Status' in df.columns else 0)
    with col3:
        done_tasks = len(personal_df[personal_df['Status'] == 'Done']) if 'Status' in df.columns else 0
        percent_done = (done_tasks / len(personal_df) * 100) if len(personal_df) > 0 else 0
        st.metric("Done", f"{done_tasks} ({percent_done:.0f}%)")

    st.divider()
    st.subheader("My Tasks")
    st.dataframe(personal_df, use_container_width=True, height=450)

# ============================================================
# PROJECT VIEW
# ============================================================
else:
    st.sidebar.header("Select Project")
    if 'Project' not in df.columns:
        st.warning("⚠️ No 'Project' column found in your data.")
        st.stop()

    selected_project = st.sidebar.selectbox("View tasks for:", sorted(df['Project'].dropna().unique().tolist()))
    project_df = df[df['Project'] == selected_project]

    st.header(f"Project: {selected_project}")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tasks", len(project_df))
    with col2:
        st.metric("Open", len(project_df[project_df['Status'] == 'Open']) if 'Status' in df.columns else 0)
    with col3:
        done_tasks = len(project_df[project_df['Status'] == 'Done']) if 'Status' in df.columns else 0
        perc
