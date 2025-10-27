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
    render_tasks_table
)

def show_tasks():
    """
    Téa's Tasks Page - Shows all of Téa's personal tasks with KPIs and charts
    """
    st.markdown("### Téa's Tasks")
    st.caption("Your personal workload overview")
    st.markdown("<br>", unsafe_allow_html=True)

    # Load data from Google Sheet
    with st.spinner("Loading your tasks..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Filter for Téa's tasks only
    user_name = "Téa Phillips"
    if has_column(df, "Person"):
        person_col = get_column(df, "Person")
        personal_df = df[df[person_col].str.contains("Téa", case=False, na=False)]
    elif has_column(df, "Assigned To"):
        person_col = get_column(df, "Assigned To")
        personal_df = df[df[person_col].str.contains("Téa", case=False, na=False)]
    else:
        personal_df = pd.DataFrame()

    # Filter to show only OPEN tasks (exclude Done/Complete/Closed)
    if has_column(personal_df, "Status"):
        status_col = get_column(personal_df, "Status")
        personal_df = personal_df[~personal_df[status_col].str.lower().isin(['done', 'complete', 'completed', 'closed'])]

    if personal_df.empty:
        st.info("No open tasks assigned to Téa.")
        return

    # Calculate personal KPIs from filtered data (only open tasks)
    my_open_tasks = len(personal_df)

    # Count active projects
    active_projects = 0
    if has_column(personal_df, "Project"):
        project_col = get_column(personal_df, "Project")
        active_projects = personal_df[project_col].nunique()

    # Calculate KPIs for charts (using calculate_kpis function)
    personal_kpis = calculate_kpis(personal_df, user_name, is_personal=True)

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

    # Display Charts
    render_charts_section(personal_kpis, personal_df)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display all personal OPEN tasks - with no limit
    st.markdown(f"### My Open Tasks ({len(personal_df)} total)")
    st.markdown("<br>", unsafe_allow_html=True)

    # Add search box
    search_term = st.text_input("🔍 Search tasks", placeholder="Type to search by task name, project, or status...", key="search_tasks")

    st.markdown("<br>", unsafe_allow_html=True)

    # Create a clean display DataFrame with all tasks
    display_columns = []
    for col in ["Task", "Status", "Project", "Due Date", "Progress %"]:
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

        # Add progress status with colors matching pie chart
        if "Progress %" in clean_table_df.columns:
            def create_progress_display(value):
                try:
                    val_str = str(value).strip().replace('%', '')
                    if val_str == '' or val_str.lower() == 'nan':
                        val = 0
                    else:
                        val = float(val_str)
                except:
                    val = 0

                # Use colored circles matching the pie chart colors
                if val == 0:
                    indicator = "🔴"  # Red for Not Started (coral in chart)
                    status = "Not Started"
                elif val < 100:
                    indicator = "🟡"  # Yellow for In Progress (lime in chart)
                    status = "In Progress"
                else:
                    indicator = "🟢"  # Green for Completed (sage in chart)
                    status = "Complete"

                return f"{indicator} {status}"

            clean_table_df["Progress Status"] = clean_table_df["Progress %"].apply(create_progress_display)
            clean_table_df = clean_table_df.drop(columns=["Progress %"])

            # Reorder columns to put Progress Status after Status
            cols = clean_table_df.columns.tolist()
            if "Progress Status" in cols and "Status" in cols:
                cols.remove("Progress Status")
                status_idx = cols.index("Status")
                cols.insert(status_idx + 1, "Progress Status")
                clean_table_df = clean_table_df[cols]

        # Configure column settings
        column_config = {
            "Task": st.column_config.TextColumn(
                "Task",
                width="large",
                help="Task description"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                width="small"
            ),
            "Project": st.column_config.TextColumn(
                "Project",
                width="medium"
            ),
            "Due Date": st.column_config.TextColumn(
                "Due Date",
                width="small"
            ),
            "Progress Status": st.column_config.TextColumn(
                "Progress Status",
                help="Task completion status",
                width="medium"
            )
        }

        # Compact table height - fits on page without scrolling
        st.markdown("""
            <style>
            [data-testid="stDataFrame"] {
                max-height: 500px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Display the full table
        st.dataframe(
            clean_table_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
    else:
        st.info("No task details available to display.")
