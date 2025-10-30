import streamlit as st
import pandas as pd
import re
from .dashboard_page import (
    load_google_sheet,
    get_column,
    has_column,
    calculate_kpis,
    render_kpi_section,
    render_charts_section,
    render_tasks_table,
    render_page_header,
    render_editable_task_grid
)

def show_tasks():
    """
    My Tasks Page - Shows user's personal tasks with KPIs and charts
    """
    # Get logged-in user's name from session state
    user_name = st.session_state.get("name", "User")
    first_name = user_name.split()[0] if user_name else "User"

    # Determine if user is Tea (admin sees everything)
    is_tea = user_name.lower() == "tea" or user_name.lower() == "tēa" or "tea" in user_name.lower()
    is_jess = "jess" in user_name.lower()

    # Page header matching Executive Overview style
    st.markdown("""
        <h2 style='
            margin: 0 0 32px 0;
            font-size: 2rem;
            font-weight: 700;
            color: #0a4b4b;
            letter-spacing: -0.01em;
            text-align: left;
        '>MY TASKS</h2>
    """, unsafe_allow_html=True)

    # Load data from Google Sheet
    with st.spinner("Loading your tasks..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Style checkboxes to match header styling
    st.markdown("""
        <style>
        /* Checkbox label styling to match headers */
        div[data-testid="stCheckbox"] label p {
            color: #0a4b4b !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
        }

        /* Checkbox styling - teal theme */
        div[data-testid="stCheckbox"] input[type="checkbox"] ~ span div svg rect {
            fill: rgba(229, 231, 235, 0.5) !important;
            stroke: rgba(10, 75, 75, 0.4) !important;
            stroke-width: 1.5 !important;
        }

        div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ span div svg rect {
            fill: #0a4b4b !important;
            stroke: #0a4b4b !important;
        }

        div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ span div svg path {
            fill: #ffffff !important;
            stroke: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Filter for user's tasks based on assignee column
    assignee_col = None
    if has_column(df, "Assigned To"):
        assignee_col = get_column(df, "Assigned To")
    elif has_column(df, "Person"):
        assignee_col = get_column(df, "Person")
    elif has_column(df, "assignee"):
        assignee_col = get_column(df, "assignee")

    if assignee_col:
        # For Tea, show all tasks; for everyone else (including Jess), filter by user name
        if is_tea:
            personal_df = df.copy()
        else:
            # All users (Jess, Megan, Justin) see only their own personal tasks on "My Tasks"
            personal_df = df[df[assignee_col].str.lower().str.contains(user_name.lower(), na=False)].copy()
    else:
        personal_df = pd.DataFrame()

    if personal_df.empty:
        st.info(f"No open tasks assigned to {first_name}.")
        return

    # Calculate personal KPIs from filtered data (only open tasks)
    personal_kpis = calculate_kpis(personal_df, user_name, is_personal=True)

    # For regular users (Megan, Justin, Jess), show chart above everything
    # For Tea only, show all KPIs and charts below
    if not is_tea:
        # Show Task Completion Status donut chart at the top for regular users
        from charts import create_team_completion_donut

        # Create columns for both charts to display side by side
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("""
                <h3 style='
                    margin: 0 0 20px 0;
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #0a4b4b;
                    letter-spacing: 0.05em;
                    text-align: left;
                    text-transform: uppercase;
                '>TASK COMPLETION STATUS</h3>
            """, unsafe_allow_html=True)
            donut_fig = create_team_completion_donut(
                personal_kpis.get("my_open_tasks", 0),
                personal_kpis.get("working_tasks", 0),
                personal_kpis.get("done_tasks", 0)
            )

            if donut_fig:
                st.plotly_chart(donut_fig, use_container_width=True, config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'task_completion_status',
                        'height': 500,
                        'width': 700,
                        'scale': 2
                    }
                })

        # Add Task Age Analysis chart for all users
        from charts import create_task_age_analysis

        with chart_col2:
            st.markdown("""
                <h3 style='
                    margin: 0 0 20px 0;
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #0a4b4b;
                    letter-spacing: 0.05em;
                    text-align: left;
                    text-transform: uppercase;
                '>TASK AGE ANALYSIS</h3>
            """, unsafe_allow_html=True)
            age_fig = create_task_age_analysis(personal_df)
            if age_fig:
                st.plotly_chart(age_fig, use_container_width=True, key="task_age_chart", config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'task_age_analysis',
                        'height': 500,
                        'width': 700,
                        'scale': 2
                    }
                })

        st.markdown("<br>", unsafe_allow_html=True)
    else:
        # Tea sees full KPI metrics
        my_open_tasks = len(personal_df)

        # Count active projects
        active_projects = 0
        if has_column(personal_df, "Project"):
            project_col = get_column(personal_df, "Project")
            active_projects = personal_df[project_col].nunique()

        # Display KPI Metrics (only showing MY data, not team data)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="MY OPEN TASKS",
                value=my_open_tasks,
                delta=None
            )

        with col2:
            st.metric(
                label="ACTIVE PROJECTS",
                value=active_projects,
                delta=None
            )

        with col3:
            # Calculate completion rate
            if has_column(personal_df, "Progress %"):
                try:
                    progress_col = get_column(personal_df, "Progress %")
                    # Convert to numeric, coerce errors to NaN
                    progress_numeric = pd.to_numeric(personal_df[progress_col], errors='coerce')
                    avg_progress = int(progress_numeric.fillna(0).mean())
                    st.metric(
                        label="AVG PROGRESS",
                        value=f"{avg_progress}%",
                        delta=None
                    )
                except Exception as e:
                    st.metric(
                        label="AVG PROGRESS",
                        value="N/A",
                        delta=None
                    )
            else:
                st.metric(
                    label="AVG PROGRESS",
                    value="N/A",
                    delta=None
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Add Task Age Analysis chart for Tea
        from charts import create_task_age_analysis
        st.markdown("""
            <h3 style='
                margin: 0 0 20px 0;
                font-size: 1.1rem;
                font-weight: 700;
                color: #0a4b4b;
                letter-spacing: 0.05em;
                text-align: left;
                text-transform: uppercase;
            '>TASK AGE ANALYSIS</h3>
        """, unsafe_allow_html=True)
        age_fig = create_task_age_analysis(personal_df)
        if age_fig:
            st.plotly_chart(age_fig, use_container_width=True, key="tea_task_age_chart", config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'task_age_analysis',
                    'height': 500,
                    'width': 700,
                    'scale': 2
                }
            })

        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display all personal OPEN tasks - with no limit
    # For regular users (Megan, Justin, Jess), just show the count; for Tea, show "My Open Tasks"
    if is_tea:
        st.markdown(f"<h2 style='text-align: left; font-size: 1.75rem; font-weight: 700; color: #0a4b4b; margin: 24px 0 16px 0;'>My Open Tasks ({len(personal_df)} total)</h2>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2 style='text-align: left; font-size: 1.75rem; font-weight: 700; color: #0a4b4b; margin: 24px 0 16px 0;'>{len(personal_df)} Open Tasks</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Add "Add New Task" and "Save Changes" buttons with KPI card styling
    st.markdown("""
        <style>
        /* KPI card-style buttons - matching the pale forest green gradient */
        button[kind="secondary"], button[kind="primary"] {
            background: linear-gradient(135deg, #f5faf2 0%, #f8fbf8 100%) !important;
            color: #2d5016 !important;
            border: 1px solid #e8eced !important;
            border-left: 4px solid #0a4b4b !important;
            font-weight: 700 !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        }
        button[kind="secondary"]:hover, button[kind="primary"]:hover {
            background: linear-gradient(135deg, #f0f5ec 0%, #f5faf2 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(10, 75, 75, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
            border-left-color: #0a4b4b !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Search and action buttons in one row - search left, buttons right
    col_search, col_spacer, col_btn1, col_btn2 = st.columns([3, 0.5, 1, 1])

    with col_search:
        search_term = st.text_input("Search tasks", placeholder="Type to search by task name, project, or status...", key="search_tasks", label_visibility="collapsed")

    with col_btn1:
        add_task = st.button("Add New Task", key="add_task_btn", width='stretch')

    with col_btn2:
        save_changes = st.button("Save Changes", key="save_changes_btn", type="primary", width='stretch')

    st.markdown("<br>", unsafe_allow_html=True)

    # Handle adding new task
    if add_task:
        st.session_state.show_add_task_form = True

    if st.session_state.get("show_add_task_form", False):
        with st.form("new_task_form"):
            st.markdown("#### Add New Task")

            col1, col2 = st.columns(2)
            with col1:
                new_transcript_id = st.text_input("Transcript ID", help="Unique identifier for this task")
                new_task = st.text_input("Task Description *", help="Required")
                new_project = st.text_input("Project")
                new_progress = st.slider("Progress %", 0, 100, 0)

            with col2:
                import datetime
                new_date_added = st.text_input("Date Added", value=datetime.date.today().strftime("%m/%d/%Y"), help="Format: MM/DD/YYYY")
                # All users can set status to "Done"
                new_status = st.selectbox("Status", ["Open", "Working On It", "Done"])
                new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)  # Default to Medium
                new_due_date = st.text_input("Due Date", help="Format: MM/DD/YYYY")

            st.markdown("<br>", unsafe_allow_html=True)

            col_submit, col_cancel = st.columns(2)
            with col_submit:
                st.markdown("""
                    <style>
                    /* KPI card-style for form submit buttons */
                    button[kind="formSubmit"] {
                        background: linear-gradient(135deg, #f5faf2 0%, #f8fbf8 100%) !important;
                        color: #2d5016 !important;
                        border: 1px solid #e8eced !important;
                        border-left: 4px solid #0a4b4b !important;
                        font-weight: 700 !important;
                        width: 100% !important;
                        border-radius: 8px !important;
                        padding: 12px 24px !important;
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02) !important;
                    }
                    button[kind="formSubmit"]:hover {
                        background: linear-gradient(135deg, #f0f5ec 0%, #f5faf2 100%) !important;
                        transform: translateY(-2px) !important;
                        box-shadow: 0 4px 12px rgba(10, 75, 75, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
                        border-left-color: #0a4b4b !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                submit = st.form_submit_button("Add Task")
            with col_cancel:
                cancel = st.form_submit_button("Cancel")

            if submit and new_task:
                # Add new task to Google Sheet
                try:
                    scope = [
                        "https://spreadsheets.google.com/feeds",
                        "https://www.googleapis.com/auth/drive"
                    ]
                    creds_dict = st.secrets["gcp_service_account"]
                    from google.oauth2.service_account import Credentials
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                    import gspread
                    client = gspread.authorize(creds)
                    sheet_id = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"
                    sheet = client.open_by_key(sheet_id).worksheet("Otter_Tasks")

                    # Append new row with all fields including Transcript ID, Date Added, and Priority
                    # Column order: Transcript, Date Assigned, Person, Task, Project, Status, Due Date, Notes, Progress %, (empty cols), Priority (col 14)
                    # For append_row, we need to specify values up to column 14
                    new_row = [
                        new_transcript_id,      # Col 1: Transcript
                        new_date_added,         # Col 2: Date Assigned
                        user_name,              # Col 3: Person
                        new_task,               # Col 4: Task
                        new_project,            # Col 5: Project
                        new_status,             # Col 6: Status
                        new_due_date,           # Col 7: Due Date
                        "",                     # Col 8: Notes (empty)
                        new_progress,           # Col 9: Progress %
                        "", "", "", "",         # Cols 10-13: Empty
                        new_priority            # Col 14: Priority
                    ]
                    sheet.append_row(new_row)

                    st.success("Task added successfully!")
                    st.session_state.show_add_task_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {str(e)}")

            if cancel:
                st.session_state.show_add_task_form = False
                st.rerun()

    # Add control checkboxes right above the table
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 3])

    with ctrl_col1:
        show_archived = st.checkbox("Show Archived", value=False, key="show_archived_my_tasks")

    with ctrl_col2:
        show_transcript_id = st.checkbox("Show Transcript #", value=False, key="show_transcript_my_tasks")

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter to show only OPEN tasks (exclude Done/Complete/Closed) unless "Show Archived" is checked
    if has_column(personal_df, "Status") and not show_archived:
        status_col = get_column(personal_df, "Status")
        personal_df = personal_df[~personal_df[status_col].str.lower().isin(['done', 'complete', 'completed', 'closed'])]

    # Use the same AgGrid table as All Tasks page, but filtered for individual user
    # Pass show_transcript_id via session state
    st.session_state['show_transcript_id_my_tasks'] = show_transcript_id

    # Render editable task grid (same as All Tasks but filtered for user)
    render_editable_task_grid(personal_df, user_name, is_tea=is_tea, key_prefix="my_tasks_", show_title=False)
