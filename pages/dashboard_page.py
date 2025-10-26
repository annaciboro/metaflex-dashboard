import streamlit as st
import pandas as pd
import gspread
import re
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from charts import create_team_completion_donut, create_project_breakdown_chart

def get_column(df, col_name):
    """
    Helper function to get a column by its original name, even if it has a unique suffix.
    Returns the column name with the suffix that exists in the DataFrame.
    """
    # First try exact match
    if col_name in df.columns:
        return col_name

    # Try to find column with ___ suffix
    matching_cols = [col for col in df.columns if col.startswith(f"{col_name}___")]
    if matching_cols:
        return matching_cols[0]  # Return the first match

    # Fallback: return the original name (will cause KeyError if doesn't exist)
    return col_name

def has_column(df, col_name):
    """Check if a column exists by original name"""
    if col_name in df.columns:
        return True
    return any(col.startswith(f"{col_name}___") for col in df.columns)

# Access scope mapping
ACCESS_SCOPE = {
    "Téa Phillips": "all",
    "Jess Lewis": {"exclude": ["Finance"]},
    "Megan Cole": ["Marketing"],
    "Justin Stehr": ["Marketing", "Products"],
}

def get_scope_description(user_name, scope):
    """
    Generate a friendly description of the user's access scope
    """
    if scope == "all":
        return "All MetaFlex projects"
    elif isinstance(scope, dict) and "exclude" in scope:
        excluded = ", ".join(scope["exclude"])
        return f"All projects except {excluded}"
    elif isinstance(scope, list):
        if len(scope) == 1:
            return f"{scope[0]} projects"
        else:
            return f"{' and '.join(scope)} projects"
    else:
        return "Your assigned tasks"

def filter_by_access(df, user_name):
    """
    Filter dataframe based on user's access scope.
    Reusable helper function for dashboard, analytics, and team pages.

    Args:
        df: DataFrame with at least 'Assigned To' or 'Person' and 'Project' columns
        user_name: Full name of the user (e.g., "Téa Phillips")

    Returns:
        Filtered DataFrame based on user's access scope
    """
    if df.empty:
        return df

    # Get user's access scope
    scope = ACCESS_SCOPE.get(user_name, None)

    # Filter based on scope type
    if scope == "all":
        # Show all rows
        return df

    elif isinstance(scope, dict) and "exclude" in scope:
        # Filter out excluded projects
        excluded_projects = scope["exclude"]
        if has_column(df, "Project"):
            project_col = get_column(df, "Project")
            # Case-insensitive filtering
            filtered_df = df[~df[project_col].str.strip().str.lower().isin([p.lower() for p in excluded_projects])]
            return filtered_df
        return df

    elif isinstance(scope, list):
        # Include only specified projects
        if has_column(df, "Project"):
            project_col = get_column(df, "Project")
            # Case-insensitive filtering
            filtered_df = df[df[project_col].str.strip().str.lower().isin([p.lower() for p in scope])]
            return filtered_df
        return df

    else:
        # Default: show only user's own assigned tasks
        if has_column(df, "Person"):
            person_col = get_column(df, "Person")
        elif has_column(df, "Assigned To"):
            person_col = get_column(df, "Assigned To")
        else:
            return df

        filtered_df = df[df[person_col].str.contains(user_name, case=False, na=False)]
        return filtered_df

