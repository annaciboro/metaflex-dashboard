# ============================================================
# 🧤 MetaFlex Glove Internal Operations System
# Google Sheets → Streamlit Integration
# ============================================================

import streamlit as st
from google.oauth2 import service_account
import gspread
import pandas as pd
import toml
import os
import datetime
import plotly.express as px
import yaml
import streamlit_authenticator as stauth
import traceback

# --- Authentication Setup (v0.4.2 compatible) ---
import yaml
import streamlit_authenticator as stauth

with open('config.yaml') as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)



name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status is False:
    st.error('Username or password is incorrect')

elif authentication_status is None:
    st.warning('Please enter your username and password')

elif authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome, {name} 👋")
else:
    st.stop()
# ----------------------------
# PAGE CONFIGURATION
# ----------------------------
st.set_page_config(
    page_title="MetaFlex Glove Internal Operations System",
    page_icon="🧤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# GLOBAL VARIABLES
# ----------------------------
CACHE_TTL = 30  # seconds
SPREADSHEET_ID = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"
WORKSHEET_NAME = "Otter_Tasks"
SHEET_NAME = "Otter_Tasks"

# ----------------------------
# CUSTOM META FLEX CSS STYLING
# ----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background-color: #ffffff;
        padding: 2rem;
    }
    
    h1 {
        color: #0a4d4d;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        color: #0a4d4d;
        font-weight: 600;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #d4ff00;
        box-shadow: 0 2px 8px rgba(212, 255, 0, 0.1);
    }
    
    .stMetric label {
        color: #0a4d4d;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #0a4d4d;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a4d4d 0%, #0d5757 100%);
        border-right: 3px solid #d4ff00;
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stSelectbox label {
        color: #d4ff00 !important;
    }
    
    .stButton button {
        background-color: #d4ff00;
        color: #0a4d4d;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #c4ff00;
        box-shadow: 0 4px 12px rgba(212, 255, 0, 0.3);
        transform: translateY(-2px);
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #d4ff00;
    }
    
    .stDataFrame {
        border: 2px solid #0a4d4d;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .block-container {
        padding-top: 3rem;
    }
    
    .metric-subtitle {
        color: #0a4d4d;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# LOAD DATA (Cached every 30 seconds)
# ----------------------------
@st.cache_data(ttl=CACHE_TTL)
def load_data():
    """Load data from Google Sheets with automatic authentication and cleaning"""
    try:
        secrets = toml.load(".streamlit/secrets.toml")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]

        # Authenticate with service account from Streamlit secrets
        creds = service_account.Credentials.from_service_account_info(
            secrets["gcp_service_account"],
            scopes=scopes
        )

        client = gspread.authorize(creds)
        sheet = client.open("Metaflexglove Dashboard v1").worksheet("Otter_Tasks")

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
                df["Progress %"]
                .astype(str)
                .str.replace("%", "", regex=False)
                .replace("", "0")
            )
            df["Progress %"] = pd.to_numeric(df["Progress %"], errors="coerce").fillna(0)

        return df

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        import traceback
        st.code(traceback.format_exc())  # 👈 shows full error details inside the Streamlit app
        return pd.DataFrame()


# ----------------------------
# DASHBOARD HEADER
# ----------------------------
st.title("MetaFlex Glove Internal Operations System")
st.markdown(
    "<p style='color: #0a4d4d; font-size: 1rem; font-weight: 500;'>Real-time task tracking and team management</p>",
    unsafe_allow_html=True,
)
st.divider()

# ----------------------------
# LOAD DATA
# ----------------------------
df = load_data()
if df.empty:
    st.warning("⚠️ No data available. Please check your Google Sheets connection.")
    st.stop()

st.caption(f"🔄 Last synced: {datetime.datetime.now().strftime('%I:%M %p')} | Auto-refresh: {CACHE_TTL}s")

# ----------------------------
# SIDEBAR - VIEW SELECTION
# ----------------------------
st.sidebar.header("Dashboard View")
view_type = st.sidebar.radio("Select View:", ["Ops Manager", "Personal View", "Project View"])
st.sidebar.divider()

# ============================================================
# OPS MANAGER VIEW
# ============================================================
if view_type == "Ops Manager":
    st.sidebar.caption("Manager Overview - All tasks, team performance, and assignments")

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
        open_tasks = len(filtered_df[filtered_df['Status'] == 'Open']) if 'Status' in df.columns else 0
        st.metric("Open", open_tasks)
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
                color_discrete_map={
                    'Open': '#e74c3c',
                    'Working on it': '#f39c12',
                    'Done': '#d4ff00'
                },
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                showlegend=True,
                margin=dict(t=0, b=0, l=0, r=0),
                font=dict(family="Inter, sans-serif")
            )
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
            fig.update_layout(
                xaxis_title="Project",
                yaxis_title="Tasks",
                showlegend=False,
                margin=dict(t=20, b=0, l=0, r=0),
                font=dict(family="Inter, sans-serif")
            )
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
        open_tasks = len(personal_df[personal_df['Status'] == 'Open']) if 'Status' in df.columns else 0
        st.metric("Open", open_tasks)
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
        open_tasks = len(project_df[project_df['Status'] == 'Open']) if 'Status' in df.columns else 0
        st.metric("Open", open_tasks)
    with col3:
        done_tasks = len(project_df[project_df['Status'] == 'Done']) if 'Status' in df.columns else 0
        percent_done = (done_tasks / len(project_df) * 100) if len(project_df) > 0 else 0
        st.metric("Done", f"{done_tasks} ({percent_done:.0f}%)")

    st.divider()
    st.subheader("Project Tasks")
    st.dataframe(project_df, use_container_width=True, height=450)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(f"🔄 Data refreshes every {CACHE_TTL}s | Connected to Google Sheet: '{WORKSHEET_NAME}'")
