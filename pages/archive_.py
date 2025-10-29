import streamlit as st
import pandas as pd
import re
from .dashboard_page import (
    load_google_sheet,
    get_column,
    has_column,
    render_tasks_table
)

def show_archive():
    """
    Archive Page - Shows completed/done tasks (filtered by user for non-Tea users)
    """
    # Get current user from session state
    user_name = st.session_state.get("name", "User")
    first_name = user_name.split()[0] if user_name else "User"
    is_tea = user_name.lower() == "tea" or user_name.lower() == "tēa" or "tea" in user_name.lower()
    is_jess = "jess" in user_name.lower()

    st.markdown(f"### {first_name}'s Archive")
    st.caption("All completed tasks")
    st.markdown("<br>", unsafe_allow_html=True)

    # Load data from Google Sheet
    with st.spinner("Loading archived tasks..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Filter by user if not Tea or Jess
    if not is_tea and not is_jess:
        # Try different possible column names for assignee
        assignee_col = None
        if has_column(df, "Assigned To"):
            assignee_col = get_column(df, "Assigned To")
        elif has_column(df, "assignee"):
            assignee_col = get_column(df, "assignee")
        elif has_column(df, "Person"):
            assignee_col = get_column(df, "Person")

        if assignee_col:
            df = df[df[assignee_col].str.lower().str.contains(user_name.lower(), na=False)].copy()
        else:
            st.error(f"Cannot filter tasks: No assignee column found. Available columns: {', '.join(df.columns.tolist())}")
            return
    elif is_jess:
        # Jess sees her, Megan's, and Justin's archived tasks
        assignee_col = None
        if has_column(df, "Assigned To"):
            assignee_col = get_column(df, "Assigned To")
        elif has_column(df, "assignee"):
            assignee_col = get_column(df, "assignee")
        elif has_column(df, "Person"):
            assignee_col = get_column(df, "Person")

        if assignee_col:
            df = df[df[assignee_col].str.lower().str.contains('jess|megan|justin', na=False, regex=True)].copy()

    # Filter for done tasks only
    if has_column(df, "Status"):
        status_col = get_column(df, "Status")
        # Filter for done/complete status (case-insensitive)
        archived_df = df[df[status_col].str.strip().str.lower().isin(['done', 'complete', 'completed'])]
    else:
        st.warning("Status column not found in data.")
        return

    if archived_df.empty:
        st.info("No archived tasks found. Tasks marked as 'Done' will appear here.")
        return

    # Show archived task count
    st.markdown(f"**Total Archived Tasks:** {len(archived_df)}")
    st.markdown("<br>", unsafe_allow_html=True)

    # Add search functionality
    search_term = st.text_input("🔍 Search archived tasks", placeholder="Search by keywords...", key="search_archive")

    if search_term:
        # Search across all columns
        search_mask = archived_df.astype(str).apply(
            lambda row: row.str.contains(search_term, case=False, na=False).any(),
            axis=1
        )
        archived_df = archived_df[search_mask]

        if len(archived_df) == 0:
            st.warning(f"No archived tasks found matching '{search_term}'")
            return

        st.caption(f"Showing {len(archived_df)} archived tasks")

    st.markdown("<br>", unsafe_allow_html=True)

    # Display archived tasks grouped by project
    if has_column(archived_df, "Project"):
        project_col = get_column(archived_df, "Project")
        unique_projects = archived_df[project_col].str.strip().str.title().dropna().unique()
        unique_projects = sorted([p for p in unique_projects if p])

        if len(unique_projects) > 0:
            st.markdown("### Archived Tasks by Project")
            st.markdown("<br>", unsafe_allow_html=True)

            for project_name in unique_projects:
                project_df = archived_df[archived_df[project_col].str.strip().str.lower() == project_name.lower()]
                task_count = len(project_df)

                st.markdown(f"#### {project_name} ({task_count} archived tasks)")

                if not project_df.empty:
                    render_tasks_table(project_df, limit=1000)

                st.markdown("<br>", unsafe_allow_html=True)
        else:
            # No projects, just show all archived tasks
            st.markdown("### All Archived Tasks")
            render_tasks_table(archived_df, limit=1000)
    else:
        # No project column, just show all archived tasks
        st.markdown("### All Archived Tasks")
        render_tasks_table(archived_df, limit=1000)
