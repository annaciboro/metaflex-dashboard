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

    if personal_df.empty:
        st.info("No tasks assigned to Téa.")
        return

    # Calculate personal KPIs
    personal_kpis = calculate_kpis(personal_df, user_name, is_personal=True)

    # Display KPI Metrics
    render_kpi_section(personal_kpis)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display Charts
    render_charts_section(personal_kpis, personal_df)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display all personal tasks - with no limit
    st.markdown(f"### All My Tasks ({len(personal_df)} total)")
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

        # Add progress status with colors
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

                if val == 0:
                    color = "🔴"
                    status = "Not Started"
                elif val < 100:
                    color = "🟡"
                    status = "In Progress"
                else:
                    color = "🟢"
                    status = "Complete"

                filled_blocks = int(val / 10)
                empty_blocks = 10 - filled_blocks
                bar = "█" * filled_blocks + "░" * empty_blocks

                return f"{color} {bar} {int(val)}%"

            clean_table_df["Progress"] = clean_table_df["Progress %"].apply(create_progress_display)
            clean_table_df = clean_table_df.drop(columns=["Progress %"])

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
            "Progress": st.column_config.TextColumn(
                "Progress",
                help="Task completion progress",
                width="medium"
            )
        }

        # Add responsive CSS for table height
        st.markdown("""
            <style>
            /* Make table taller on larger screens, responsive on smaller */
            [data-testid="stDataFrame"] {
                height: calc(100vh - 500px) !important;
                min-height: 400px !important;
                max-height: 900px !important;
            }

            /* Adjust for mobile/tablet */
            @media (max-width: 768px) {
                [data-testid="stDataFrame"] {
                    height: calc(100vh - 600px) !important;
                    min-height: 300px !important;
                }
            }

            /* Adjust for small mobile */
            @media (max-width: 480px) {
                [data-testid="stDataFrame"] {
                    height: calc(100vh - 650px) !important;
                    min-height: 250px !important;
                }
            }
            </style>
        """, unsafe_allow_html=True)

        # Display the full table
        st.dataframe(
            clean_table_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            height=None  # Let CSS handle the height
        )
    else:
        st.info("No task details available to display.")
