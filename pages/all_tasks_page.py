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
    st.markdown("### All Tasks")
    st.caption("Complete task list for all team members")
    st.markdown("<br>", unsafe_allow_html=True)

    # Load data from Google Sheet
    with st.spinner("Loading all tasks..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Get current user
    user_name = st.session_state.get("name", "Téa Phillips")
    is_tea = user_name == "Téa Phillips"

    # Show task count
    st.markdown(f"**Total Tasks:** {len(df)}")
    st.markdown("<br>", unsafe_allow_html=True)

    # Render editable task grid for all tasks
    render_editable_task_grid(df, user_name, is_tea=is_tea)
