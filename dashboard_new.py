# ============================================================
# MetaFlex Glove Internal Operations System
# Google Sheets → Streamlit Integration
# ============================================================
import streamlit as st
import warnings
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

# Configure page (title, layout, sidebar) with favicon if available
try:
    import os
    _icon_candidates = [
        "metaflexglove.png", "assets/metaflexglove.png",
        "favicon.png", "assets/favicon.png",
        "metaflexglove.ico", "assets/metaflexglove.ico",
        os.path.expanduser("~/Desktop/metaflexglove.png"),
    ]
    _page_icon = next((p for p in _icon_candidates if os.path.exists(p)), "🧤")
except Exception:
    _page_icon = "🧤"

st.set_page_config(
    page_title="MetaFlex Operations System",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

from google.oauth2 import service_account
import gspread
import pandas as pd
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from datetime import datetime
import time
import streamlit.components.v1 as stc
import os
import html
import os
import base64
import mimetypes
try:
    from charts import create_team_completion_donut, create_project_breakdown_chart
except ImportError as e:
    st.error(f"Import error: {e}")
    import charts
    st.error(f"Available in charts: {dir(charts)}")
    raise

# ============================================================
# LOAD DATA FROM GOOGLE SHEET
# ============================================================
def load_data_from_gsheet():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    SHEET_ID = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"
    worksheet = gc.open_by_key(SHEET_ID).worksheet("Otter_Tasks")

    values = worksheet.get_all_values()
    if not values:
        return pd.DataFrame()

    headers = [h.strip() or f"Unnamed_{i}" for i, h in enumerate(values[0])]
    df = pd.DataFrame(values[1:], columns=headers)
    df = df.replace("", pd.NA).dropna(how="all")

    hidden_cols = [
        "Progress Helper", "0%", "25%", "50%", "75%", "100%",
        "Emails", "Email", "Confidence", "Notes", "Duplicate Check"
    ]
    df = df.loc[:, ~df.columns.isin(hidden_cols)]
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]
    return df


# ============================================================
# AUTO-ARCHIVE ONLY "DONE" TASKS
# ============================================================
def auto_archive_done_tasks():
    """Automatically archive all tasks with Status = 'Done'"""
    try:
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        SHEET_ID = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"
        spreadsheet = gc.open_by_key(SHEET_ID)
        worksheet = spreadsheet.worksheet("Otter_Tasks")

        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:
            return

        headers = [h.strip() for h in all_values[0]]

        status_col_idx = None
        transcript_col_idx = None

        for i, header in enumerate(headers):
            if header.lower() == "status":
                status_col_idx = i
            if "transcript" in header.lower() and "id" in header.lower():
                transcript_col_idx = i

        if status_col_idx is None or transcript_col_idx is None:
            return

        done_transcript_ids = []
        for row in all_values[1:]:
            if len(row) > max(status_col_idx, transcript_col_idx):
                status = str(row[status_col_idx]).strip().lower()
                transcript_id = str(row[transcript_col_idx]).strip()

                if status == "done" and transcript_id and transcript_id.lower() != "nan":
                    done_transcript_ids.append(transcript_id)

        for transcript_id in done_transcript_ids:
            archive_task(gc, spreadsheet, transcript_id)
            time.sleep(0.5)

    except Exception as e:
        pass


# ============================================================
# AUTHENTICATION SETUP
# ============================================================
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ============================================================
# LOGIN
# ============================================================
authenticator.login(location="main")

# ============================================================
# RUN AUTO-ARCHIVE AFTER LOGIN
# ============================================================
if st.session_state.get("authentication_status"):
    auto_archive_done_tasks()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # Sidebar brand: logo above, title on one line
    # Look for a logo file in common locations
    def get_logo_path():
        candidates = [
            "metaflexglove.png",
            "assets/metaflexglove.png",
            "logo.png",
            "assets/logo.png",
            "metaflexglove.svg",
            "assets/metaflexglove.svg",
            "logo.svg",
            "assets/logo.svg",
            # Relative path to Desktop from this project dir
            os.path.join("..", "metaflexglove.png"),
            # Absolute Desktop path
            os.path.expanduser("~/Desktop/metaflexglove.png"),
        ]
        for p in candidates:
            try:
                if os.path.exists(p):
                    return p
            except Exception:
                continue
        return None

    # Defer rendering of sidebar brand until after metrics/menu below (to place it further down)

    # Defer menu/logout until after metrics are computed so we can insert metrics above the menu

