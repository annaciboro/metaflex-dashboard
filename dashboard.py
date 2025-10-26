import os
import streamlit as st
import pages as pg

st.set_page_config(
    page_title="MetaFlex Ops",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

pages_list = ["Home", "Téa's Tasks", "All Tasks", "Team Tasks", "Settings", "Investor Portal"]

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "metaflexglove.svg")

# Premium navigation bar styles
st.markdown(
    """
    <style>
    .stApp {
        margin-top: 0px;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type {
        background-color: #0f6a6a;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding: 0.4rem 2rem;
        min-height: 64px;
        gap: 0rem;
    }
    /* Premium button styling for navbar */
    div[data-testid="stHorizontalBlock"]:first-of-type button {
        background: none !important;
        border: none !important;
        color: #f9f9f9 !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        letter-spacing: 0.4px !important;
        padding: 10px 22px !important;
        border-radius: 24px !important;
        transition: all 0.25s ease-in-out !important;
        box-shadow: none !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button:hover {
        background-color: rgba(255,255,255,0.08) !important;
        color: #b9c97d !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.2) !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type button:active,
    div[data-testid="stHorizontalBlock"]:first-of-type button:focus {
        background-color: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.2) !important;
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
    # User info
    st.markdown(
        """
        <div style="background: #f2f4f4; color: #4c7a7a; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 500; text-align: center; margin-top: 8px;">
            Logged in as Téa
        </div>
        """,
        unsafe_allow_html=True
    )

    # Logout button styling - placed below user info
    st.markdown("""
        <style>
        /* Target the logout button specifically in the user column */
        div[data-testid="column"]:last-of-type button[kind="secondary"] {
            background: #ef4444 !important;
            color: white !important;
            border: none !important;
            padding: 6px 20px !important;
            border-radius: 20px !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            margin-top: 4px !important;
            width: 100% !important;
            transition: all 0.2s ease-in-out !important;
        }
        div[data-testid="column"]:last-of-type button[kind="secondary"]:hover {
            background: #dc2626 !important;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("Logout", key="logout_btn", type="secondary", use_container_width=True):
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
    "Settings": pg.show_community,
    "Investor Portal": pg.show_settings,
}

# Call the appropriate page function
go_to = functions.get(st.session_state.current_page)
if go_to:
    go_to()
else:
    st.error(f"Page not found: '{st.session_state.current_page}'")
