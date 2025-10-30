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

    # Filter data based on user - ONLY Tea sees all tasks
    if is_tea:
        # Tea sees everyone's tasks - no filtering
        pass
    elif is_jess:
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
    else:
        # Other users (Megan, Justin, etc.) should only see their own tasks
        assignee_col = None
        if has_column(df, "Assigned To"):
            assignee_col = get_column(df, "Assigned To")
        elif has_column(df, "Person"):
            assignee_col = get_column(df, "Person")
        elif has_column(df, "assignee"):
            assignee_col = get_column(df, "assignee")

        if assignee_col:
            df = df[df[assignee_col].str.lower().str.contains(user_name.lower(), na=False, regex=False)].copy()

    # Page header matching MY TASKS style
    st.markdown("""
        <h2 style='
            margin: 0 0 32px 0;
            font-size: 2rem;
            font-weight: 700;
            color: #0a4b4b;
            letter-spacing: -0.01em;
            text-align: left;
        '>ALL TASKS</h2>
    """, unsafe_allow_html=True)

    # Add control checkboxes in a row
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 3])

    with ctrl_col1:
        show_archived = st.checkbox("Show Archived", value=False, key="show_archived_all_tasks")

    with ctrl_col2:
        show_transcript_id = st.checkbox("Show Transcript #", value=False, key="show_transcript_all_tasks")

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter to show only OPEN tasks (exclude Done/Complete/Closed) unless "Show Archived" is checked
    if has_column(df, "Status") and not show_archived:
        status_col = get_column(df, "Status")
        df = df[~df[status_col].str.lower().isin(['done', 'complete', 'completed', 'closed'])].copy()

    # Add analytics charts for All Tasks
    from charts import create_task_completion_velocity, create_project_health_dashboard, create_tasks_by_user_chart
    from .dashboard_page import calculate_executive_metrics

    # Calculate metrics for charts
    exec_metrics = calculate_executive_metrics(df)

    # Two charts side by side
    chart_col1, chart_spacer, chart_col2 = st.columns([1, 0.1, 1])

    with chart_col1:
        velocity_fig = create_task_completion_velocity(exec_metrics)
        if velocity_fig:
            st.plotly_chart(velocity_fig, use_container_width=True)

    with chart_col2:
        health_fig = create_project_health_dashboard(exec_metrics)
        if health_fig:
            st.plotly_chart(health_fig, use_container_width=True)

    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    # Add Tasks by User chart for Tea only
    if is_tea:
        st.markdown("<h3 style='text-align: left; margin: 0 0 20px 0; color: #0a4b4b; font-weight: 600; font-size: 1.1rem; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;'>Tasks by User</h3>", unsafe_allow_html=True)
        tasks_by_user_fig = create_tasks_by_user_chart(df)
        if tasks_by_user_fig:
            st.plotly_chart(tasks_by_user_fig, use_container_width=True)
        st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    # Render editable task grid for all tasks (with show_title=False to avoid duplicate header)
    # Note: The render_editable_task_grid function doesn't support show_transcript_id parameter yet
    # For now, we'll just pass the show_transcript_id as a session state variable
    st.session_state['show_transcript_id_all_tasks'] = show_transcript_id
    render_editable_task_grid(df, user_name, is_tea=is_tea, show_title=False)