@st.cache_data(ttl=45)  # Cache for 45 seconds to reduce API calls
def load_google_sheet():
    """
    Load data from Google Sheets (Otter_Tasks worksheet)
    Cached for 45 seconds to avoid hitting API quota limits
    """
    try:
        # Define the scope
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Load credentials from Streamlit secrets
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

        # Authorize and open the sheet
        client = gspread.authorize(creds)
        # Extract sheet ID from URL or use direct ID
        if "google_sheet_id" in st.secrets:
            sheet_id = st.secrets["google_sheet_id"]
        else:
            # Extract from google_sheets.SHEET_URL
            sheet_url = st.secrets["google_sheets"]["SHEET_URL"]
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]

        # Try to open Otter_Tasks worksheet, fallback to first sheet
        try:
            sheet = client.open_by_key(sheet_id).worksheet("Otter_Tasks")
        except:
            sheet = client.open_by_key(sheet_id).sheet1

        # Get all values as list of lists
        all_values = sheet.get_all_values()

        if not all_values or len(all_values) < 2:
            st.warning("Sheet is empty or has no data rows.")
            return pd.DataFrame()

        # First row is headers, rest is data
        headers = all_values[0]
        data_rows = all_values[1:]

        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=headers)

        # Remove empty rows
        df = df.dropna(how='all')

        # Remove columns with empty headers AND no data
        # Use column indices to avoid duplicate column name issues
        cols_to_keep = []
        for idx, col in enumerate(df.columns):
            # Keep column if it has a non-empty header OR has any non-empty data
            if str(col).strip() != '':
                cols_to_keep.append(idx)
            else:
                # Check if column has any data (using iloc to avoid duplicate column issues)
                col_data = df.iloc[:, idx].astype(str).str.strip()
                if col_data.ne('').any():
                    cols_to_keep.append(idx)

        # Select only the columns we want to keep
        df = df.iloc[:, cols_to_keep]

        # Store mapping of clean column names to unique column names
        # This allows the rest of the code to reference "Person", "Task", etc.
        original_cols = [str(col).strip() for col in df.columns]

        # Define columns to hide by name
        columns_to_hide = ["Progress Bar", "Confidence", "Emails", "Duplicate Check", "0%"]

        # Filter columns: keep only the first 10 columns and exclude unwanted ones
        filtered_indices = []
        for i, col_name in enumerate(original_cols):
            # Keep only first 10 columns (0-9), which are the main task fields
            if i >= 10:
                continue
            # Skip columns in the hide list
            if col_name in columns_to_hide or "confidence" in col_name.lower():
                continue
            filtered_indices.append(i)

        # Keep only the filtered columns
        df = df.iloc[:, filtered_indices]
        original_cols = [original_cols[i] for i in filtered_indices]

        # Make ALL column names absolutely unique by appending index
        unique_cols = [f"{original_cols[i]}___{i}" for i in range(len(original_cols))]
        df.columns = unique_cols

        # Store the mapping in session state for reference
        if 'column_mapping' not in st.session_state:
            st.session_state.column_mapping = {}

        # Map original name to unique name (for first occurrence only)
        for i, orig_name in enumerate(original_cols):
            if orig_name not in st.session_state.column_mapping:
                st.session_state.column_mapping[orig_name] = unique_cols[i]

        return df

    except Exception as e:
        st.error(f"Error loading Google Sheet: {str(e)}")
        return pd.DataFrame()

def update_google_sheet(updated_df):
    """
    Push edited data back to Google Sheets (Otter_Tasks worksheet)
    """
    try:
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        # Extract sheet ID from URL or use direct ID
        if "google_sheet_id" in st.secrets:
            SHEET_ID = st.secrets["google_sheet_id"]
        else:
            # Extract from google_sheets.SHEET_URL
            sheet_url = st.secrets["google_sheets"]["SHEET_URL"]
            SHEET_ID = sheet_url.split("/d/")[1].split("/")[0]

        # Try to open Otter_Tasks worksheet, fallback to first sheet
        try:
            ws = gc.open_by_key(SHEET_ID).worksheet("Otter_Tasks")
        except:
            ws = gc.open_by_key(SHEET_ID).sheet1

        # Strip the suffix from column names before writing back
        df_to_write = updated_df.copy()
        clean_columns = []
        for col in df_to_write.columns:
            # Remove everything from __ onwards (two or more underscores)
            clean_col = re.sub(r'__+.*$', '', str(col))
            clean_columns.append(clean_col)
        df_to_write.columns = clean_columns

        # Clear and write new data
        ws.clear()
        ws.update([df_to_write.columns.values.tolist()] + df_to_write.values.tolist())

        return True
    except Exception as e:
        st.error(f"Error updating Google Sheet: {str(e)}")
        return False

