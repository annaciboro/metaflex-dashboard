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
    render_page_header
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

    # Filter to show only OPEN tasks (exclude Done/Complete/Closed)
    if has_column(personal_df, "Status"):
        status_col = get_column(personal_df, "Status")
        personal_df = personal_df[~personal_df[status_col].str.lower().isin(['done', 'complete', 'completed', 'closed'])]

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
            st.markdown("<h3 style='text-align: left; margin: 0 0 20px 0; color: #0a4b4b; font-weight: 600; font-size: 1.1rem; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;'>Task Completion Status</h3>", unsafe_allow_html=True)
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
            st.markdown("<h3 style='text-align: left; margin: 0 0 20px 0; color: #0a4b4b; font-weight: 600; font-size: 1.1rem; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;'>Task Age Analysis</h3>", unsafe_allow_html=True)
            age_fig = create_task_age_analysis(personal_df)
            if age_fig:
                st.plotly_chart(age_fig, use_container_width=True, config={
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
        st.markdown("<h4 style='color: #0a4b4b; margin-bottom: 16px;'>Task Age Analysis</h4>", unsafe_allow_html=True)
        age_fig = create_task_age_analysis(personal_df)
        if age_fig:
            st.plotly_chart(age_fig, use_container_width=True, config={
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

                    # Append new row with all fields including Transcript ID and Date Added
                    new_row = [
                        new_transcript_id,
                        new_task,
                        user_name,
                        new_status,
                        new_project,
                        new_due_date,
                        new_progress,
                        new_date_added
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

    # Create a clean display DataFrame with all tasks - including row IDs
    display_columns = []

    # Add Transcript ID if it exists
    if has_column(personal_df, "Transcript ID"):
        display_columns.append(get_column(personal_df, "Transcript ID"))

    # Simplified columns for Tea: Task, Date Assigned, Due Date, Notes
    if is_tea:
        cols_to_display = ["Task", "Date Assigned", "Due Date", "Notes"]
    else:
        cols_to_display = ["Task", "Status", "Project", "Date Assigned", "Due Date", "Notes"]

    for col in cols_to_display:
        if has_column(personal_df, col):
            display_columns.append(get_column(personal_df, col))

    if display_columns:
        table_df = personal_df[display_columns].copy()

        # Remove suffix patterns from column names
        clean_data = {}
        for col in table_df.columns:
            clean_col = re.sub(r'__+.*$', '', str(col))
            clean_data[clean_col] = table_df[col].values

        clean_table_df = pd.DataFrame(clean_data)

        # Apply search filter if search term is provided
        if search_term:
            # Search across all text columns
            mask = clean_table_df.astype(str).apply(
                lambda row: row.str.contains(search_term, case=False, na=False).any(),
                axis=1
            )
            clean_table_df = clean_table_df[mask]

            if len(clean_table_df) == 0:
                st.warning(f"No tasks found matching '{search_term}'")
                return

            st.caption(f"Showing {len(clean_table_df)} of {len(personal_df)} tasks")

        # Store original dataframe with row indices for updates
        if 'task_edits' not in st.session_state:
            st.session_state.task_edits = clean_table_df.copy()

        # Configure column settings for editable table
        # All users can now set status to "Done"
        status_options = ["Open", "Working On It", "Done"]

        # Simplified column config for Tea
        if is_tea:
            column_config = {
                "Task": st.column_config.TextColumn(
                    "Task",
                    width="large",
                    help="Task description (editable)"
                ),
                "Date Assigned": st.column_config.TextColumn(
                    "Date Assigned",
                    width="small",
                    help="Date task was assigned"
                ),
                "Due Date": st.column_config.TextColumn(
                    "Due Date",
                    width="small",
                    help="Enter date as text (e.g., 2025-01-15)"
                ),
                "Notes": st.column_config.TextColumn(
                    "Notes",
                    width="large",
                    help="Additional notes or comments"
                )
            }
        else:
            column_config = {
                "Transcript ID": st.column_config.TextColumn(
                    "ID",
                    width="small",
                    help="Transcript/Row ID",
                    disabled=True  # Read-only
                ),
                "Task": st.column_config.TextColumn(
                    "Task",
                    width="large",
                    help="Task description (editable)"
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    width="small",
                    options=status_options,
                    required=True,
                    help="Change task status"
                ),
                "Project": st.column_config.TextColumn(
                    "Project",
                    width="medium"
                ),
                "Date Assigned": st.column_config.TextColumn(
                    "Date Assigned",
                    width="small",
                    help="Date task was assigned"
                ),
                "Due Date": st.column_config.TextColumn(
                    "Due Date",
                    width="small",
                    help="Enter date as text (e.g., 2025-01-15)"
                ),
                "Notes": st.column_config.TextColumn(
                    "Notes",
                    width="large",
                    help="Additional notes or comments"
                )
            }

        # Add MetaFlex premium light theme styling for tables
        st.markdown("""
            <style>
            /* Premium SaaS light theme styling for dataframes AND data_editor */
            div[data-testid="stDataFrame"],
            div[data-testid="stDataFrame"] > div,
            div[data-testid="stDataFrame"] > div > div,
            div[data-testid="stDataFrame"] iframe,
            [data-testid="stDataFrame"],
            div[data-testid="data-editor"],
            div[data-testid="data-editor"] > div,
            [data-testid="data-editor"] {
                background: #ffffff !important;
                border-radius: 0 0 12px 12px !important;
                padding: 16px !important;
                border: 1px solid #e5e7eb !important;
                border-top: none !important;
                box-shadow: 0 4px 12px rgba(10, 75, 75, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04) !important;
            }

            /* Target ALL table elements */
            div[data-testid="stDataFrame"] table,
            div[data-testid="stDataFrame"] thead,
            div[data-testid="stDataFrame"] tbody,
            [data-testid="stDataFrame"] table,
            div[data-testid="data-editor"] table,
            div[data-testid="data-editor"] thead,
            div[data-testid="data-editor"] tbody,
            table {
                background: transparent !important;
            }

            /* Style the table header - premium light theme */
            div[data-testid="stDataFrame"] thead tr th,
            div[data-testid="stDataFrame"] th,
            div[data-testid="data-editor"] thead tr th,
            div[data-testid="data-editor"] th,
            [data-testid="stDataFrame"] thead tr th,
            thead tr th,
            th {
                background: #f9fafb !important;
                color: #374151 !important;
                font-weight: 600 !important;
                border-bottom: 1px solid #e5e7eb !important;
                padding: 12px 8px !important;
                text-transform: uppercase !important;
                font-size: 0.7rem !important;
                letter-spacing: 0.05em !important;
            }

            /* Alternate row colors - subtle light gray */
            div[data-testid="stDataFrame"] tbody tr:nth-child(even),
            div[data-testid="stDataFrame"] tbody tr:nth-child(even) td,
            [data-testid="stDataFrame"] tbody tr:nth-child(even),
            tbody tr:nth-child(even),
            tbody tr:nth-child(even) td {
                background: #fafbfc !important;
                background-color: #fafbfc !important;
            }

            div[data-testid="stDataFrame"] tbody tr:nth-child(odd),
            div[data-testid="stDataFrame"] tbody tr:nth-child(odd) td,
            [data-testid="stDataFrame"] tbody tr:nth-child(odd),
            tbody tr:nth-child(odd),
            tbody tr:nth-child(odd) td {
                background: #ffffff !important;
                background-color: #ffffff !important;
            }

            /* Hover effect - subtle teal accent */
            div[data-testid="stDataFrame"] tbody tr:hover,
            div[data-testid="stDataFrame"] tbody tr:hover td,
            [data-testid="stDataFrame"] tbody tr:hover,
            div[data-testid="data-editor"] tbody tr:hover,
            div[data-testid="data-editor"] tbody tr:hover td,
            tbody tr:hover,
            tbody tr:hover td {
                background: rgba(10, 75, 75, 0.04) !important;
                background-color: rgba(10, 75, 75, 0.04) !important;
                box-shadow: inset 0 0 0 1px rgba(10, 75, 75, 0.1) !important;
                transition: all 0.2s ease !important;
            }

            /* Cell styling - dark gray text on light background */
            div[data-testid="stDataFrame"] tbody tr td,
            div[data-testid="stDataFrame"] td,
            [data-testid="stDataFrame"] tbody tr td,
            tbody tr td,
            td {
                border-bottom: 1px solid #f3f4f6 !important;
                padding: 12px 8px !important;
                color: #2d3748 !important;
            }

            /* Scrollbar styling for light theme */
            div[data-testid="stDataFrame"] ::-webkit-scrollbar {
                width: 8px !important;
                height: 8px !important;
            }

            div[data-testid="stDataFrame"] ::-webkit-scrollbar-track {
                background: #f3f4f6 !important;
                border-radius: 4px !important;
            }

            div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {
                background: #d1d5db !important;
                border-radius: 4px !important;
            }

            div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb:hover {
                background: #9ca3af !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Premium table header with gradient accent
        st.markdown("""
            <div style='
                background: linear-gradient(135deg, #0a4b4b 0%, #4d7a40 100%);
                height: 4px;
                border-radius: 4px 4px 0 0;
                margin-bottom: -1px;
                box-shadow: 0 2px 8px rgba(10, 75, 75, 0.3);
            '></div>
        """, unsafe_allow_html=True)

        # Display editable table
        edited_df = st.data_editor(
            clean_table_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            num_rows="dynamic",  # Allow adding/deleting rows
            key="task_editor"
        )

        # Handle save changes
        if save_changes:
            try:
                # Connect to Google Sheets
                scope = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"
                ]
                creds_dict = st.secrets["gcp_service_account"]
                from google.oauth2.service_account import Credentials
                import gspread
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                client = gspread.authorize(creds)
                sheet_id = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"
                sheet = client.open_by_key(sheet_id).worksheet("Otter_Tasks")

                # Update changed rows
                changes_made = False
                for idx, row in edited_df.iterrows():
                    # Check if row was modified
                    if idx < len(clean_table_df):
                        original_row = clean_table_df.iloc[idx]
                        if not row.equals(original_row):
                            # Find the row in Google Sheets by Transcript ID if available
                            if "Transcript ID" in row and pd.notna(row["Transcript ID"]):
                                # Update specific row by ID
                                row_num = idx + 2  # +2 for header and 0-indexing

                                # Update each column
                                for col_idx, col_name in enumerate(edited_df.columns):
                                    if col_name != "Transcript ID":
                                        cell_value = row[col_name]
                                        sheet.update_cell(row_num, col_idx + 1, str(cell_value))

                                changes_made = True

                if changes_made:
                    st.success("✅ Changes saved successfully!")
                    st.rerun()
                else:
                    st.info("No changes detected.")

            except Exception as e:
                st.error(f"Error saving changes: {str(e)}")
    else:
        st.info("No task details available to display.")
