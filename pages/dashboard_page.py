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

def render_page_header(title, subtitle=None):
    """
    Standardized page header with teal gradient title
    Used across all pages for consistency
    """
    st.markdown(f"""
        <h1 style='
            margin: 0 0 {('8px' if subtitle else '24px')} 0;
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0a4b4b 0%, #0d6868 50%, #7a9900 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
            text-align: center;
        '>{title}</h1>
    """, unsafe_allow_html=True)

    if subtitle:
        st.markdown(f"""
            <p style='
                margin: 0 0 24px 0;
                text-align: center;
                color: #6b7280;
                font-size: 0.95rem;
            '>{subtitle}</p>
        """, unsafe_allow_html=True)

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
        
        # Use Google Sheet ID: 1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc
        sheet_id = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"

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
    SAFE MODE: Only allows updates and additions - NEVER deletes rows
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

        # Use Google Sheet ID: 1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc
        SHEET_ID = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"

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

        # SAFE MODE: Get current sheet data to prevent deletions
        current_data = ws.get_all_values()
        current_row_count = len(current_data)
        new_row_count = len(df_to_write) + 1  # +1 for header

        # Check if rows would be deleted
        if new_row_count < current_row_count:
            st.error(f"❌ Cannot save: This would delete {current_row_count - new_row_count} rows from Google Sheets. Streamlit can only UPDATE or ADD data, never delete. Please use Google Sheets directly to delete rows.")
            return False

        # Safe update: Only update existing rows and add new ones
        # Update header and all existing rows
        data_to_write = [df_to_write.columns.values.tolist()] + df_to_write.values.tolist()
        ws.update(data_to_write, 'A1')

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
    Render KPI metrics in elegant, refined cards with subtle MetaFlex branding
    """
    # Add edge spacers for more breathing room
    edge_spacer_left, col1, spacer1, col2, spacer2, col3, edge_spacer_right = st.columns([0.2, 1, 0.1, 1, 0.1, 1, 0.2])

    with col1:
        st.markdown(f"""
            <div class='kpi-card' style='
                background: linear-gradient(135deg, #fafbfc 0%, #f5f7f9 100%);
                padding: 32px 48px;
                border-radius: 12px;
                border-left: 3px solid #0a4b4b;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
                transition: all 0.2s ease;
                text-align: center;
            '>
                <p style='
                    margin: 0 0 16px 0;
                    font-size: 0.7rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    color: #6b7280;
                '>MY OPEN TASKS</p>
                <h2 style='
                    margin: 0;
                    font-size: 2.75rem;
                    font-weight: 300;
                    color: #1f2937;
                    line-height: 1;
                    letter-spacing: -0.02em;
                '>{kpis["my_open_tasks"]}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class='kpi-card' style='
                background: linear-gradient(135deg, #fafbfc 0%, #f5f7f9 100%);
                padding: 32px 48px;
                border-radius: 12px;
                border-left: 3px solid #0a4b4b;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
                transition: all 0.2s ease;
                text-align: center;
            '>
                <p style='
                    margin: 0 0 16px 0;
                    font-size: 0.7rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    color: #6b7280;
                '>TEAM OPEN TASKS</p>
                <h2 style='
                    margin: 0;
                    font-size: 2.75rem;
                    font-weight: 300;
                    color: #1f2937;
                    line-height: 1;
                    letter-spacing: -0.02em;
                '>{kpis["team_open_tasks"]}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class='kpi-card' style='
                background: linear-gradient(135deg, #fafbfc 0%, #f5f7f9 100%);
                padding: 32px 48px;
                border-radius: 12px;
                border-left: 3px solid #7a9900;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
                transition: all 0.2s ease;
                text-align: center;
            '>
                <p style='
                    margin: 0 0 16px 0;
                    font-size: 0.7rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    color: #6b7280;
                '>ACTIVE PROJECTS</p>
                <h2 style='
                    margin: 0;
                    font-size: 2.75rem;
                    font-weight: 300;
                    color: #1f2937;
                    line-height: 1;
                    letter-spacing: -0.02em;
                '>{kpis["active_projects"]}</h2>
            </div>
        """, unsafe_allow_html=True)

def render_personal_kpi_section(kpis):
    """
    Render KPI metrics for personal users with elegant light theme (only My Open Tasks and Active Projects)
    """
    # Add edge spacers and only 2 columns
    edge_spacer_left, col1, spacer1, col2, edge_spacer_right = st.columns([0.5, 1, 0.2, 1, 0.5])

    with col1:
        st.markdown(f"""
            <div class='kpi-card' style='
                background: linear-gradient(135deg, #fafbfc 0%, #f5f7f9 100%);
                padding: 32px 48px;
                border-radius: 12px;
                border-left: 3px solid #0a4b4b;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
                transition: all 0.2s ease;
                text-align: center;
            '>
                <p style='
                    margin: 0 0 16px 0;
                    font-size: 0.7rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    color: #6b7280;
                '>MY OPEN TASKS</p>
                <h2 style='
                    margin: 0;
                    font-size: 2.75rem;
                    font-weight: 300;
                    color: #1f2937;
                    line-height: 1;
                    letter-spacing: -0.02em;
                '>{kpis["my_open_tasks"]}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class='kpi-card' style='
                background: linear-gradient(135deg, #fafbfc 0%, #f5f7f9 100%);
                padding: 32px 48px;
                border-radius: 12px;
                border-left: 3px solid #7a9900;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
                transition: all 0.2s ease;
                text-align: center;
            '>
                <p style='
                    margin: 0 0 16px 0;
                    font-size: 0.7rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    color: #6b7280;
                '>ACTIVE PROJECTS</p>
                <h2 style='
                    margin: 0;
                    font-size: 2.75rem;
                    font-weight: 300;
                    color: #1f2937;
                    line-height: 1;
                    letter-spacing: -0.02em;
                '>{kpis["active_projects"]}</h2>
            </div>
        """, unsafe_allow_html=True)

def render_charts_section(kpis, filtered_df, show_project_chart=True):
    """
    Render chart visualizations with generous spacing
    (All styling now in style.css)

    Args:
        kpis: Dictionary of KPI metrics
        filtered_df: Filtered dataframe for charts
        show_project_chart: If False, only show Task Completion Status (for regular users)
    """
    # Single row - one or two columns depending on user type
    if show_project_chart:
        chart_col1, chart_col2 = st.columns([1, 1])
    else:
        # For regular users, just show one centered chart
        chart_col1 = st.container()

    with chart_col1:
        # Use Streamlit container to keep everything together
        container1 = st.container()
        with container1:
            st.markdown("""
                <style>
                /* Target this specific column */
                div[data-testid="column"]:nth-child(1) div[data-testid="stVerticalBlock"] {
                    background: linear-gradient(135deg, #f5faf2 0%, #f8fbf8 100%) !important;
                    border-radius: 12px !important;
                    padding: 24px !important;
                    border: 1px solid rgba(10, 75, 75, 0.1) !important;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                }
                div[data-testid="column"]:nth-child(1) div[data-testid="stVerticalBlock"]:hover {
                    transform: translateY(-4px) !important;
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.04) !important;
                    border: 1px solid rgba(10, 75, 75, 0.2) !important;
                }
                </style>
                <h3 style="text-align: left; margin: 0 0 20px 0; color: #0a4b4b; font-weight: 500; font-size: 1.0rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">Task Completion Status</h3>
            """, unsafe_allow_html=True)

            # Create vertical bar chart for task completion
            import plotly.graph_objects as go

            statuses = ['Open', 'In Progress', 'Complete']
            counts = [kpis["open_tasks"], kpis["working_tasks"], kpis["done_tasks"]]
            colors = ['#d17a6f', '#e8b968', '#4d7a40']

            # Calculate percentages
            total = sum(counts)
            percentages = [(count / total * 100) if total > 0 else 0 for count in counts]

            # Create text labels with both count and percentage
            text_labels = [f'{count}<br>({pct:.0f}%)' for count, pct in zip(counts, percentages)]

            fig = go.Figure(data=[
                go.Bar(
                    x=statuses,
                    y=counts,
                    marker=dict(
                        color=colors,
                        line=dict(color='#ffffff', width=2)
                    ),
                    text=text_labels,
                    textposition='outside',
                    textfont=dict(size=14, color='#0a4b4b', family='-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Count: %{y} (%{customdata:.0f}%)<extra></extra>',
                    customdata=percentages
                )
            ])

            fig.update_layout(
                showlegend=False,
                height=380,
                margin=dict(l=20, r=20, t=50, b=60),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    title=None,
                    tickfont=dict(size=13, color='#0a4b4b', family='-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#f3f4f6',
                    title=None,
                    tickfont=dict(size=12, color='#0a4b4b', family='-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'),
                    range=[0, max(counts) * 1.2]  # Add 20% padding to prevent cutoff
                )
            )

            st.plotly_chart(fig, use_container_width=True)

    # Only show "Tasks by Project" chart for Tea and Jess
    if show_project_chart:
        with chart_col2:
            # Use Streamlit container to keep everything together
            container2 = st.container()
            with container2:
                st.markdown("""
                    <style>
                    /* Target this specific column */
                    div[data-testid="column"]:nth-child(2) div[data-testid="stVerticalBlock"] {
                        background: linear-gradient(135deg, #f5faf2 0%, #f8fbf8 100%) !important;
                        border-radius: 12px !important;
                        padding: 24px !important;
                        border: 1px solid rgba(10, 75, 75, 0.1) !important;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    }
                    div[data-testid="column"]:nth-child(2) div[data-testid="stVerticalBlock"]:hover {
                        transform: translateY(-4px) !important;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.04) !important;
                        border: 1px solid rgba(10, 75, 75, 0.2) !important;
                    }
                    </style>
                    <h3 style="text-align: left; margin: 0 0 20px 0; color: #0a4b4b; font-weight: 500; font-size: 1.0rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">Tasks by Project</h3>
                """, unsafe_allow_html=True)

                project_fig = create_project_breakdown_chart(filtered_df)
                if project_fig:
                    st.plotly_chart(project_fig, use_container_width=True, config={
                        'displayModeBar': True,
                        'modeBarButtonsToAdd': ['toImage'],
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'project_breakdown_chart',
                            'height': 500,
                            'width': 700,
                            'scale': 2
                        }
                    })

def render_tasks_table(filtered_df, limit=10, hide_project_column=False, show_transcript_checked=False):
    """
    Render tasks table with color-coded progress bars

    Args:
        filtered_df: DataFrame to display
        limit: Maximum number of rows to show
        hide_project_column: If True, don't show the Project column (for project-specific views)
        show_transcript_checked: If True, show the Transcript ID column
    """
    if not filtered_df.empty:
        # Select and order columns for display using helper function
        display_columns = []

        # Only add Transcript ID column if "Show Transcript" is checked (passed from parent)
        transcript_col_found = False
        if show_transcript_checked:
            for transcript_name in ["Transcript ID", "Transcript Number", "Transcript #", "ID", "Transcript"]:
                if has_column(filtered_df, transcript_name):
                    display_columns.append(get_column(filtered_df, transcript_name))
                    transcript_col_found = True
                    break

        # Add other columns (including Date Assigned, Notes, excluding Project if hide_project_column is True)
        # Note: We'll combine Status and Progress % into a single column, so we'll handle them separately
        columns_to_add = ["Task", "Person", "Status", "Progress %", "Date Assigned", "Due Date", "Notes"]
        if not hide_project_column:
            columns_to_add.insert(3, "Project")  # Add Project after Status

        for col in columns_to_add:
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
                "Transcript ID": st.column_config.TextColumn(
                    "Transcript ID",
                    width="small",
                    help="Transcript number"
                ),
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
                "Date Assigned": st.column_config.TextColumn(
                    "Date Assigned",
                    width="small",
                    help="Date task was assigned"
                ),
                "Due Date": st.column_config.TextColumn(
                    "Due Date",
                    width="small"
                ),
                "Notes": st.column_config.TextColumn(
                    "Notes",
                    width="large",
                    help="Additional notes or comments"
                )
            }

            # Combine Status and Progress % into a single column with dropdown selector
            if "Status" in clean_table_df.columns and "Progress %" in clean_table_df.columns:
                # Normalize status values to match dropdown options
                def normalize_status(status):
                    status_str = str(status).strip().lower()

                    # Map various status values to our three standard options
                    if any(word in status_str for word in ['open', 'not started', 'to do', 'todo']):
                        return "🟥 Open"
                    elif any(word in status_str for word in ['working', 'in progress', 'started', 'ongoing']):
                        return "🟨 In Progress"
                    elif any(word in status_str for word in ['done', 'complete', 'finished', 'closed']):
                        return "🟩 Done"
                    else:
                        # Default to Open if status is unrecognized
                        return "🟥 Open"

                # Apply normalization to Status column
                clean_table_df["Status"] = clean_table_df["Status"].apply(normalize_status)

                # Remove the Progress % column as it's now combined with Status
                clean_table_df = clean_table_df.drop(columns=["Progress %"])

                # Configure Status as a dropdown with the three color-coded options
                column_config["Status"] = st.column_config.SelectboxColumn(
                    "Status",
                    help="Task status (🟥 Open, 🟨 In Progress, 🟩 Done)",
                    width="medium",
                    options=["🟥 Open", "🟨 In Progress", "🟩 Done"],
                    required=True
                )
            elif "Progress %" in clean_table_df.columns:
                # Fallback: If only Progress % exists (no Status column)
                progress_values = []
                for val in clean_table_df["Progress %"]:
                    try:
                        val_str = str(val).strip().replace('%', '')
                        if val_str == '' or val_str.lower() == 'nan':
                            progress_values.append(0)
                        else:
                            progress_values.append(float(val_str))
                    except:
                        progress_values.append(0)

                def create_progress_display(value):
                    if value == 0:
                        return f"🔴 {int(value)}%"
                    elif value < 100:
                        return f"🟡 {int(value)}%"
                    else:
                        return f"🟢 {int(value)}%"

                clean_table_df["Progress"] = [create_progress_display(val) for val in progress_values]
                clean_table_df = clean_table_df.drop(columns=["Progress %"])

                column_config["Progress"] = st.column_config.TextColumn(
                    "Progress",
                    help="Task completion progress",
                    width="medium"
                )

            # Add 2px teal accent line above table
            st.markdown("""
                <div style="height: 2px; background: linear-gradient(90deg, #0a4b4b 0%, #14b8a6 100%); border-radius: 2px; margin-bottom: 0;"></div>
            """, unsafe_allow_html=True)

            # Add MetaFlex premium light theme styling for tables (both dataframe and data_editor)
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
                    border-radius: 8px !important;
                    padding: 0 !important;
                    border: 1px solid #e8eaed !important;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
                    overflow: hidden !important;
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
                    border-top: none !important;
                    padding: 16px 12px !important;
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
                    background: rgba(10, 75, 75, 0.02) !important;
                    background-color: rgba(10, 75, 75, 0.02) !important;
                    transition: all 0.2s ease !important;
                }

                /* Cell styling - dark gray text on light background */
                div[data-testid="stDataFrame"] tbody tr td,
                div[data-testid="stDataFrame"] td,
                [data-testid="stDataFrame"] tbody tr td,
                tbody tr td,
                td {
                    border-bottom: 1px solid #f3f4f6 !important;
                    border-left: none !important;
                    border-right: none !important;
                    padding: 14px 12px !important;
                    color: #2d3748 !important;
                }

                /* Scrollbar styling for light theme */
                /* Translucent dark MetaFlex teal scrollbars for tables */
                div[data-testid="stDataFrame"] ::-webkit-scrollbar,
                div[data-testid="data-editor"] ::-webkit-scrollbar {
                    width: 8px !important;
                    height: 8px !important;
                }

                div[data-testid="stDataFrame"] ::-webkit-scrollbar-track,
                div[data-testid="data-editor"] ::-webkit-scrollbar-track {
                    background: rgba(10, 75, 75, 0.08) !important;
                    border-radius: 4px !important;
                }

                div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb,
                div[data-testid="data-editor"] ::-webkit-scrollbar-thumb {
                    background: rgba(10, 75, 75, 0.4) !important;
                    border-radius: 4px !important;
                }

                div[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb:hover,
                div[data-testid="data-editor"] ::-webkit-scrollbar-thumb:hover {
                    background: rgba(10, 75, 75, 0.6) !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Editable data table
            edited_df = st.data_editor(
                clean_table_df,
                use_container_width=True,
                hide_index=True,
                column_config=column_config,
                num_rows="fixed",
                key=f"project_table_{hash(str(filtered_df.iloc[0].to_dict()) if len(filtered_df) > 0 else 'empty')}"
            )

            # Custom button styling - soft grey with dark teal text, rounded corners, translucent
            st.markdown("""
                <style>
                /* Target all Streamlit buttons more aggressively */
                div[data-testid="column"] button,
                div[data-testid="column"] button[kind="primary"],
                div[data-testid="column"] button[kind="secondary"],
                .stButton > button,
                .stDownloadButton > button {
                    background: rgba(229, 231, 235, 0.7) !important;
                    color: #0a4b4b !important;
                    border: 1px solid rgba(10, 75, 75, 0.2) !important;
                    border-radius: 12px !important;
                    font-weight: 500 !important;
                    transition: all 0.2s ease !important;
                }

                div[data-testid="column"] button:hover,
                div[data-testid="column"] button[kind="primary"]:hover,
                div[data-testid="column"] button[kind="secondary"]:hover,
                .stButton > button:hover,
                .stDownloadButton > button:hover {
                    background: rgba(229, 231, 235, 0.9) !important;
                    border: 1px solid rgba(10, 75, 75, 0.4) !important;
                    box-shadow: 0 2px 8px rgba(10, 75, 75, 0.15) !important;
                }
                </style>
            """, unsafe_allow_html=True)

            # Save and Export buttons - Centered
            _, save_col, export_col, _ = st.columns([1.5, 1, 1, 1.5])
            with save_col:
                if st.button("Save to Sheets", key=f"save_btn_{hash(str(filtered_df.iloc[0].to_dict()) if len(filtered_df) > 0 else 'empty')}", type="primary", use_container_width=True):
                    # Map edited data back to original DataFrame structure
                    # We need to reverse the cleaning process and update the original df
                    with st.spinner("Syncing to Google Sheets..."):
                        try:
                            # Update the original dataframe with edited values
                            for clean_col, orig_col in column_mapping.items():
                                if clean_col in edited_df.columns:
                                    # Find matching rows in filtered_df and update
                                    for idx in filtered_df.head(limit).index:
                                        row_num = list(filtered_df.head(limit).index).index(idx)
                                        if row_num < len(edited_df):
                                            value = edited_df.iloc[row_num][clean_col]

                                            # Special handling for Status column: strip emoji prefix
                                            if clean_col == "Status" and isinstance(value, str):
                                                # Remove emoji prefix (e.g., "🟥 Open" → "Open")
                                                value = value.replace("🟥 ", "").replace("🟨 ", "").replace("🟩 ", "").strip()

                                            filtered_df.loc[idx, orig_col] = value

                            # Call update function (you'll need to pass the full df and update it)
                            success = update_google_sheet(filtered_df)
                            if success:
                                st.success("✅ Changes saved to Google Sheets successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save changes. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error saving: {str(e)}")

            with export_col:
                # Convert dataframe to CSV for download
                csv = edited_df.to_csv(index=False).encode('utf-8')

                # Try to extract project name from the dataframe if it exists
                try:
                    if has_column(filtered_df, "Project") and len(filtered_df) > 0:
                        first_project = str(get_column_value(filtered_df.iloc[0], "Project", ""))
                        filename = f"project_tasks_{first_project.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
                    else:
                        filename = f"project_tasks_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
                except:
                    filename = f"project_tasks_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"

                if st.download_button(
                    label="Export CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    key=f"export_btn_{hash(str(filtered_df.iloc[0].to_dict()) if len(filtered_df) > 0 else 'empty')}",
                    use_container_width=True
                ):
                    pass  # Download button handles the download automatically
        else:
            st.info("No task details available to display.")
    else:
        st.info("No tasks to display.")

def render_editable_task_grid(df, current_user, is_tea=False, key_prefix="", show_title=True):
    """
    Render editable AgGrid for task management

    Args:
        df: Full dataframe
        current_user: Current logged-in user's name
        is_tea: Whether the current user is Téa Phillips
        key_prefix: Unique prefix for widget keys to avoid duplicates
        show_title: Whether to display the section title and caption
    """
    # Filter based on user permissions
    if is_tea:
        visible_df = df.copy()  # Téa sees all tasks
        section_title = "## All Task Management"
        section_caption = "Edit any field directly. Then commit to Google Sheets by pressing the button 'Send to Google Sheets'."
    else:
        # Other users see only their own tasks
        first_name = current_user.split()[0] if current_user else ""
        if has_column(df, "Person"):
            person_col = get_column(df, "Person")
            visible_df = df[df[person_col].str.contains(first_name, case=False, na=False)]
        else:
            visible_df = pd.DataFrame()
        section_title = "## My Tasks Management"
        section_caption = "Edit any field directly. Then commit to Google Sheets by pressing the button 'Send to Google Sheets'."

    if visible_df.empty:
        st.info("No tasks available to edit.")
        return df

    # Display section header only if show_title is True
    if show_title:
        st.markdown(section_title)
        if section_caption:
            st.caption(section_caption)

    if visible_df.empty:
        st.info("No tasks to display.")
        return df

    st.markdown("<br>", unsafe_allow_html=True)

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

    # Only show filters for "All Task Management" (when key_prefix is empty)
    filtered_df = visible_df.copy()

    if key_prefix == "":
        # NOTE: Archive filtering is now handled in all_tasks_page.py
        # Removed duplicate checkbox to avoid double checkboxes
        st.markdown("<br>", unsafe_allow_html=True)

        # Add filter dropdowns and search box in 3-column layout
        col1, col2, col3 = st.columns([2, 2, 1])

        # Build project filter options
        project_options = ["All Projects"]

        if has_column(filtered_df, "Project"):
            project_col = get_column(filtered_df, "Project")
            unique_projects = sorted(filtered_df[project_col].dropna().unique().tolist())
            project_options.extend(unique_projects)

        with col1:
            project_filter = st.selectbox("🔍 Filter by Project", options=project_options, key=f"{key_prefix}_project_filter")

        with col2:
            search_term = st.text_input("🔎 Search Tasks", placeholder="Search by keywords...", key=f"{key_prefix}_search_tasks")

        with col3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            clear_filters = st.button("Clear Filters", key=f"{key_prefix}_clear_filters")

        # Handle clear filters
        if clear_filters:
            st.session_state[f"{key_prefix}_project_filter"] = "All Projects"
            st.session_state[f"{key_prefix}_search_tasks"] = ""
            st.rerun()

        # Check if filters are active
        filters_active = project_filter != "All Projects" or (search_term and search_term.strip() != "")

        # Apply filters
        if project_filter != "All Projects" and has_column(filtered_df, "Project"):
            project_col = get_column(filtered_df, "Project")
            filtered_df = filtered_df[filtered_df[project_col] == project_filter]

        # Apply keyword search
        if search_term:
            search_mask = filtered_df.astype(str).apply(
                lambda row: row.str.contains(search_term, case=False, na=False).any(),
                axis=1
            )
            filtered_df = filtered_df[search_mask]

        # Show filter indicator if filters are active
        if filters_active:
            active_filters = []
            if project_filter != "All Projects":
                active_filters.append(f"Project: {project_filter}")
            if search_term and search_term.strip() != "":
                active_filters.append(f"Search: '{search_term}'")

            filter_text = " • ".join(active_filters)
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
                    border-left: 4px solid #0a4b4b;
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin: 16px 0;
                    font-size: 0.9rem;
                    color: #0a4b4b;
                    font-weight: 600;
                    box-shadow: 0 2px 4px rgba(10, 75, 75, 0.1);
                '>
                    🔍 Active Filters: {filter_text} • Showing {len(filtered_df)} of {len(visible_df)} tasks
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    if filtered_df.empty:
        st.info("No tasks to display with current filters.")
        return df

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
                return "🟠 Not Started"
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

    # Add unique row IDs for proper AG-Grid tracking
    display_df = display_df.reset_index(drop=False)
    display_df = display_df.rename(columns={'index': '_row_id'})

    # Configure AgGrid - DISABLE pagination to show all on one page
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_pagination(enabled=False)  # Disable pagination
    gb.configure_default_column(editable=True, filter=True, sortable=True, resizable=True)

    # Hide the internal row ID column
    gb.configure_column("_row_id", hide=True)

    # Configure specific columns using clean names
    if "Status" in display_df.columns:
        gb.configure_column("Status", hide=True)  # Hidden in home view
    if "Due Date" in display_df.columns:
        gb.configure_column("Due Date", editable=True)
    if "Project" in display_df.columns:
        gb.configure_column("Project", hide=True)  # Hide since project name is in heading
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
                'values': ['🟠 Not Started', '🟡 In Progress', '🟢 Complete']
            },
            width=180,
            headerClass='progress-status-header'
        )

    # Progress % - hide in home view (still used for data syncing)
    if "Progress %" in display_df.columns:
        gb.configure_column("Progress %", hide=True)

    # Set getRowId using GridOptionsBuilder to avoid unsafe JavaScript
    gb.configure_grid_options(getRowNodeId='_row_id')

    grid_options = gb.build()

    # Render AgGrid with display dataframe (clean column names)
    response = AgGrid(
        display_df,
        gridOptions=grid_options,
        theme="streamlit",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=False,  # Security: Disable unsafe JavaScript code execution
        fit_columns_on_grid_load=True,
        height=800,  # Increased height to show more rows
    )

    edited_df = pd.DataFrame(response["data"])

    # Remove internal row ID column if present
    if "_row_id" in edited_df.columns:
        edited_df = edited_df.drop(columns=["_row_id"])

    # Add manual "Send to Google Sheets" button
    st.markdown("<br>", unsafe_allow_html=True)

    # Check if any changes were made (compare without _row_id column)
    display_df_compare = display_df.drop(columns=["_row_id"]) if "_row_id" in display_df.columns else display_df
    has_changes = not edited_df.equals(display_df_compare)

    if has_changes:
        st.info("You have unsaved changes in the grid above.")

    # No custom CSS needed - all styling handled by metaflex_premium.css

    # Create single "Send to Google Sheets" button
    if st.button("Send to Google Sheets", type="primary", disabled=not has_changes, width='stretch', key=f"{key_prefix}_save_button"):
        # Check for completed tasks that will be auto-archived
        completed_tasks_count = 0
        if "Progress Status" in edited_df.columns:
            completed_mask = edited_df["Progress Status"].str.contains("🟢|Complete", case=False, na=False)
            completed_tasks_count = completed_mask.sum()
        with st.spinner("Saving changes to Google Sheets..."):
            # Convert Progress Status back to Progress %
            edited_df_to_save = edited_df.copy()
            if "Progress Status" in edited_df_to_save.columns:
                def status_to_percentage(status):
                    if "🟠" in str(status) or "🔴" in str(status) or "Not Started" in str(status):
                        return "0%"
                    elif "🟡" in str(status) or "In Progress" in str(status):
                        return "50%"  # Default to 50% for in progress
                    elif "🟢" in str(status) or "Complete" in str(status):
                        return "100%"
                    return "0%"

                # Update Progress % based on Progress Status
                if "Progress %" in edited_df_to_save.columns:
                    edited_df_to_save["Progress %"] = edited_df_to_save["Progress Status"].apply(status_to_percentage)

                # AUTO-ARCHIVE: Set Status to "Done" for all completed tasks
                if "Status" in edited_df_to_save.columns:
                    completed_mask = edited_df_to_save["Progress Status"].str.contains("🟢|Complete", case=False, na=False)
                    edited_df_to_save.loc[completed_mask, "Status"] = "Done"

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
                if completed_tasks_count > 0:
                    st.success(f"✅ Changes saved! {completed_tasks_count} completed task(s) automatically archived.")
                else:
                    st.success("✅ Changes saved successfully to Google Sheets!")
                st.cache_data.clear()  # Clear cache to show fresh data
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to save changes. Please try again.")

    return edited_df

def calculate_executive_metrics(df):
    """
    Calculate executive-level metrics for Tea's admin view
    Returns detailed project breakdown and team metrics
    """
    if df.empty:
        return {
            "total_tasks": 0,
            "total_open": 0,
            "total_in_progress": 0,
            "total_complete": 0,
            "completion_rate": 0,
            "tasks_by_project": {},
            "tasks_by_person": {},
            "overdue_tasks": 0
        }

    df_copy = df.copy()

    # Normalize status
    if has_column(df_copy, "Status"):
        status_col = get_column(df_copy, "Status")
        df_copy[status_col] = df_copy[status_col].str.strip().str.lower()
    else:
        return {}

    # Count status
    status_lower = df_copy[status_col]
    total_open = len(df_copy[status_lower.str.contains("not started|open|🔴", case=False, na=False)])
    total_in_progress = len(df_copy[status_lower.str.contains("in progress|working|🟡", case=False, na=False)])
    total_complete = len(df_copy[status_lower.str.contains("done|complete|🟢", case=False, na=False)])
    total_tasks = len(df_copy)

    # Completion rate
    completion_rate = round((total_complete / total_tasks * 100) if total_tasks > 0 else 0, 1)

    # Tasks by project
    tasks_by_project = {}
    if has_column(df_copy, "Project"):
        project_col = get_column(df_copy, "Project")
        for project in df_copy[project_col].dropna().unique():
            project_df = df_copy[df_copy[project_col] == project]
            project_status = project_df[status_col]
            tasks_by_project[project] = {
                "total": len(project_df),
                "open": len(project_df[project_status.str.contains("not started|open|🔴", case=False, na=False)]),
                "in_progress": len(project_df[project_status.str.contains("in progress|working|🟡", case=False, na=False)]),
                "complete": len(project_df[project_status.str.contains("done|complete|🟢", case=False, na=False)])
            }

    # Tasks by person
    tasks_by_person = {}
    person_col = None
    if has_column(df_copy, "Person"):
        person_col = get_column(df_copy, "Person")
    elif has_column(df_copy, "Assigned To"):
        person_col = get_column(df_copy, "Assigned To")

    if person_col:
        # Normalize person names to title case for consistent grouping
        # Also filter out empty/null values
        df_copy['_normalized_person'] = df_copy[person_col].fillna('').str.strip().str.title()
        df_copy = df_copy[df_copy['_normalized_person'] != '']  # Remove empty names

        for person in sorted(df_copy['_normalized_person'].unique()):
            if person:  # Skip empty strings
                person_df = df_copy[df_copy['_normalized_person'] == person]
                person_status = person_df[status_col]
                tasks_by_person[person] = {
                    "total": len(person_df),
                    "open": len(person_df[person_status.str.contains("not started|open|🔴", case=False, na=False)]),
                    "in_progress": len(person_df[person_status.str.contains("in progress|working|🟡", case=False, na=False)]),
                    "complete": len(person_df[person_status.str.contains("done|complete|🟢", case=False, na=False)])
                }

    # Overdue tasks
    overdue_tasks = 0
    if has_column(df_copy, "Due Date"):
        from datetime import datetime
        due_date_col = get_column(df_copy, "Due Date")
        today = datetime.now()

        for idx, row in df_copy.iterrows():
            try:
                if pd.notna(row[due_date_col]):
                    due_date = pd.to_datetime(row[due_date_col])
                    if due_date < today and row[status_col] not in ["done", "complete", "completed"]:
                        overdue_tasks += 1
            except:
                pass

    return {
        "total_tasks": total_tasks,
        "total_open": total_open,
        "total_in_progress": total_in_progress,
        "total_complete": total_complete,
        "completion_rate": completion_rate,
        "tasks_by_project": tasks_by_project,
        "tasks_by_person": tasks_by_person,
        "overdue_tasks": overdue_tasks
    }


def render_executive_dashboard(exec_metrics, df):
    """
    Render executive dashboard for Tea with enhanced metrics
    """
    # Add KPI card hover effects
    st.markdown("""
        <style>
        .kpi-card {
            background: #ffffff;
            padding: 48px 32px;
            border-radius: 12px;
            border: 1px solid #e8eaed;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: default;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-color: #d1d5db;
        }
        </style>
        <h2 style='
            margin: 0 0 48px 0;
            font-size: 1.5rem;
            font-weight: 400;
            color: #2d3748;
            letter-spacing: 0.02em;
        '>Executive Overview</h2>
    """, unsafe_allow_html=True)

    # Top row: 4 key metrics - Luxury minimal style with ample spacing
    col1, sp1, col2, sp2, col3, sp3, col4 = st.columns([1, 0.15, 1, 0.15, 1, 0.15, 1])

    with col1:
        st.markdown(f"""
            <div class='kpi-card'>
                <p style='margin: 0 0 20px 0; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #9ca3af;'>Open Tasks</p>
                <h2 style='margin: 0; font-size: 2.75rem; font-weight: 300; color: #1f2937; line-height: 1; letter-spacing: -0.02em;'>{exec_metrics["total_open"]}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class='kpi-card'>
                <p style='margin: 0 0 20px 0; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #9ca3af;'>In Progress</p>
                <h2 style='margin: 0; font-size: 2.75rem; font-weight: 300; color: #1f2937; line-height: 1; letter-spacing: -0.02em;'>{exec_metrics["total_in_progress"]}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class='kpi-card'>
                <p style='margin: 0 0 20px 0; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #9ca3af;'>Complete</p>
                <h2 style='margin: 0; font-size: 2.75rem; font-weight: 300; color: #1f2937; line-height: 1; letter-spacing: -0.02em;'>{exec_metrics["total_complete"]}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class='kpi-card'>
                <p style='margin: 0 0 20px 0; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #9ca3af;'>Completion Rate</p>
                <h2 style='margin: 0; font-size: 2.75rem; font-weight: 300; color: #1f2937; line-height: 1; letter-spacing: -0.02em;'>{exec_metrics["completion_rate"]}%</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin: 80px 0;'></div>", unsafe_allow_html=True)

    # Second row: Project and Person breakdowns side by side
    # Charts removed from Overview - now distributed across other pages
    # - Task Age Analysis -> My Tasks page
    # - Completion Velocity & Project Health -> All Tasks page

    # Import the chart functions
    from charts import (
        create_project_tasks_overview_chart,
        create_task_age_analysis,
        create_task_completion_velocity,
        create_project_health_dashboard
    )

    # Charts moved to other pages for better organization:
    # - Task Age Analysis -> My Tasks page
    # - Completion Velocity & Project Health -> All Tasks page


def show_dashboard():
    """
    Home page: Team and Project Overview with charts and analytics
    """
    # Get current user from session state
    user_name = st.session_state.get("name")

    # If user_name is None, user is not authenticated - redirect to login
    if not user_name:
        st.warning("Please log in to view the dashboard.")
        st.stop()

    # Load data from Google Sheet
    with st.spinner("Loading dashboard data..."):
        df = load_google_sheet()

    if df.empty:
        st.warning("No data available. Please check your Google Sheet connection.")
        return

    # Determine if user is Tea (admin), Jess (view_all_tasks), or regular user
    # Handle various spellings: Tea, Téa, Tēa, tea phillips, etc.
    user_lower = user_name.lower()
    is_tea = "tea" in user_lower or "téa" in user_lower or "tēa" in user_lower
    is_jess = "jess" in user_lower


    # Filter data based on user type
    if is_tea:
        # Tea sees all data with team KPIs
        filtered_df = df
        kpis = calculate_kpis(filtered_df, user_name, is_personal=False)
        exec_metrics = calculate_executive_metrics(df)
    elif is_jess:
        # Jess sees only her, Megan's, and Justin's tasks
        assignee_col = None
        if has_column(df, "Assigned To"):
            assignee_col = get_column(df, "Assigned To")
        elif has_column(df, "assignee"):
            assignee_col = get_column(df, "assignee")
        elif has_column(df, "Person"):
            assignee_col = get_column(df, "Person")

        if assignee_col:
            # Filter for Jess, Megan, and Justin
            filtered_df = df[
                df[assignee_col].str.lower().str.contains('jess|megan|justin', na=False, regex=True)
            ].copy()
        else:
            filtered_df = df
        kpis = calculate_kpis(filtered_df, user_name, is_personal=False)
    else:
        # Other users only see their own tasks
        # Try different possible column names for assignee
        assignee_col = None
        if has_column(df, "Assigned To"):
            assignee_col = get_column(df, "Assigned To")
        elif has_column(df, "assignee"):
            assignee_col = get_column(df, "assignee")
        elif has_column(df, "Person"):
            assignee_col = get_column(df, "Person")

        if assignee_col:
            filtered_df = df[df[assignee_col].str.lower().str.contains(user_name.lower(), na=False)].copy()
        else:
            st.error(f"Cannot filter tasks: No assignee column found. Available columns: {', '.join(df.columns.tolist())}")
            return
        kpis = calculate_kpis(filtered_df, user_name, is_personal=True)

    # Render KPIs based on user type
    if is_tea:
        # Tea sees enhanced executive dashboard only (no duplicate basic KPIs)
        render_executive_dashboard(exec_metrics, df)
    elif is_jess:
        # Jess sees all 3 KPI cards
        render_kpi_section(kpis)
    else:
        # Other users see only 2 KPI cards (My Open Tasks, Active Projects)
        render_personal_kpi_section(kpis)

    # Section: Performance Overview
    st.markdown("<div style='margin-top: 48px;'></div>", unsafe_allow_html=True)

    # Charts (filtered based on user)
    # Only Tea and Jess see the "Tasks by Project" chart; regular users only see Task Completion Status
    render_charts_section(kpis, filtered_df, show_project_chart=(is_tea or is_jess))

    # === PROJECT BREAKDOWN === (Only show for Tea and Jess)
    if is_tea or is_jess:
        st.markdown("<div style='margin-top: 64px;'></div>", unsafe_allow_html=True)

        st.markdown("""
            <h2 style='
                margin: 0 0 32px 0;
                font-size: 2rem;
                font-weight: 700;
                color: #2d3748;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            '>BREAKDOWN OF TASKS BY PROJECT</h2>
        """, unsafe_allow_html=True)

        # Add archive filter with calm styling
        show_archived_projects = st.checkbox("Include archived", value=False, key="show_archived_projects")

        # Add "Show Transcript #" checkbox right below
        show_transcript_global = st.checkbox("Show Transcript #", value=False, key="show_transcript_global")

        # Style checkboxes with calm, subdued dark teal - minimal interference
        st.markdown("""
            <style>
            /* Style checkbox label text - calm and subdued */
            div[data-testid="stCheckbox"] label p {
                color: #5a6c7d !important;
                font-size: 0.9rem !important;
                font-weight: 400 !important;
            }

            /* Unchecked checkbox - soft grey with subtle teal border */
            div[data-testid="stCheckbox"] input[type="checkbox"] ~ span div svg rect {
                fill: rgba(229, 231, 235, 0.5) !important;
                stroke: rgba(10, 75, 75, 0.3) !important;
                stroke-width: 1.5 !important;
            }

            /* Checked checkbox - calm dark teal */
            div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ span div svg rect {
                fill: #0a4b4b !important;
                stroke: #0a4b4b !important;
            }

            /* Make checkmark white when checked */
            div[data-testid="stCheckbox"] input[type="checkbox"]:checked ~ span div svg path {
                fill: #ffffff !important;
                stroke: #ffffff !important;
                stroke-width: 2 !important;
            }

            /* Hover effect - subtle */
            div[data-testid="stCheckbox"]:hover input[type="checkbox"] ~ span div svg rect {
                stroke: rgba(10, 75, 75, 0.5) !important;
            }

            div[data-testid="stCheckbox"]:hover input[type="checkbox"]:checked ~ span div svg rect {
                fill: #0d5a5a !important;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)

        # Apply archive filter to dataframe
        # Use filtered_df for Jess (already filtered to Jess/Megan/Justin), full df for Tea
        projects_df = filtered_df.copy() if is_jess else df.copy()
        if not show_archived_projects and has_column(projects_df, "Status"):
            status_col = get_column(projects_df, "Status")
            projects_df = projects_df[~projects_df[status_col].str.strip().str.lower().isin(['done', 'complete', 'completed'])]

        # Dynamically show all projects from Google Sheets with editable grids
        if has_column(projects_df, "Project"):
            project_col = get_column(projects_df, "Project")

            # Get unique projects (case-insensitive, trimmed)
            unique_projects = projects_df[project_col].str.strip().str.title().dropna().unique()
            unique_projects = sorted([p for p in unique_projects if p])  # Sort alphabetically

            if len(unique_projects) > 0:
                # Display each project's tasks with editable grids
                for idx, project_name in enumerate(unique_projects):
                    # Filter tasks for this project (case-insensitive)
                    project_df = projects_df[projects_df[project_col].str.strip().str.lower() == project_name.lower()].copy()

                    # Calculate project KPIs
                    task_count = len(project_df)
                    open_count = 0
                    in_progress_count = 0
                    complete_count = 0

                    if has_column(project_df, "Status"):
                        status_col = get_column(project_df, "Status")
                        open_count = len(project_df[project_df[status_col].str.lower().str.contains("open|not started", case=False, na=False)])
                        in_progress_count = len(project_df[project_df[status_col].str.lower().str.contains("in progress|working", case=False, na=False)])
                        complete_count = len(project_df[project_df[status_col].str.lower().str.contains("done|complete", case=False, na=False)])

                    completion_rate = int((complete_count / task_count * 100)) if task_count > 0 else 0

                    # Project header - Subdued styling
                    st.markdown(f"""<h3 style='
                        text-align: left;
                        font-size: 1.1rem;
                        font-weight: 500;
                        color: #6b7280;
                        margin: 24px 0 16px 0;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    '>{project_name}</h3>""", unsafe_allow_html=True)

                    # Premium KPI cards using Streamlit columns
                    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

                    with kpi_col1:
                        st.markdown(f"""<div style='
                            background: #ffffff;
                            border-radius: 10px;
                            padding: 20px 16px;
                            border: 1px solid #e8eaed;
                            border-left: 2px solid #0a4b4b;
                            text-align: center;
                            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
                        '>
                            <p style='margin: 0 0 8px 0; font-size: 0.65rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: #9ca3af;'>TOTAL</p>
                            <h3 style='margin: 0; font-size: 1.6rem; font-weight: 400; color: #2d3748;'>{task_count}</h3>
                        </div>""", unsafe_allow_html=True)

                    with kpi_col2:
                        st.markdown(f"""<div style='
                            background: #ffffff;
                            border-radius: 10px;
                            padding: 20px 16px;
                            border: 1px solid #e8eaed;
                            border-left: 2px solid #0a4b4b;
                            text-align: center;
                            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
                        '>
                            <p style='margin: 0 0 8px 0; font-size: 0.65rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: #9ca3af;'>OPEN</p>
                            <h3 style='margin: 0; font-size: 1.6rem; font-weight: 400; color: #4a5568;'>{open_count}</h3>
                        </div>""", unsafe_allow_html=True)

                    with kpi_col3:
                        st.markdown(f"""<div style='
                            background: #ffffff;
                            border-radius: 10px;
                            padding: 20px 16px;
                            border: 1px solid #e8eaed;
                            border-left: 2px solid #0a4b4b;
                            text-align: center;
                            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
                        '>
                            <p style='margin: 0 0 8px 0; font-size: 0.65rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: #9ca3af;'>IN PROGRESS</p>
                            <h3 style='margin: 0; font-size: 1.6rem; font-weight: 400; color: #4a5568;'>{in_progress_count}</h3>
                        </div>""", unsafe_allow_html=True)

                    with kpi_col4:
                        st.markdown(f"""<div style='
                            background: #ffffff;
                            border-radius: 10px;
                            padding: 20px 16px;
                            border: 1px solid #e8eaed;
                            border-left: 2px solid #4d7a40;
                            text-align: center;
                            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
                        '>
                            <p style='margin: 0 0 8px 0; font-size: 0.65rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; color: #9ca3af;'>COMPLETE</p>
                            <h3 style='margin: 0; font-size: 1.6rem; font-weight: 400; color: #4d7a40;'>{completion_rate}%</h3>
                        </div>""", unsafe_allow_html=True)

                    # Spacing after KPI cards
                    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

                    if not project_df.empty:
                        # Render STATIC read-only table for display
                        # Hide Project column since we're already showing project-specific tables
                        render_tasks_table(project_df, limit=len(project_df), hide_project_column=True, show_transcript_checked=show_transcript_global)

                    # Elegant spacing between project sections
                    if idx < len(unique_projects) - 1:  # Don't add extra space after last project
                        st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    # LOAD METAFLEX JAVASCRIPT AT END OF PAGE
    import os
    import streamlit.components.v1 as components

    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_path = os.path.join(os.path.dirname(current_dir), "static", "metaflex.js")

    if os.path.exists(js_path):
        with open(js_path, 'r') as f:
            js_code = f.read()

        # Inject via iframe (only way to run JS in Streamlit)
        components.html(
            f"""
            <script>
            {js_code}
            </script>
            """,
            height=0,
            width=0
        )
        print(f"✅ MetaFlex JS loaded on Home page from: {js_path}")
    else:
        print(f"❌ JS not found at: {js_path}")