# ============================================================
# HELPERS
# ============================================================
def run_js(js_code: str, height: int = 0):
    """Inject and execute JavaScript in the app via a hidden iframe.

    Note: The script runs inside an iframe. Use window.parent.document to
    target Streamlit's main DOM when needed.
    """
    try:
        stc.html(f"<script>{js_code}</script>", height=height)
    except Exception as e:
        st.warning(f"JS injection failed: {e}")

def get_logo_path():
    """Return a path to the logo file if found in common locations."""
    candidates = [
        "metaflexglove.png",
        "assets/metaflexglove.png",
        "logo.png",
        "assets/logo.png",
        "metaflexglove.svg",
        "assets/metaflexglove.svg",
        "logo.svg",
        "assets/logo.svg",
        os.path.join("..", "metaflexglove.png"),
        os.path.expanduser("~/Desktop/metaflexglove.png"),
    ]
    for p in candidates:
        try:
            if os.path.exists(p):
                return p
        except Exception:
            continue
    return None

def get_logo_data_uri():
    """Return a base64 data URI for the logo so it renders inside HTML img src.

    This avoids issues with Streamlit not serving local file paths referenced
    directly in HTML. Falls back to None if no logo is found.
    """
    path = get_logo_path()
    if not path:
        return None
    try:
        mime, _ = mimetypes.guess_type(path)
        if not mime:
            mime = "image/png"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    except Exception:
        return None

def color_status(val):
    if not isinstance(val, str):
        return ""
    v = val.strip().lower()
    if v == "open":
        return "🔴 <span style='color:#d35b5b;font-weight:600;'>Open</span>"
    if v in ["working on it", "in progress"]:
        return "🟡 <span style='color:#d9a84e;font-weight:600;'>Working on it</span>"
    if v == "done":
        return "🟢 <span style='color:#3aa76d;font-weight:600;'>Done</span>"
    return val


def progress_bar_html(pct):
    """Progress bar WITHOUT percentage text"""
    try:
        if isinstance(pct, str):
            pct = pct.strip().replace("%", "")
        pct = float(pct)
    except:
        return ""
    pct = max(0, min(100, pct))
    return f"<div class='progress-wrapper'><div class='progress-fill' style='width:{pct}%;'></div></div>"


