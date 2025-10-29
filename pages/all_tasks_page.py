import streamlit as st
import pandas as pd
import re
from .dashboard_page import (
    load_google_sheet,
    get_column,
    has_column,
    render_editable_task_grid
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

    # Single clean header with title and task count on same row
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        if is_jess:
            st.markdown('<h1 style="font-family: \'Marcellus\', serif; font-size: 42px; font-weight: 600; color: #1a2424; margin: 0; letter-spacing: -0.02em;">Team Task Management</h1>', unsafe_allow_html=True)
            st.markdown('<p style="font-family: \'Inter\', sans-serif; font-size: 15px; color: #6a7878; margin-top: 8px; margin-bottom: 0; line-height: 1.6;">Manage tasks for Jess, Megan, and Justin</p>', unsafe_allow_html=True)
        else:
            st.markdown('<h1 style="font-family: \'Marcellus\', serif; font-size: 42px; font-weight: 600; color: #1a2424; margin: 0; letter-spacing: -0.02em;">All Task Management</h1>', unsafe_allow_html=True)
            st.markdown('<p style="font-family: \'Inter\', sans-serif; font-size: 15px; color: #6a7878; margin-top: 8px; margin-bottom: 0; line-height: 1.6;">Edit fields directly, then sync to Google Sheets</p>', unsafe_allow_html=True)

    with header_col2:
        st.markdown(f'<p style="font-family: \'Inter\', sans-serif; font-size: 16px; color: #2a3a3a; font-weight: 600; text-align: right; margin-top: 8px;">Total Tasks: {len(df)}</p>', unsafe_allow_html=True)

    # Uniform spacing after header
    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    # Render editable task grid for all tasks (with show_title=False to avoid duplicate header)
    render_editable_task_grid(df, user_name, is_tea=is_tea, show_title=False)
