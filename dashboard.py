import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import plotly.express as px
from datetime import datetime

# ----------------------------
# Streamlit Page Configuration
# ----------------------------
st.set_page_config(
    page_title="MetaFlex Internal Ops",
    page_icon="🧤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Custom CSS Styling
# ----------------------------
st.markdown("""
<style>
    body { font-family: 'Helvetica', sans-serif; }
    .main { background-color: #f7f7f7; }
    h1, h2, h3 { color: #333333; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Load Data Function (cached)
# ----------------------------
@st.cache_data(ttl=30)  # refresh every 30 seconds
def load_data():
    """Load data from Google Sheet"""
    try:
        # ----------------------------
        # Authenticate using Streamlit Secrets (Cloud) or Local Key (Mac)
        # ----------------------------
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        if "gcp_service_account" in st.secrets:
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=scopes
            )
            st.success("🟢 Connected to Google Sheets via Streamlit Secrets")
        else:
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_file(
                "/Users/annaciboro/.config/gcloud/metaflex-key.json",
                scopes=scopes
            )
            st.info("🟡 Using local key (testing mode)")

        # ----------------------------
        # Connect to Google Sheets
        # ----------------------------
        client = gspread.authorize(creds)
        sheet = client.open("Metaflexglove Dashboard v1").worksheet("Otter_Tasks")

        # ----------------------------
        # Get all data
        # ----------------------------
        data = sheet.get_all_values()
        if len(data) < 2:
            st.error("No rows found in sheet.")
            return pd.DataFrame()

        # Clean headers
        headers = [h.strip() for h in data[0] if h.strip() != ""]
        rows = [r[:len(headers)] for r in data[1:] if any(cell.strip() for cell in r)]
        df = pd.DataFrame(rows, columns=headers)

        # Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]

        # Clean and format columns
        if 'Due Date' in df.columns:
            df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce')
        if 'Progress %' in df.columns:
            df['Progress %'] = (
                df['Progress %']
                .astype(str)
                .str.replace('%', '', regex=False)
                .replace('', '0')
            )
            df['Progress %'] = pd.to_numeric(df['Progress %'], errors='coerce').fillna(0)

        return df

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

# ----------------------------
# Dashboard Layout
# ----------------------------
st.title("🧤 MetaFlex Internal Ops Dashboard")
st.markdown("*Real-time task tracking from Google Sheets*")
st.divider()

# Load data
df = load_data()
if df.empty:
    st.warning("No data found. Check your Google Sheets connection.")
    st.stop()

# Sidebar - View Selection
st.sidebar.header("📊 Dashboard View")
view_type = st.sidebar.radio(
    "Select View:",
    ["👔 Ops Manager", "👤 Personal View", "📁 Project View"]
)
st.sidebar.divider()

# ----------------------------
# OPS MANAGER VIEW
# ----------------------------
if view_type == "👔 Ops Manager":
    st.sidebar.caption("**Manager Overview** – See all tasks, team performance, and unassigned items")

    if 'Project' in df.columns:
        all_projects = ['All'] + sorted(df['Project'].dropna().unique().tolist())
    else:
        st.warning("⚠️ No 'Project' column found in your data.")
        all_projects = ['All']

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

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total Tasks", len(filtered_df))
    with col2:
        open_tasks = len(filtered_df[filtered_df['Status'] == 'Open']) if 'Status' in df.columns else 0
        st.metric("🔴 Open", open_tasks)
    with col3:
        done_tasks = len(filtered_df[filtered_df['Status'] == 'Done']) if 'Status' in df.columns else 0
        st.metric("✅ Done", done_tasks)
    with col4:
        percent_done = (done_tasks / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric("📈 Completion Rate", f"{percent_done:.0f}%")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Tasks by Status")
        if 'Status' in df.columns:
            status_counts = filtered_df['Status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color=status_counts.index,
                color_discrete_map={'Open': '#d9938f', 'Working on it': '#f4d89d', 'Done': '#a8c9a1'}
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📁 Tasks by Project")
        if 'Project' in df.columns:
            project_counts = filtered_df['Project'].value_counts()
            fig = px.bar(
                x=project_counts.index,
                y=project_counts.values,
                color_discrete_sequence=['#5f87af']
            )
            fig.update_layout(xaxis_title="Project", yaxis_title="Tasks", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("📋 All Tasks")
    st.dataframe(filtered_df, use_container_width=True, height=450)

# ----------------------------
# PERSONAL VIEW
# ----------------------------
elif view_type == "👤 Personal View":
    st.sidebar.header("👤 Select Team Member")
    if 'Emails' in df.columns:
        selected_email = st.sidebar.selectbox("View tasks for:", sorted(df['Emails'].dropna().unique().tolist()))
        personal_df = df[df['Emails'] == selected_email]
    else:
        st.warning("⚠️ No 'Emails' column found in your data.")
        personal_df = df.copy()
        selected_email = "Unknown"

    st.header(f"👋 Hi, {selected_email}")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 My Tasks", len(personal_df))
    with col2:
        open_tasks = len(personal_df[personal_df['Status'] == 'Open']) if 'Status' in df.columns else 0
        st.metric("🔴 Open", open_tasks)
    with col3:
        done_tasks = len(personal_df[personal_df['Status'] == 'Done']) if 'Status' in df.columns else 0
        percent_done = (done_tasks / len(personal_df) * 100) if len(personal_df) > 0 else 0
        st.metric("✅ Done", f"{done_tasks} ({percent_done:.0f}%)")

    st.divider()
    st.subheader("📊 My Tasks")
    st.dataframe(personal_df, use_container_width=True, height=450)

# ----------------------------
# PROJECT VIEW
# ----------------------------
else:
    st.sidebar.header("📁 Select Project")
    if 'Project' in df.columns:
        selected_project = st.sidebar.selectbox("View tasks for:", sorted(df['Project'].dropna().unique().tolist()))
        project_df = df[df['Project'] == selected_project]
    else:
        st.warning("⚠️ No 'Project' column found in your data.")
        project_df = df.copy()
        selected_project = "Unknown"

    st.header(f"📁 {selected_project}")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Total Tasks", len(project_df))
    with col2:
        open_tasks = len(project_df[project_df['Status'] == 'Open']) if 'Status' in df.columns else 0
        st.metric("🔴 Open", open_tasks)
    with col3:
        done_tasks = len(project_df[project_df['Status'] == 'Done']) if 'Status' in df.columns else 0
        percent_done = (done_tasks / len(project_df) * 100) if len(project_df) > 0 else 0
        st.metric("✅ Done", f"{done_tasks} ({percent_done:.0f}%)")

    st.divider()
    st.subheader("📊 Project Tasks")
    st.dataframe(project_df, use_container_width=True, height=450)

# ----------------------------
# Footer
# ----------------------------
st.divider()
st.caption("🔄 Data refreshes automatically every 30 seconds • Connected securely via Streamlit Secrets")
