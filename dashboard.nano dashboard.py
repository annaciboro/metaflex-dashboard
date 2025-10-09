import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="MetaFlex Internal Ops",
    page_icon="🧤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    h1 {
        color: #5f87af;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)  # Refresh every 30 seconds
def load_data():
    """Load data from Google Sheet"""
    try:
        # Setup credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json',
            scope
        )
        client = gspread.authorize(creds)
        
        # ⚠️ CHANGE THIS TO YOUR EXACT SHEET NAME
        sheet = client.open("MetaFlex Internal Ops").sheet1
        
        # Get all data starting from row 3 (skip title and headers)
        data = sheet.get_all_values()[2:]
        
        # Column names from your sheet
        columns = [
            'Transcript ID', 'Date Assigned', 'Assigned To', 'Task',
            'Project', 'Status', 'Confidence', 'Due Date', 'Notes',
            'Progress %', 'Progress Bar', 'Email'
        ]
        
        df = pd.DataFrame(data, columns=columns)
        
        # Clean up data
        df = df[df['Assigned To'].notna() & (df['Assigned To'] != '')]
        df['Date Assigned'] = pd.to_datetime(df['Date Assigned'], errors='coerce')
        df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce')
        
        # Convert progress percentage
        df['Progress %'] = df['Progress %'].str.replace('%', '').replace('', '0')
        df['Progress %'] = pd.to_numeric(df['Progress %'], errors='coerce').fillna(0)
        
        return df
    
    except Exception as e:
        st.error(f"⚠️ Error loading data: {str(e)}")
        return pd.DataFrame()

# Header
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

