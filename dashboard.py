import os
import streamlit as st
import pages as pg

st.set_page_config(
    page_title="MetaFlex Ops",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, "style.css")

if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Hide Streamlit's built-in sidebar and menu
hide_default_format = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        header[data-testid="stHeader"] {display: none;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_default_format, unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

pages_list = ["Home", "Téa's Tasks", "All Tasks", "Archive", "Sales Portal", "Investor Portal"]

logo_path = os.path.join(current_dir, "metaflexglove.svg")

# Clean navigation bar with teal accent
st.markdown(
    """
    <style>
    .stApp {
        margin-top: 0px;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type {
        background-color: #ffffff;
        box-shadow: 0 1px 4px rgba(26, 36, 36, 0.06);
        border-bottom: 2px solid #5f8c8c;
        padding: 0.8rem 3rem;
        min-height: 72px;
        gap: 0rem;
    }
    /* Clean button styling for navbar */
    div[data-testid="stHorizontalBlock"]:first-of-type button {
        background: none !important;
        border: none !important;
        color: #516060 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        letter-spacing: 0 !important;
        padding: 10px 20px !important;
        border-radius: 24px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button:hover {
        background-color: rgba(95, 140, 140, 0.08) !important;
        color: #5f8c8c !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button:active,
    div[data-testid="stHorizontalBlock"]:first-of-type button:focus {
        background-color: rgba(95, 140, 140, 0.12) !important;
        color: #5f8c8c !important;
        font-weight: 600 !important;
    }
    /* MetaFlex logo styling */
    div[data-testid="stHorizontalBlock"]:first-of-type img {
        filter: brightness(0) saturate(100%) invert(49%) sepia(13%) saturate(808%) hue-rotate(131deg) brightness(90%) contrast(86%);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create navigation bar
col_logo, *nav_cols, col_user = st.columns([1] + [1.2]*len(pages_list) + [1.5])

with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=40)
    else:
        st.markdown("### MF")

for idx, (col, page_name) in enumerate(zip(nav_cols, pages_list)):
    with col:
        if st.button(page_name, key=f"nav_{idx}", use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()

with col_user:
    # User info and logout inline
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-top: 8px;">
            <div style="background: #f2f4f4; color: #4c7a7a; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 500;">
                Logged in as Téa
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Logout button styling - ghost button inline
    st.markdown("""
        <style>
        /* Target the logout button in the user column - ghost style */
        div[data-testid="column"]:last-of-type button[kind="secondary"] {
            background: transparent !important;
            color: #516060 !important;
            border: 1px solid #d8dcdc !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            margin-top: 8px !important;
            margin-left: auto !important;
            width: auto !important;
            transition: all 0.2s ease-in-out !important;
            position: absolute !important;
            right: 0 !important;
            top: 0 !important;
        }
        div[data-testid="column"]:last-of-type button[kind="secondary"]:hover {
            background: #f9fafa !important;
            border-color: #5f8c8c !important;
            color: #5f8c8c !important;
        }
        /* Make the user column container relative for absolute positioning */
        div[data-testid="column"]:last-of-type {
            position: relative !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("Logout", key="logout_btn", type="secondary"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Add spacing below navbar
st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

functions = {
    "Home": pg.show_dashboard,
    "Téa's Tasks": pg.show_tasks,
    "All Tasks": pg.show_analytics,
    "Team Tasks": pg.show_team_tasks,
    "Archive": pg.show_community,
    "Investor Portal": pg.show_settings,
}

# Call the appropriate page function
go_to = functions.get(st.session_state.current_page)
if go_to:
    go_to()
else:
    st.error(f"Page not found: '{st.session_state.current_page}'")
