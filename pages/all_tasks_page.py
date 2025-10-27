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
    All Tasks Page - Shows all tasks for all users with editable grid
    """
    # Load data from Google Sheet
    with st.spinner("Loading all tasks..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Get current user
    user_name = st.session_state.get("name", "Téa Phillips")
    is_tea = user_name == "Téa Phillips"

    # Single clean header with title and task count on same row
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        st.markdown('<h2 style="font-family: \'Marcellus\', serif; font-size: 32px; font-weight: 400; color: #2a3a3a; margin: 0;">All Task Management</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-family: \'Inter\', sans-serif; font-size: 15px; color: #7a8888; margin-top: 8px; margin-bottom: 0;">Edit fields directly, then sync to Google Sheets</p>', unsafe_allow_html=True)

    with header_col2:
        st.markdown(f'<p style="font-family: \'Inter\', sans-serif; font-size: 16px; color: #2a3a3a; font-weight: 600; text-align: right; margin-top: 8px;">Total Tasks: {len(df)}</p>', unsafe_allow_html=True)

    # Uniform spacing after header
    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

    # Render editable task grid for all tasks (with show_title=False to avoid duplicate header)
    render_editable_task_grid(df, user_name, is_tea=is_tea, show_title=False)