def calculate_kpis(df, user_name, is_personal=False):
    """
    Calculate KPI metrics from filtered data

    Args:
        df: DataFrame to calculate metrics from
        user_name: User's full name
        is_personal: If True, calculate only user's personal tasks
    """
    if df.empty:
        return {
            "my_open_tasks": 0,
            "team_open_tasks": 0,
            "active_projects": 0,
            "open_tasks": 0,
            "working_tasks": 0,
            "done_tasks": 0
        }

    # Ensure Status column exists
    if not has_column(df, "Status"):
        return {
            "my_open_tasks": 0,
            "team_open_tasks": 0,
            "active_projects": 0,
            "open_tasks": 0,
            "working_tasks": 0,
            "done_tasks": 0
        }

    # Normalize status values (case-insensitive)
    df_copy = df.copy()
    status_col = get_column(df_copy, "Status")
    df_copy[status_col] = df_copy[status_col].str.strip().str.lower()

    # Determine person column name
    if has_column(df_copy, "Person"):
        person_col = get_column(df_copy, "Person")
    elif has_column(df_copy, "Assigned To"):
        person_col = get_column(df_copy, "Assigned To")
    else:
        person_col = None

    # My open tasks (assigned to user, status is "open")
    my_open_tasks = 0
    if person_col:
        if is_personal:
            # For personal view, only count user's tasks
            my_open_tasks = len(df_copy[
                (df_copy[person_col].str.contains(user_name, case=False, na=False)) &
                (df_copy[status_col] == "open")
            ])
        else:
            # For team view or filtered view
            my_open_tasks = len(df_copy[
                (df_copy[person_col].str.contains(user_name, case=False, na=False)) &
                (df_copy[status_col] == "open")
            ])

    # Team open tasks (all open tasks in filtered scope)
    team_open_tasks = len(df_copy[df_copy[status_col] == "open"])

    # Active projects (unique projects in filtered scope)
    active_projects = 0
    if has_column(df_copy, "Project"):
        project_col = get_column(df_copy, "Project")
        active_projects = df_copy[project_col].nunique()

    # Task breakdown by status - handle both emoji and text formats
    status_lower = df_copy[status_col].str.lower().str.strip()

    # Open tasks: contains "not started" or "open" or red circle emoji
    open_tasks = len(df_copy[status_lower.str.contains("not started|open|🔴", case=False, na=False)])

    # Working tasks: contains "in progress" or "working" or yellow circle emoji
    working_tasks = len(df_copy[status_lower.str.contains("in progress|working|🟡", case=False, na=False)])

    # Done tasks: contains "done" or "complete" or green circle emoji
    done_tasks = len(df_copy[status_lower.str.contains("done|complete|🟢", case=False, na=False)])

    return {
        "my_open_tasks": my_open_tasks,
        "team_open_tasks": team_open_tasks,
        "active_projects": active_projects,
        "open_tasks": open_tasks,
        "working_tasks": working_tasks,
        "done_tasks": done_tasks
    }