# ============================================================
# AUTHENTICATED SECTION
# ============================================================
if st.session_state.get("authentication_status"):

    # Header/hero bar removed per request (start directly with main content)
    # (JS helpers available via run_js(); initialization removed)

    # Top header: logo + MetaFlex Ops centered on one line
    full_name = st.session_state.get("name", "User")
    first_name = full_name.split()[0] if full_name else "User"

    _logo_uri = get_logo_data_uri()
    logo_html = f"<img src='{_logo_uri}' class='mf-brand-logo' alt='MetaFlex logo'/>" if _logo_uri else ""
    # Anchor target for sidebar "<Name>'s Dashboard" link
    st.markdown("<div id='dash'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style='width: 100%; padding: 10px 0; margin-bottom: 10px; text-align: center;'>
            <div style='max-width: 1200px; margin: 0 auto; padding: 10px 20px;'>
                <h1 style='font-size: 64px; font-weight: 800; margin: 0 0 12px 0; font-family: Inter, sans-serif; white-space: nowrap; background: linear-gradient(90deg, #d4ff00 0%, #b8e600 25%, #0f6a6a 60%, #0a5e5e 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 1px 1px 0 rgba(10, 77, 77, 0.15), 2px 2px 0 rgba(10, 77, 77, 0.13), 3px 3px 0 rgba(10, 77, 77, 0.11), 4px 4px 0 rgba(10, 77, 77, 0.09), 5px 5px 0 rgba(10, 77, 77, 0.07); filter: contrast(1.05) drop-shadow(0 0 8px rgba(212, 255, 0, 0.4));'>
                    MetaFle{f"<img src='{_logo_uri}' style='height: 58px; vertical-align: -0.08em; margin: 0 2px;' alt='x'/>" if _logo_uri else "x"} Ops
                </h1>
                <div style='width: 200px; height: 1px; margin: 0 auto 10px auto; background: linear-gradient(90deg, transparent 0%, #0a5e5e 50%, transparent 100%); box-shadow: 0 0 4px rgba(10, 94, 94, 0.4), 0 0 8px rgba(212, 255, 0, 0.2);'></div>
                <div style='font-size: 14px; letter-spacing: 0.8px; color: #0a5e5e; font-weight: 700; text-transform: uppercase; margin-top: 0; text-align: center; width: 100%; display: block; text-shadow: 0 0 10px rgba(212, 255, 0, 0.3);'>GET A GRIP ON LIFE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # (Greeting will be shown directly above the table instead of here)

    # (JS Playground removed)

    # ============================================================
    # LOAD DATA
    # ============================================================
    df = load_data_from_gsheet()
    if df.empty:
        st.warning("No tasks found.")
        st.stop()

    # ============================================================
    # SUMMARY METRICS (SINGLE INSTANCE)
    # ============================================================
    def safe_int(x):
        try:
            return int(str(x).replace('%', '').strip())
        except:
            return 0

    user_email = (st.session_state["username"] or "").lower().strip()
    admin_email = "tea@metaflexglove.com"

    if user_email == admin_email:
        metrics_df = df
    else:
        if "Person" in df.columns:
            metrics_df = df[df["Person"].str.lower() == st.session_state["name"].lower()]
        else:
            metrics_df = df

    open_tasks = len(metrics_df[metrics_df['Status'].str.lower() == 'open']) if 'Status' in metrics_df else 0
    working_tasks = len(metrics_df[metrics_df['Status'].str.lower().str.contains('working')]) if 'Status' in metrics_df else 0
    done_tasks = len(metrics_df[metrics_df['Status'].str.lower() == 'done']) if 'Status' in metrics_df else 0
    total_tasks = len(metrics_df)
    avg_progress = round(metrics_df['Progress %'].apply(safe_int).mean(), 1) if 'Progress %' in metrics_df else 0

    # (Metrics will be shown next to the greeting above the table)
    # Also show compact metrics in the sidebar
    if st.session_state.get("authentication_status"):
        with st.sidebar:
            # Build inline logo for 'x' in sidebar title (if logo available)
            x_logo = f"<img src='{_logo_uri}' class='mf-side-xlogo' alt='x'/>" if _logo_uri else "x"
            st.markdown(
                f"""
                <div class='mf-sidewrap'>
                    <div class='mf-sidebrand'>
                        <div class='mf-side-title'>MetaFle{x_logo} Ops</div>
                        <div class='mf-side-sub'>SBS Architected</div>
                    </div>
                    <div class='mf-side-middle'>
                        <a class='mf-side-heading' href='#dash'>{first_name}\'s Dashboard</a>
                        <div class='mf-side-metrics'>
                        <div class='mf-side-metric' style='display:flex; align-items:center; justify-content:space-between;'>
                            <div class='mf-sm-label'><span class='mf-dot mf-red'></span>Open</div>
                            <div class='mf-sm-value'>{open_tasks}</div>
                        </div>
                        <div class='mf-side-metric' style='display:flex; align-items:center; justify-content:space-between;'>
                            <div class='mf-sm-label'><span class='mf-dot mf-yellow'></span>In&nbsp;Progress</div>
                            <div class='mf-sm-value'>{working_tasks}</div>
                        </div>
                        <div class='mf-side-metric' style='display:flex; align-items:center; justify-content:space-between;'>
                            <div class='mf-sm-label'><span class='mf-dot mf-green'></span>Done</div>
                            <div class='mf-sm-value'>{done_tasks}</div>
                        </div>
                        <div class='mf-sep'></div>
                        <div class='mf-side-metric' style='display:flex; align-items:center; justify-content:space-between; padding-top: 4px;'>
                            <div class='mf-sm-label' style='font-weight: 700;'>Total Tasks</div>
                            <div class='mf-sm-value'>{total_tasks}</div>
                        </div>
                        </div>
                        <nav class=\"mf-menu\">
                            <a class=\"mf-menu-item mf-primary-btn\" href=\"#update-tasks\">Update Task</a>
                            <a class=\"mf-menu-item mf-primary-btn\" href=\"#add-new-task\">Add New Task</a>
                            <a class=\"mf-see-tasks-btn\" href=\"#all-tasks-table\">See All Tasks</a>
                        </nav>
                    </div>
                </div>

                """,
                unsafe_allow_html=True,
            )
            # Place a spacer so Logout sits ~4 button-rows below the last menu button
            st.markdown("<div class='mf-logout-gap'></div>", unsafe_allow_html=True)
            # Wrap logout for custom shimmer styling
            st.markdown("<div class='mf-logout-wrap'>", unsafe_allow_html=True)
            authenticator.logout("Logout", location='sidebar')
            st.markdown("</div>", unsafe_allow_html=True)

    # ============================================================
    # CHARTS SECTION (ADMIN ONLY)
    # ============================================================
    if user_email == admin_email:
        st.markdown('<div id="task-tracker"></div>', unsafe_allow_html=True)
        # Slightly smaller heading with extra space before charts
        st.markdown("<h3 class='mf-section-title mf-title-subtle'>Task Tracker Dashboard</h3>", unsafe_allow_html=True)
        col_chart1, col_chart2 = st.columns([1, 1])
        with col_chart1:
            fig_donut = create_team_completion_donut(open_tasks, working_tasks, done_tasks)
            if fig_donut:
                st.plotly_chart(fig_donut, use_container_width=True)
        with col_chart2:
            fig_project = create_project_breakdown_chart(metrics_df)
            if fig_project:
                st.plotly_chart(fig_project, use_container_width=True)

        # ============================================================
        # PROJECT METRICS BREAKDOWN
        # ============================================================
        st.markdown("<h3 class='mf-section-title mf-title-subtle'>Metrics by Project</h3>", unsafe_allow_html=True)
        if "Project" in df.columns:
            projects = sorted([str(p).title() for p in df["Project"].str.lower().str.strip().dropna().unique() if str(p).strip()])
            if projects:
                num_projects = len(projects)
                cols = st.columns(min(num_projects, 4))
                for idx, project in enumerate(projects):
                    col_idx = idx % 4
                    with cols[col_idx]:
                        # Filter by project
                        project_df = df[df["Project"].str.lower().str.strip() == project.lower()]

                        p_open = len(project_df[project_df['Status'].str.lower() == 'open']) if 'Status' in project_df else 0
                        p_working = len(project_df[project_df['Status'].str.lower().str.contains('working')]) if 'Status' in project_df else 0
                        p_done = len(project_df[project_df['Status'].str.lower() == 'done']) if 'Status' in project_df else 0
                        p_total = len(project_df)
                        p_avg_progress = round(project_df['Progress %'].apply(safe_int).mean(), 1) if 'Progress %' in project_df else 0

                        # Assign color class based on project name
                        project_lower = project.lower()
                        if 'general' in project_lower:
                            card_class = 'mf-project-card mf-project-card-general'
                        elif 'marketing' in project_lower:
                            card_class = 'mf-project-card mf-project-card-marketing'
                        elif 'product' in project_lower:
                            card_class = 'mf-project-card mf-project-card-products'
                        else:
                            card_class = 'mf-project-card'

                        st.markdown(f"""
                            <div class='{card_class}'>
                                <h4>{project}</h4>
                                <div class='mf-project-card-content'>
                                    <p><span class='mf-project-dot mf-project-dot-red'></span>Open: <strong>{p_open}</strong></p>
                                    <p><span class='mf-project-dot mf-project-dot-yellow'></span>In Progress: <strong>{p_working}</strong></p>
                                    <p><span class='mf-project-dot mf-project-dot-green'></span>Done: <strong>{p_done}</strong></p>
                                    <hr class='mf-project-divider'>
                                    <p>Total Tasks: <strong>{p_total}</strong></p>
                                    <p>Avg Progress: <strong>{p_avg_progress}%</strong></p>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
        st.markdown("---")

    # ============================================================
    # HELPER FUNCTIONS
    # ============================================================
    def update_task_fields(transcript_id, new_status, new_due_date=None):
        """Update task status and due date in Google Sheets"""
        try:
            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
            gc = gspread.authorize(creds)
            SHEET_ID = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"
            spreadsheet = gc.open_by_key(SHEET_ID)
            worksheet = spreadsheet.worksheet("Otter_Tasks")

            all_values = worksheet.get_all_values()
            headers = [h.strip() for h in all_values[0]]

            status_col_idx = None
            progress_col_idx = None
            due_date_col_idx = None

            for i, header in enumerate(headers):
                if header.lower().strip() == "status":
                    status_col_idx = i + 1
                elif "progress" in header.lower() and "%" in header.lower():
                    progress_col_idx = i + 1
                elif "due date" in header.lower():
                    due_date_col_idx = i + 1

            cell = worksheet.find(transcript_id)
            if cell:
                if status_col_idx:
                    worksheet.update_cell(cell.row, status_col_idx, new_status)
                    time.sleep(0.3)

                if progress_col_idx:
                    progress_map = {
                        "Open": "0%",
                        "Working on it": "25%",
                        "Done": "100%"
                    }
                    worksheet.update_cell(cell.row, progress_col_idx, progress_map.get(new_status, "0%"))
                    time.sleep(0.3)

                if due_date_col_idx and new_due_date:
                    formatted_date = new_due_date.strftime("%m/%d/%Y")
                    worksheet.update_cell(cell.row, due_date_col_idx, formatted_date)
                    time.sleep(0.3)

                return True
            return False
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False

    def archive_task(gc, spreadsheet, transcript_id):
        """Archive a task by moving it from Otter_Tasks to Archive"""
        try:
            worksheet = spreadsheet.worksheet("Otter_Tasks")
            all_values = worksheet.get_all_values()
            headers = all_values[0]

            cell = worksheet.find(transcript_id)
            if not cell:
                return False

            row_idx = cell.row
            row_data = all_values[row_idx - 1]

            status_col_idx = None
            for i, h in enumerate(headers):
                if h.strip().lower() == "status":
                    status_col_idx = i
                    break

            if status_col_idx is not None:
                current_status = str(row_data[status_col_idx]).strip().lower()
                if current_status != "done":
                    return False

            for i, h in enumerate(headers):
                if h.strip().lower() == "status":
                    row_data[i] = "Done"
                elif "progress" in h.lower() and "%" in h.lower():
                    row_data[i] = "100%"

            try:
                archive_sheet = spreadsheet.worksheet("Archive")
            except:
                archive_sheet = spreadsheet.add_worksheet(title="Archive", rows=1000, cols=30)
                archive_sheet.update('A1:' + chr(65 + len(headers)) + '1', [headers + ["Archived Date"]])
                time.sleep(0.5)

            archived_date = datetime.now().strftime("%m/%d/%Y %I:%M %p")
            archive_row = list(row_data) + [archived_date]
            archive_sheet.append_row(archive_row, value_input_option='USER_ENTERED')
            time.sleep(0.5)

            worksheet.delete_rows(row_idx)
            time.sleep(0.5)

            return True
        except Exception as e:
            return False

    def load_archived_tasks():
        try:
            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
            gc = gspread.authorize(creds)
            SHEET_ID = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"

            try:
                archive_sheet = gc.open_by_key(SHEET_ID).worksheet("Archive")
            except:
                return pd.DataFrame()

            values = archive_sheet.get_all_values()
            if not values or len(values) <= 1:
                return pd.DataFrame()

            headers = [h.strip() or f"Unnamed_{i}" for i, h in enumerate(values[0])]
            df = pd.DataFrame(values[1:], columns=headers)
            df = df.replace("", pd.NA).dropna(how="all")

            hidden_cols = ["Progress Helper", "0%", "25%", "50%", "75%", "100%",
                          "Emails", "Email", "Confidence", "Notes", "Duplicate Check"]
            df = df.loc[:, ~df.columns.isin(hidden_cols)]
            df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]
            return df
        except Exception as e:
            st.error(f"Error loading archive: {str(e)}")
            return pd.DataFrame()

    # ============================================================
    # ADMIN / USER VIEW
    # ============================================================
    progress_col = next((c for c in df.columns if "progress" in c.lower()), None)
    if progress_col:
        df["Progress Bar"] = df[progress_col].apply(progress_bar_html)

    if user_email == admin_email:
        tab1, tab2 = st.tabs(["Active Tasks", "Archive"])

        with tab1:
            st.markdown("<h3 class='mf-section-title mf-title-subtle'>Admin View: Filter and Sort</h3>", unsafe_allow_html=True)

            # Gradient card wrapper for filter section
            st.markdown("<div class='mf-filter-card-wrapper'>", unsafe_allow_html=True)

            proj_opts = ["All"]
            pers_opts = ["All"]
            stat_opts = ["All"]

            if "Project" in df.columns:
                proj_opts += sorted([str(p).title() for p in df["Project"].str.lower().str.strip().dropna().unique() if str(p).strip()])

            if "Person" in df.columns:
                person_list = []
                for p in df["Person"].str.lower().str.strip().dropna().unique():
                    name = str(p).title().replace("Tea", "Téa") if "tea" in str(p).lower() else str(p).title()
                    person_list.append(name)
                pers_opts += sorted(list(set(person_list)))

            if "Status" in df.columns:
                stat_opts += sorted([str(s).title() for s in df["Status"].str.lower().str.strip().dropna().unique() if str(s).strip()])

            for c in ["Person", "Project", "Status"]:
                if c in df.columns:
                    df[c] = df[c].astype(str).str.lower().str.strip()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                p = st.selectbox("Filter by Project", proj_opts)
            with col2:
                per = st.selectbox("Filter by Person", pers_opts)
            with col3:
                s = st.selectbox("Filter by Status", stat_opts)
            with col4:
                sort_choice = st.selectbox("Sort by", ["None", "Person", "Project", "Status", "Due Date (Soonest)"])

            # Close filter card wrapper
            st.markdown("</div>", unsafe_allow_html=True)

            f = df.copy()
            if p != "All" and "Project" in f.columns:
                f = f[f["Project"] == p.lower()]
            if per != "All" and "Person" in f.columns:
                f = f[f["Person"] == per.lower().replace("téa", "tea")]
            if s != "All" and "Status" in f.columns:
                f = f[f["Status"] == s.lower()]

            if sort_choice == "Due Date (Soonest)" and "Due Date" in f.columns:
                f["Due Date"] = pd.to_datetime(f["Due Date"], errors="coerce")
                f = f.sort_values(by="Due Date")

            for c in ["Person", "Project"]:
                if c in f.columns:
                    f[c] = f[c].astype(str).str.title()

            if "Person" in f.columns:
                f["Person"] = f["Person"].apply(lambda x: x.replace("Tea", "Téa") if "tea" in x.lower() else x)

            if "Status" in f.columns:
                f["Status_Plain"] = f["Status"].astype(str).str.title()
                f["Status_Display"] = f["Status_Plain"].apply(color_status)

            if "Progress Bar" in f.columns:
                cols = [c for c in f.columns if c not in ["Progress Bar", "Progress %", "Status_Plain", "Status_Display", "Status"]]
                f_display = f[cols].copy()
                f_display["Status"] = f["Status_Display"]
                f_display["Progress Bar"] = f["Progress Bar"]
            else:
                cols = [c for c in f.columns if c not in ["Progress %", "Status_Plain", "Status_Display", "Status"]]
                f_display = f[cols].copy()
                f_display["Status"] = f["Status_Display"]

            # Make transcript show full value on hover via title tooltip
            if "Transcript" in f_display.columns:
                try:
                    f_display["Transcript"] = f_display["Transcript"].apply(
                        lambda x: f"<span title='{html.escape(str(x))}'>{html.escape(str(x))}</span>"
                    )
                except Exception:
                    pass

            # Add anchor for "See All Tasks" button
            st.markdown("<div id='all-tasks-table'></div>", unsafe_allow_html=True)
            # (Removed greeting/counts from main body per request)
            st.markdown("<div class='table-container'>" + f_display.to_html(escape=False, index=False) + "</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div id="update-tasks"></div>', unsafe_allow_html=True)
            st.markdown("<h3 class='mf-section-title mf-title-subtle'>Quick Task Update</h3>", unsafe_allow_html=True)
            # Gradient card wrapper for entire update block
            with st.container():
                st.markdown("<div class='mf-card-sentinel-qt'></div>", unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    task_options = []
                    task_map = {}
                    transcript_col = "Transcript ID" if "Transcript ID" in f.columns else "Transcript"

                    if len(f) > 0 and transcript_col in f.columns and "Task" in f.columns:
                        for idx in f.index:
                            try:
                                transcript = str(f.loc[idx, transcript_col]).strip()
                                task_desc = str(f.loc[idx, "Task"])[:50]
                                status = str(f.loc[idx, "Status_Plain"]) if "Status_Plain" in f.columns else "Unknown"

                                if transcript and transcript.lower() != 'nan':
                                    option = f"[{status}] {transcript} - {task_desc}..."
                                    task_options.append(option)
                                    task_map[option] = transcript
                            except:
                                continue

                    task_options = ["Select a task..."] + task_options if task_options else ["No tasks available"]
                    selected_task = st.selectbox("Select Task to Update", task_options, key="admin_task_select")

                with col2:
                    new_status = st.selectbox("Change Status", ["Done", "Working on it", "Open"], key="admin_status_select")

                with col3:
                    new_due_date = st.date_input("New Due Date", format="MM/DD/YYYY", key="admin_date_select")

                with col4:
                    st.markdown("<div class='quick-update'>", unsafe_allow_html=True)
                    # sentinel to force primary-style button via CSS
                    st.markdown("<span class='quick-update-sentinel'></span>", unsafe_allow_html=True)
                    if st.button("Update Task", use_container_width=True, key="admin_update_btn"):
                        if selected_task not in ["Select a task...", "No tasks available"]:
                            transcript_id = task_map.get(selected_task)
                            if transcript_id and update_task_fields(transcript_id, new_status, new_due_date):
                                st.success(f"✅ Task updated!")
                                if new_status == "Done":
                                    st.info("Task will be auto-archived on next refresh.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Update failed")
                        else:
                            st.warning("Please select a task")
                    st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.subheader("📦 Archived Tasks")
            df_archive = load_archived_tasks()

            if df_archive.empty:
                st.info("No archived tasks. Tasks marked 'Done' will appear here.")
            else:
                progress_col_archive = next((c for c in df_archive.columns if "progress" in c.lower()), None)
                if progress_col_archive:
                    df_archive["Progress Bar"] = df_archive[progress_col_archive].apply(progress_bar_html)

                for c in ["Person", "Project"]:
                    if c in df_archive.columns:
                        df_archive[c] = df_archive[c].astype(str).str.title()

                if "Person" in df_archive.columns:
                    df_archive["Person"]
                    df_archive["Person"] = df_archive["Person"].apply(lambda x: x.replace("Tea", "Téa") if isinstance(x, str) and "tea" in x.lower() else x)

                if "Status" in df_archive.columns:
                    df_archive["Status_Display"] = df_archive["Status"].apply(color_status)

                if "Progress Bar" in df_archive.columns:
                    cols = [c for c in df_archive.columns if c not in ["Progress Bar", "Progress %", "Status"]]
                    df_archive_display = df_archive[cols].copy()
                    df_archive_display["Status"] = df_archive["Status_Display"] if "Status_Display" in df_archive.columns else df_archive["Status"]
                    df_archive_display["Progress Bar"] = df_archive["Progress Bar"]
                else:
                    cols = [c for c in df_archive.columns if c not in ["Progress %", "Status"]]
                    df_archive_display = df_archive[cols].copy()
                    if "Status_Display" in df_archive.columns:
                        df_archive_display["Status"] = df_archive["Status_Display"]

                st.markdown("<div class='table-container'>" + df_archive_display.to_html(escape=False, index=False) + "</div>", unsafe_allow_html=True)
                st.success(f"Showing {len(df_archive)} archived tasks.")

    else:
        if "Person" in df.columns:
            df_user = df[df["Person"].str.lower() == st.session_state["name"].lower()]
        else:
            df_user = df.copy()

        if df_user.empty:
            st.info("You have no active tasks.")
        else:
            for c in ["Person", "Project"]:
                if c in df_user.columns:
                    df_user[c] = df_user[c].astype(str).str.title()

            if "Person" in df_user.columns:
                df_user["Person"] = df_user["Person"].apply(lambda x: x.replace("Tea", "Téa") if isinstance(x, str) and "tea" in x.lower() else x)

            if "Status" in df_user.columns:
                df_user["Status_Plain"] = df_user["Status"].astype(str).str.title()
                df_user["Status_Display"] = df_user["Status_Plain"].apply(color_status)

            if "Progress Bar" in df_user.columns:
                cols = [c for c in df_user.columns if c not in ["Progress Bar", "Progress %", "Status_Plain", "Status_Display", "Status"]]
                df_user_display = df_user[cols].copy()
                df_user_display["Status"] = df_user["Status_Display"]
                df_user_display["Progress Bar"] = df_user["Progress Bar"]
            else:
                cols = [c for c in df_user.columns if c not in ["Progress %", "Status_Plain", "Status_Display", "Status"]]
                df_user_display = df_user[cols].copy()
                df_user_display["Status"] = df_user["Status_Display"]

            # Hover tooltip for Transcript column (user view)
            if "Transcript" in df_user_display.columns:
                try:
                    df_user_display["Transcript"] = df_user_display["Transcript"].apply(
                        lambda x: f"<span title='{html.escape(str(x))}'>{html.escape(str(x))}</span>"
                    )
                except Exception:
                    pass

            # Add anchor for "See All Tasks" button
            st.markdown("<div id='all-tasks-table'></div>", unsafe_allow_html=True)
            # (Removed greeting/counts from main body per request)
            st.markdown("<div class='table-container'>" + df_user_display.to_html(escape=False, index=False) + "</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div id="update-tasks"></div>', unsafe_allow_html=True)
            st.markdown("<h3 class='mf-section-title mf-title-subtle'>Update My Tasks</h3>", unsafe_allow_html=True)
            # Gradient card wrapper for entire user update block
            with st.container():
                st.markdown("<div class='mf-card-sentinel-qt'></div>", unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    task_options = []
                    task_map = {}
                    transcript_col = "Transcript ID" if "Transcript ID" in df_user.columns else "Transcript"

                    if len(df_user) > 0 and transcript_col in df_user.columns and "Task" in df_user.columns:
                        for idx in df_user.index:
                            try:
                                transcript = str(df_user.loc[idx, transcript_col]).strip()
                                task_desc = str(df_user.loc[idx, "Task"])[:50]
                                status = str(df_user.loc[idx, "Status_Plain"]) if "Status_Plain" in df_user.columns else "Unknown"

                                if transcript and transcript.lower() != 'nan':
                                    option = f"[{status}] {transcript} - {task_desc}..."
                                    task_options.append(option)
                                    task_map[option] = transcript
                            except:
                                continue

                    task_options = ["Select a task..."] + task_options if task_options else ["No tasks available"]
                    selected_task = st.selectbox("Select Task to Update", task_options, key="user_task_select")

                with col2:
                    new_status = st.selectbox("Change Status", ["Done", "Working on it", "Open"], key="user_status_select")

                with col3:
                    new_due_date = st.date_input("New Due Date", format="MM/DD/YYYY", key="user_date_select")

                with col4:
                    st.markdown("<div class='quick-update'>", unsafe_allow_html=True)
                    # sentinel to force primary-style button via CSS
                    st.markdown("<span class='quick-update-sentinel'></span>", unsafe_allow_html=True)
                    if st.button("Update Task", use_container_width=True, key="user_update_btn"):
                        if selected_task not in ["Select a task...", "No tasks available"]:
                            transcript_id = task_map.get(selected_task)
                            if transcript_id and update_task_fields(transcript_id, new_status, new_due_date):
                                st.success(f"✅ Task updated!")
                                if new_status == "Done":
                                    st.info("Task will be auto-archived on next refresh.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Update failed")
                        else:
                            st.warning("Please select a task")
                    st.markdown("</div>", unsafe_allow_html=True)

    # ============================================================
    # ADD TASK FORM
    # ============================================================
    st.markdown("---")
    st.markdown('<div id="add-new-task"></div>', unsafe_allow_html=True)
    st.markdown("<h3 class='mf-section-title mf-title-subtle'>Add New Task Manually</h3>", unsafe_allow_html=True)
    person_list = ["", "Téa Phillips", "Megan Cole", "Justin Stehr", "+ Add New Person"]
    project_list = ["", "Conference", "Marketing", "Products", "Employees", "Finance"]

    # Gradient card wrapper for the entire form block
    with st.container():
        st.markdown("<div class='mf-card-sentinel-add'></div>", unsafe_allow_html=True)
        with st.form("manual_entry_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                transcript_id = st.text_input("Transcript ID", placeholder="2JPQQNH5ETL3YFWW")
                person_select = st.selectbox("Person", person_list)
                new_person = ""
                if person_select == "+ Add New Person":
                    new_person = st.text_input("Enter New Person Name", placeholder="Enter full name")
                status = st.selectbox("Status", ["Open", "Working on it", "Done"])

            with col2:
                date_assigned = st.date_input("Date Assigned", format="MM/DD/YYYY")
                project = st.selectbox("Project", project_list)
                due_date = st.date_input("Due Date", format="MM/DD/YYYY")

            with col3:
                task = st.text_area("Task Description", placeholder="Describe the task...", height=100)
                progress = st.slider("Progress %", 0, 100, 0, step=5)

            submitted = st.form_submit_button("Add Task", use_container_width=True)

            if submitted:
                final_person = new_person if person_select == "+ Add New Person" else person_select

                if not final_person:
                    st.error("Please select or enter a person name!")
                elif not transcript_id:
                    st.error("Please enter a Transcript ID!")
                elif not project:
                    st.error("Please select a project!")
                elif not task:
                    st.error("Please enter a task description!")
                else:
                    try:
                        SCOPES = [
                            "https://www.googleapis.com/auth/spreadsheets",
                            "https://www.googleapis.com/auth/drive"
                        ]
                        creds = service_account.Credentials.from_service_account_info(
                            st.secrets["gcp_service_account"], scopes=SCOPES
                        )
                        gc = gspread.authorize(creds)
                        SHEET_ID = "1U_9CEbWHWMQVS2C20O0fpOG5gVxoYjB7BmppKlTHIzc"
                        worksheet = gc.open_by_key(SHEET_ID).worksheet("Otter_Tasks")

                        new_row = [
                            transcript_id,
                            date_assigned.strftime("%m/%d/%Y"),
                            final_person,
                            task,
                            project,
                            status,
                            due_date.strftime("%m/%d/%Y"),
                            f"{progress}%"
                        ]

                        worksheet.append_row(new_row)
                        st.success(f"Task added successfully! Assigned to {final_person}")
                        time.sleep(1)
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error adding task: {str(e)}")

else:
    if st.session_state.get("authentication_status") == False:
        st.error("Username/password is incorrect")
    else:
        st.warning("Please enter your username and password")

# ============================================================
# LOAD GLOBAL CSS
# ============================================================
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class='mf-footer'>
        &copy; Strategic Business Solutions 2025
    </div>
    """,
    unsafe_allow_html=True,
)
