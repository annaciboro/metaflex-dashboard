import streamlit as st
import pandas as pd
import re
from .dashboard_page import (
    load_google_sheet,
    get_column,
    has_column,
    render_editable_task_grid,
    render_page_header
)

def show_analytics():
    """
    Team Tasks Page - Shows all team tasks for Tea and Jess with editable grid
    """
    # Load data from Google Sheet
    with st.spinner("Loading team tasks..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Get current user
    user_name = st.session_state.get("name", "Téa Phillips")
    is_tea = user_name.lower() == "tea" or user_name.lower() == "tēa" or "tea" in user_name.lower()
    is_jess = "jess" in user_name.lower()

    # Filter data based on user
    if is_jess:
        # Jess sees her team's tasks (Jess, Megan, Justin)
        assignee_col = None
        if has_column(df, "Assigned To"):
            assignee_col = get_column(df, "Assigned To")
        elif has_column(df, "Person"):
            assignee_col = get_column(df, "Person")
        elif has_column(df, "assignee"):
            assignee_col = get_column(df, "assignee")

        if assignee_col:
            df = df[df[assignee_col].str.lower().str.contains('jess|megan|justin', na=False, regex=True)].copy()

    # Standardized header
    if is_jess:
        render_page_header("Team Task Management", f"Manage tasks for Jess, Megan, and Justin • {len(df)} total tasks")
    else:
        render_page_header("All Task Management", f"Edit fields directly, then sync to Google Sheets • {len(df)} total tasks")

    # Uniform spacing after header
    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    # Add analytics charts for All Tasks
    from charts import create_task_completion_velocity, create_project_health_dashboard
    from .dashboard_page import calculate_executive_overview

    # Calculate metrics for charts
    exec_metrics = calculate_executive_overview(df)

    # Two charts side by side
    chart_col1, chart_spacer, chart_col2 = st.columns([1, 0.1, 1])

    with chart_col1:
        st.markdown("<h4 style='color: #0a4b4b; margin-bottom: 16px;'>Completion Velocity</h4>", unsafe_allow_html=True)
        velocity_fig = create_task_completion_velocity(exec_metrics)
        if velocity_fig:
            st.plotly_chart(velocity_fig, width='stretch')

    with chart_col2:
        st.markdown("<h4 style='color: #0a4b4b; margin-bottom: 16px;'>Project Health</h4>", unsafe_allow_html=True)
        health_fig = create_project_health_dashboard(exec_metrics)
        if health_fig:
            st.plotly_chart(health_fig, width='stretch')

    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    # Render editable task grid for all tasks (with show_title=False to avoid duplicate header)
    render_editable_task_grid(df, user_name, is_tea=is_tea, show_title=False)