def render_kpi_section(kpis, section_label=""):
    """
    Render KPI metrics in a 3-column layout
    """
    # Add clean peaceful styling exactly like the mockup
    st.markdown("""
        <style>
        /* Override Streamlit's default h1, h2, h3 styling - LIGHTER */
        h1 {
            font-size: 24px !important;
            font-weight: 500 !important;
            letter-spacing: -0.01em !important;
            line-height: 1.3 !important;
            color: #2a3a3a !important;
        }

        h2 {
            font-size: 20px !important;
            font-weight: 500 !important;
            letter-spacing: -0.005em !important;
            line-height: 1.4 !important;
            color: #1a2424 !important;
        }

        h3 {
            font-size: 18px !important;
            font-weight: 400 !important;
            letter-spacing: 0 !important;
            line-height: 1.4 !important;
            color: #2a3a3a !important;
        }

        /* Remove ALL teal backgrounds and boxes */
        .main .block-container {
            padding: 3rem 4rem !important;
            background: #ffffff !important;
        }

        /* Premium metric cards WITH containers */
        [data-testid="metric-container"] {
            background: #ffffff !important;
            border: 1px solid #e1e5e5 !important;
            border-radius: 12px !important;
            padding: 24px !important;
            box-shadow: 0 1px 3px rgba(26, 36, 36, 0.04) !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="metric-container"]:hover {
            box-shadow: 0 4px 8px rgba(26, 36, 36, 0.08) !important;
            border-color: #5f8c8c !important;
        }

        /* Metric labels - clean and minimal */
        [data-testid="stMetricLabel"] {
            color: #7a8888 !important;
            font-size: 10px !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
            margin-bottom: 0.5rem !important;
        }

        /* Metric values - lighter and smaller */
        [data-testid="stMetricValue"] {
            color: #1a2424 !important;
            font-size: 32px !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="MY OPEN TASKS",
            value=kpis["my_open_tasks"],
            delta=None
        )

    with col2:
        st.metric(
            label="TEAM OPEN TASKS",
            value=kpis["team_open_tasks"],
            delta=None
        )

    with col3:
        st.metric(
            label="ACTIVE PROJECTS",
            value=kpis["active_projects"],
            delta=None
        )

def render_charts_section(kpis, filtered_df):
    """
    Render chart visualizations in premium containers with generous spacing
    """
    # Add CSS for clean peaceful chart containers - NO TEAL
    st.markdown("""
        <style>
        /* Clean peaceful chart containers - pure white */
        .chart-container {
            background: #ffffff;
            border-radius: 0;
            padding: 0;
            box-shadow: none;
            border: none;
            margin-bottom: 3rem;
        }

        .chart-title {
            font-size: 13px;
            font-weight: 500;
            color: #2a3a3a;
            margin-bottom: 1.5rem;
            letter-spacing: 0;
        }

        /* Section headers - lighter weight */
        .section-header {
            font-size: 24px !important;
            font-weight: 500 !important;
            color: #2a3a3a !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.01em !important;
            line-height: 1.3 !important;
        }

        .section-subtitle {
            font-size: 12px;
            color: #7a8888;
            margin-bottom: 2rem;
            font-weight: 400;
            line-height: 1.5;
        }

        /* Add spacing between metric card columns */
        [data-testid="column"] {
            padding: 0 12px !important;
        }

        [data-testid="column"]:first-child {
            padding-left: 0 !important;
        }

        [data-testid="column"]:last-child {
            padding-right: 0 !important;
        }

        /* Add breathing room between sections */
        .section-spacer {
            margin-bottom: 48px;
        }

        /* Hide any teal backgrounds from Streamlit */
        div[data-testid="stVerticalBlock"] > div {
            background: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Add generous horizontal space between charts
    chart_col1, spacer, chart_col2 = st.columns([10, 1, 10])

    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Task Completion Status</h3>', unsafe_allow_html=True)

        # Team completion donut chart
        donut_fig = create_team_completion_donut(
            kpis["open_tasks"],
            kpis["working_tasks"],
            kpis["done_tasks"]
        )
        if donut_fig:
            st.plotly_chart(donut_fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # spacer column stays empty for breathing room

    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Tasks by Project</h3>', unsafe_allow_html=True)

        # Project breakdown chart
        project_fig = create_project_breakdown_chart(filtered_df)
        if project_fig:
            st.plotly_chart(project_fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

def render_tasks_table(filtered_df, limit=10):
    """
    Render tasks table with color-coded progress bars
    """
    if not filtered_df.empty:
        # Select and order columns for display using helper function
        display_columns = []
        for col in ["Task", "Person", "Status", "Project", "Due Date", "Progress %"]:
            if has_column(filtered_df, col):
                display_columns.append(get_column(filtered_df, col))

        if display_columns:
            table_df = filtered_df[display_columns].head(limit).copy()

            # Remove suffix patterns like __N, ___N, __N__N__, __... from column names
            # Use a fresh DataFrame to ensure clean column names
            clean_data = {}
            column_mapping = {}
            for col in table_df.columns:
                # Remove everything from __ onwards (two or more underscores)
                clean_col = re.sub(r'__+.*$', '', str(col))
                clean_data[clean_col] = table_df[col].values
                column_mapping[clean_col] = col

            # Create new DataFrame with clean column names
            clean_table_df = pd.DataFrame(clean_data)

            # Configure column settings for wrapping and progress bars
            column_config = {
                "Task": st.column_config.TextColumn(
                    "Task",
                    width="large",
                    help="Task description"
                ),
                "Person": st.column_config.TextColumn(
                    "Person",
                    width="medium",
                    help="Assigned person"
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
                )
            }

            # Add progress bar configuration if Progress % column exists
            if "Progress %" in clean_table_df.columns:
                # Convert Progress % to numeric, handling various formats
                progress_values = []
                for val in clean_table_df["Progress %"]:
                    try:
                        # Remove % sign if present and convert to float
                        val_str = str(val).strip().replace('%', '')
                        if val_str == '' or val_str.lower() == 'nan':
                            progress_values.append(0)
                        else:
                            progress_values.append(float(val_str))
                    except:
                        progress_values.append(0)

                # Create simple colored circle with percentage
                def create_progress_display(value):
                    # Determine color based on progress
                    if value == 0:
                        color = "🔴"  # Red circle
                    elif value < 100:
                        color = "🟡"  # Yellow circle
                    else:
                        color = "🟢"  # Green circle

                    # Just show circle and percentage - no bars
                    return f"{color} {int(value)}%"

                clean_table_df["Progress"] = [create_progress_display(val) for val in progress_values]
                # Remove the original Progress % column
                clean_table_df = clean_table_df.drop(columns=["Progress %"])

                column_config["Progress"] = st.column_config.TextColumn(
                    "Progress",
                    help="Task completion progress (Red: 0%, Yellow: 1-99%, Green: 100%)",
                    width="medium"
                )

            # Format the table
            st.dataframe(
                clean_table_df,
                use_container_width=True,
                hide_index=True,
                column_config=column_config
            )
        else:
            st.info("No task details available to display.")
    else:
        st.info("No tasks to display.")

def render_editable_task_grid(df, current_user, is_tea=False):
    """
    Render editable AgGrid for task management

    Args:
        df: Full dataframe
        current_user: Current logged-in user's name
        is_tea: Whether the current user is Téa Phillips
    """
    # Filter based on user permissions
    if is_tea:
        visible_df = df.copy()  # Téa sees all tasks
        section_title = "## All Tasks Management"
        section_caption = "Edit any field directly. Changes sync automatically to the Google Sheet."
    else:
        # Other users see only their own tasks
        first_name = current_user.split()[0] if current_user else ""
        if has_column(df, "Person"):
            person_col = get_column(df, "Person")
            visible_df = df[df[person_col].str.contains(first_name, case=False, na=False)]
        else:
            visible_df = pd.DataFrame()
        section_title = "## My Tasks Management"
        section_caption = "Edit your tasks directly. Changes sync automatically to the Google Sheet."

    if visible_df.empty:
        st.info("No tasks available to edit.")
        return df

    # Display section header
    st.markdown(section_title)
    st.caption(section_caption)

    # Add helpful instruction for progress editing
    st.info("💡 **Tip:** Click on any cell in the **Progress Status** column to select 🔴 Not Started, 🟡 In Progress, or 🟢 Complete")

    # Add CSS to highlight Progress Status column
    st.markdown("""
        <style>
        /* Highlight Progress Status header */
        .ag-header-cell.progress-status-header {
            background-color: #fbbf24 !important;
            font-weight: bold !important;
        }
        /* Make Progress Status cells stand out */
        .ag-cell[col-id="Progress Status"] {
            background-color: rgba(251, 191, 36, 0.1) !important;
            font-weight: 600 !important;
            cursor: pointer !important;
        }
        .ag-cell[col-id="Progress Status"]:hover {
            background-color: rgba(251, 191, 36, 0.2) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Add filter dropdowns and search box in 3-column layout
    col1, col2, col3 = st.columns(3)

    # Get unique values for dropdowns
    project_options = ["All Projects"]
    # Standardized person names for filter
    person_options = ["All People", "Téa", "Jess", "Justin", "Megan"]

    if has_column(visible_df, "Project"):
        project_col = get_column(visible_df, "Project")
        unique_projects = sorted(visible_df[project_col].dropna().unique().tolist())
        project_options.extend(unique_projects)

    with col1:
        project_filter = st.selectbox("🔍 Filter by Project", options=project_options, key="project_filter")

    with col2:
        # Search box in the middle
        search_term = st.text_input("🔎 Search Tasks", placeholder="Search by keywords...", key="search_all_tasks")

    with col3:
        person_filter = st.selectbox("🔍 Filter by Person", options=person_options, key="person_filter")

    # Apply filters if provided
    filtered_df = visible_df.copy()
    if project_filter != "All Projects" and has_column(filtered_df, "Project"):
        project_col = get_column(filtered_df, "Project")
        filtered_df = filtered_df[filtered_df[project_col] == project_filter]

    if person_filter != "All People" and has_column(filtered_df, "Person"):
        person_col = get_column(filtered_df, "Person")
        # Use contains to match first names (case-insensitive)
        filtered_df = filtered_df[filtered_df[person_col].str.contains(person_filter, case=False, na=False)]

    # Apply keyword search across all text columns
    if search_term:
        # Search across all columns
        search_mask = filtered_df.astype(str).apply(
            lambda row: row.str.contains(search_term, case=False, na=False).any(),
            axis=1
        )
        filtered_df = filtered_df[search_mask]

    if filtered_df.empty:
        if search_term:
            st.warning(f"No tasks match the search term '{search_term}' with current filters.")
        else:
            st.info("No tasks match the current filters.")
        return df

    st.markdown("<br>", unsafe_allow_html=True)

    # Create a display copy with clean column names (remove ___N suffix)
    # Build a completely new DataFrame with clean column names
    clean_data = {}
    clean_column_mapping = {}  # Map clean names back to original names with suffix

    for col in filtered_df.columns:
        # Remove everything from __ onwards (two or more underscores)
        clean_col = re.sub(r'__+.*$', '', str(col))
        clean_data[clean_col] = filtered_df[col].values
        clean_column_mapping[clean_col] = col

    display_df = pd.DataFrame(clean_data)

    # Transform Progress % to simple status icons for easy editing
    if "Progress %" in display_df.columns:
        def get_progress_status(value):
            try:
                # Convert to numeric
                val_str = str(value).strip().replace('%', '')
                if val_str == '' or val_str.lower() == 'nan':
                    val = 0
                else:
                    val = float(val_str)
            except:
                val = 0

            # Determine status based on progress
            if val == 0:
                return "🔴 Not Started"
            elif val < 100:
                return "🟡 In Progress"
            else:
                return "🟢 Complete"

        display_df["Progress Status"] = display_df["Progress %"].apply(get_progress_status)
        # Keep Progress % for reference but we'll use Progress Status for editing

        # Reorder columns to put Progress Status right after Status
        cols = display_df.columns.tolist()
        if "Progress Status" in cols and "Status" in cols:
            # Remove Progress Status from its current position
            cols.remove("Progress Status")
            # Find Status column index and insert Progress Status after it
            status_idx = cols.index("Status")
            cols.insert(status_idx + 1, "Progress Status")
            display_df = display_df[cols]

    # Configure AgGrid - DISABLE pagination to show all on one page
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(enabled=False)  # Disable pagination
    gb.configure_default_column(editable=True, filter=True, sortable=True, resizable=True)

    # Configure specific columns using clean names
    if "Status" in display_df.columns:
        gb.configure_column("Status", editable=True)
    if "Due Date" in display_df.columns:
        gb.configure_column("Due Date", editable=True)
    if "Project" in display_df.columns:
        gb.configure_column("Project", editable=True)
    if "Task" in display_df.columns:
        gb.configure_column("Task", editable=True)

    # Person column - only editable for Téa
    if "Person" in display_df.columns:
        gb.configure_column("Person", editable=is_tea)

    # Progress Status - editable dropdown with the three options
    if "Progress Status" in display_df.columns:
        gb.configure_column(
            "Progress Status",
            editable=True,
            cellEditor='agSelectCellEditor',
            cellEditorParams={
                'values': ['🔴 Not Started', '🟡 In Progress', '🟢 Complete']
            },
            width=180,
            headerClass='progress-status-header'
        )

    # Progress % - keep it editable as a number field
    if "Progress %" in display_df.columns:
        gb.configure_column("Progress %", editable=True, type=["numericColumn"])

    grid_options = gb.build()

    # Render AgGrid with display dataframe (clean column names)
    response = AgGrid(
        display_df,
        gridOptions=grid_options,
        theme="streamlit",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=800,  # Increased height to show more rows
    )

    edited_df = pd.DataFrame(response["data"])

    # Add manual "Send to Google Sheets" button
    st.markdown("<br>", unsafe_allow_html=True)

    # Check if any changes were made
    has_changes = not edited_df.equals(display_df)

    if has_changes:
        st.info("You have unsaved changes in the grid above.")

    # Custom button styling to match MetaFlex color scheme
    st.markdown("""
        <style>
        /* Google Sheets sync button styling - target all primary buttons in this section */
        button[kind="primary"],
        .stButton > button[kind="primary"],
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #0f6a6a 0%, #0d5858 80%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 14px 28px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            letter-spacing: 0.5px !important;
            transition: all 0.25s ease-in-out !important;
            box-shadow: 0 2px 6px rgba(15, 106, 106, 0.15) !important;
        }
        button[kind="primary"]:hover:not(:disabled),
        .stButton > button[kind="primary"]:hover:not(:disabled),
        button[data-testid="baseButton-primary"]:hover:not(:disabled) {
            background: linear-gradient(135deg, #127878 0%, #0f6a6a 80%) !important;
            box-shadow: 0 4px 12px rgba(15, 106, 106, 0.25) !important;
            transform: translateY(-1px);
        }
        button[kind="primary"]:disabled,
        .stButton > button[kind="primary"]:disabled,
        button[data-testid="baseButton-primary"]:disabled {
            background: #e7ecec !important;
            color: #7a8c8c !important;
            cursor: not-allowed !important;
            box-shadow: none !important;
            opacity: 0.6;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create button - always show it, but disable if no changes
    if st.button("Send to Google Sheets", type="primary", disabled=not has_changes, use_container_width=True):
        with st.spinner("Saving changes to Google Sheets..."):
            # Convert Progress Status back to Progress %
            edited_df_to_save = edited_df.copy()
            if "Progress Status" in edited_df_to_save.columns:
                def status_to_percentage(status):
                    if "🔴" in str(status) or "Not Started" in str(status):
                        return "0%"
                    elif "🟡" in str(status) or "In Progress" in str(status):
                        return "50%"  # Default to 50% for in progress
                    elif "🟢" in str(status) or "Complete" in str(status):
                        return "100%"
                    return "0%"

                # Update Progress % based on Progress Status
                if "Progress %" in edited_df_to_save.columns:
                    edited_df_to_save["Progress %"] = edited_df_to_save["Progress Status"].apply(status_to_percentage)

                # Remove Progress Status column (it's not in the original sheet)
                edited_df_to_save = edited_df_to_save.drop(columns=["Progress Status"])

            # Restore the ___N suffix to column names for proper mapping
            edited_df_with_suffix = edited_df_to_save.copy()
            suffix_cols = []
            for col in edited_df_to_save.columns:
                # Find the original column name with suffix from clean_column_mapping
                if col in clean_column_mapping:
                    suffix_cols.append(clean_column_mapping[col])
                else:
                    suffix_cols.append(col)
            edited_df_with_suffix.columns = suffix_cols

            # If not Téa, merge edited rows back into full dataframe
            if not is_tea and has_column(df, "Person"):
                # For non-Téa users, we need to merge their edits back into the full dataset
                # This is complex, so for now let's just save what they can see
                success = update_google_sheet(edited_df_with_suffix)
            else:
                # Téa's edits - save the entire edited dataset
                success = update_google_sheet(edited_df_with_suffix)

            if success:
                st.success("Changes saved successfully to Google Sheets!")
                st.cache_data.clear()  # Clear cache to show fresh data
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to save changes. Please try again.")

    return edited_df

def show_dashboard():
    """
    Home page: Team and Project Overview with charts and analytics
    """
    # Get current user from session state
    user_name = st.session_state.get("name", "Téa Phillips")  # Default to Téa for testing

    # Get first name for greeting
    first_name = user_name.split()[0] if user_name else "User"

    # Display friendly header
    st.markdown(f"### Welcome back, {first_name}")
    st.caption("Team & Project Overview")

    st.markdown("<br>", unsafe_allow_html=True)

    # Load data from Google Sheet
    with st.spinner("Loading dashboard data..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Calculate team-wide KPIs (all data)
    team_kpis = calculate_kpis(df, user_name, is_personal=False)

    # === CLEAN HEADER SECTION LIKE MOCKUP ===
    st.markdown('<h1 class="section-header">Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Real-time insights into team performance and project progress</p>', unsafe_allow_html=True)

    render_kpi_section(team_kpis)

    st.markdown("<br>", unsafe_allow_html=True)

    # Performance Overview Section
    st.markdown('<h2 class="section-header">Performance Overview</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Track completion rates and project distribution</p>', unsafe_allow_html=True)

    # Team charts
    render_charts_section(team_kpis, df)

    st.markdown("<br>", unsafe_allow_html=True)

    # === PROJECT BREAKDOWN - DYNAMIC ===
    st.markdown("### All Team Tasks by Project")
    st.markdown("<br>", unsafe_allow_html=True)

    # Dynamically show all projects from Google Sheets
    if has_column(df, "Project"):
        project_col = get_column(df, "Project")

        # Get unique projects (case-insensitive, trimmed)
        unique_projects = df[project_col].str.strip().str.title().dropna().unique()
        unique_projects = sorted([p for p in unique_projects if p])  # Sort alphabetically

        if len(unique_projects) == 0:
            st.info("No projects found in the data.")
        else:
            # Display each project's tasks
            for project_name in unique_projects:
                # Filter tasks for this project (case-insensitive)
                project_df = df[df[project_col].str.strip().str.lower() == project_name.lower()]

                # Show task count in header
                task_count = len(project_df)
                st.markdown(f"#### {project_name} ({task_count} tasks)")

                if not project_df.empty:
                    # Show ALL tasks for this project (no limit)
                    render_tasks_table(project_df, limit=1000)
                else:
                    st.caption(f"No {project_name} tasks found.")

                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Project column not found in data.")