# Different views based on selection
if view_type == "👔 Ops Manager":
    st.sidebar.caption("**Manager Overview**\nSee all tasks, team performance, and unassigned items")
    
    # Filters
    st.sidebar.header("🔍 Filters")
    all_team = ['All'] + sorted(df['Assigned To'].unique().tolist())
    selected_team = st.sidebar.selectbox("Team Member", all_team)
    
    all_status = ['All'] + df['Status'].unique().tolist()
    selected_status = st.sidebar.selectbox("Status", all_status)
    
    all_projects = ['All'] + sorted(df['Project'].unique().tolist())
    selected_project = st.sidebar.selectbox("Project", all_projects)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_team != 'All':
        filtered_df = filtered_df[filtered_df['Assigned To'] == selected_team]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    if selected_project != 'All':
        filtered_df = filtered_df[filtered_df['Project'] == selected_project]
    
    st.sidebar.divider()
    st.sidebar.caption(f"📊 Showing {len(filtered_df)} of {len(df)} tasks")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Tasks", len(filtered_df))
    with col2:
        open_tasks = len(filtered_df[filtered_df['Status'] == 'Open'])
        st.metric("🔴 Open", open_tasks)
    with col3:
        working_tasks = len(filtered_df[filtered_df['Status'] == 'Working on it'])
        st.metric("🟡 Working", working_tasks)
    with col4:
        done_tasks = len(filtered_df[filtered_df['Status'] == 'Done'])
        completion_rate = (done_tasks / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric("✅ Done", f"{done_tasks} ({completion_rate:.0f}%)")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Tasks by Status")
        status_counts = filtered_df['Status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_map={
                'Open': '#d9938f',
                'Working on it': '#f4d89d',
                'Done': '#a8c9a1'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Tasks by Team Member")
        team_counts = filtered_df['Assigned To'].value_counts()
        fig = px.bar(
            x=team_counts.index,
            y=team_counts.values,
            color_discrete_sequence=['#5f87af']
        )
        fig.update_layout(xaxis_title="Team Member", yaxis_title="Tasks", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Task table
    st.subheader("📋 All Tasks")
    display_columns = ['Assigned To', 'Task', 'Project', 'Status', 'Progress %', 'Due Date']
    st.dataframe(filtered_df[display_columns], use_container_width=True, height=400)

elif view_type == "👤 Personal View":
    st.sidebar.caption("**Individual Dashboard**\nSee your personal tasks and progress")
    
    # Select person
    st.sidebar.header("👤 Select Team Member")
    selected_person = st.sidebar.selectbox(
        "View tasks for:",
        sorted(df['Assigned To'].unique().tolist())
    )
    
    # Filter to selected person
    person_df = df[df['Assigned To'] == selected_person]
    
    # Personal greeting
    st.header(f"👋 Hi, {selected_person}!")
    st.markdown("*Here's what you're working on*")
    st.divider()
    
    # Personal metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 My Tasks", len(person_df))
    with col2:
        my_open = len(person_df[person_df['Status'] == 'Open'])
        st.metric("🔴 To Start", my_open)
    with col3:
        my_working = len(person_df[person_df['Status'] == 'Working on it'])
        st.metric("🟡 In Progress", my_working)
    with col4:
        my_done = len(person_df[person_df['Status'] == 'Done'])
        completion = (my_done / len(person_df) * 100) if len(person_df) > 0 else 0
        st.metric("✅ Done", f"{my_done} ({completion:.0f}%)")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 My Task Status")
        status_counts = person_df['Status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_map={
                'Open': '#d9938f',
                'Working on it': '#f4d89d',
                'Done': '#a8c9a1'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📁 My Projects")
        project_counts = person_df['Project'].value_counts()
        fig = px.bar(
            x=project_counts.index,
            y=project_counts.values,
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(xaxis_title="Project", yaxis_title="Tasks", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Tasks by status
    for status in ['Open', 'Working on it', 'Done']:
        status_tasks = person_df[person_df['Status'] == status]
        if not status_tasks.empty:
            emoji = {'Open': '🔴', 'Working on it': '🟡', 'Done': '✅'}
            st.subheader(f"{emoji[status]} {status} ({len(status_tasks)})")
            
            for idx, row in status_tasks.iterrows():
                with st.expander(f"**{row['Task']}**"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Project:** {row['Project']}")
                        st.write(f"**Due Date:** {row['Due Date']}")
                        if row['Notes']:
                            st.write(f"**Notes:** {row['Notes']}")
                    with col2:
                        progress_val = row['Progress %'] / 100 if pd.notna(row['Progress %']) else 0
                        st.progress(progress_val)
                        st.caption(f"{int(row['Progress %'])}% complete")

else:  # Project View
    st.sidebar.caption("**Project Overview**\nSee tasks grouped by project")
    
    # Select project
    st.sidebar.header("📁 Select Project")
    selected_project = st.sidebar.selectbox(
        "View tasks for:",
        sorted(df['Project'].unique().tolist())
    )
    
    # Filter to selected project
    project_df = df[df['Project'] == selected_project]
    
    st.header(f"📁 {selected_project}")
    st.divider()
    
    # Project metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Tasks", len(project_df))
    with col2:
        proj_open = len(project_df[project_df['Status'] == 'Open'])
        st.metric("🔴 Open", proj_open)
    with col3:
        proj_working = len(project_df[project_df['Status'] == 'Working on it'])
        st.metric("🟡 Working", proj_working)
    with col4:
        proj_done = len(project_df[project_df['Status'] == 'Done'])
        proj_completion = (proj_done / len(project_df) * 100) if len(project_df) > 0 else 0
        st.metric("✅ Done", f"{proj_done} ({proj_completion:.0f}%)")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Project Status")
        status_counts = project_df['Status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_map={
                'Open': '#d9938f',
                'Working on it': '#f4d89d',
                'Done': '#a8c9a1'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("👥 Team Members")
        team_counts = project_df['Assigned To'].value_counts()
        fig = px.bar(
            x=team_counts.index,
            y=team_counts.values,
            color_discrete_sequence=['#5f87af']
        )
        fig.update_layout(xaxis_title="Team Member", yaxis_title="Tasks", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Project tasks
    st.subheader("📋 Project Tasks")
    display_columns = ['Assigned To', 'Task', 'Status', 'Progress %', 'Due Date']
    st.dataframe(project_df[display_columns], use_container_width=True, height=400)

# Footer
st.divider()
st.caption("🔄 Data refreshes automatically every 30 seconds • Connected to Google Sheets")y

