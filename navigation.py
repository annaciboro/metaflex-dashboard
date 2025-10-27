import os
import streamlit as st
import pages as pg
import time

st.set_page_config(
    page_title="MetaFlex Ops",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, "style.css")

print(f"Current directory: {current_dir}")  # DEBUG
print(f"CSS path: {css_path}")  # DEBUG
print(f"CSS exists: {os.path.exists(css_path)}")  # DEBUG

if os.path.exists(css_path):
    with open(css_path) as f:
        css_content = f.read()
        css_timestamp = str(int(time.time()))
        st.markdown(f"<style>/* CSS TIMESTAMP: {css_timestamp} */\n{css_content}</style>", unsafe_allow_html=True)
        print(f"CSS loaded with timestamp: {css_timestamp}")  # DEBUG
else:
    st.error(f"⚠️ CSS FILE NOT FOUND at: {css_path}")

# PREMIUM NAVIGATION STYLING - Inject into Streamlit buttons
st.markdown("""
<style>
/* Hide default Streamlit elements */
[data-testid="stSidebar"] {display: none;}
[data-testid="stSidebarNav"] {display: none;}
header[data-testid="stHeader"] {display: none;}
footer {visibility: hidden;}

/* Premium Navigation Container */
[data-testid="stHorizontalBlock"]:has(button[kind="primary"]),
[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    border-bottom: 1px solid rgba(95, 140, 140, 0.12);
    padding: 10px 48px !important;
    position: sticky;
    top: 0;
    z-index: 999;
    margin-bottom: 2rem;
}

/* Style ALL buttons in navigation */
[data-testid="stHorizontalBlock"] button {
    background: transparent !important;
    border: none !important;
    border-radius: 24px !important;
    color: #516060 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: none !important;
    height: 48px !important;
}

/* Hover state for navigation buttons */
[data-testid="stHorizontalBlock"] button:hover {
    color: #5f8c8c !important;
    background: linear-gradient(135deg, rgba(95, 140, 140, 0.08), rgba(95, 140, 140, 0.12)) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(95, 140, 140, 0.15) !important;
}

/* Active state - primary buttons */
[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background: linear-gradient(135deg, #7a9999, #6a8989) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(95, 140, 140, 0.25) !important;
}

[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #8aabab, #7a9999) !important;
    transform: translateY(-1px) !important;
}

/* Logo styling */
[data-testid="stImage"] {
    width: 38px !important;
    height: 38px !important;
    border-radius: 8px !important;
    filter: drop-shadow(0 2px 4px rgba(95, 140, 140, 0.15)) !important;
    transition: transform 0.3s ease !important;
}

[data-testid="stImage"]:hover {
    transform: scale(1.08) rotate(3deg) !important;
    cursor: pointer !important;
}

/* User badge styling */
.user-badge-nav {
    background: linear-gradient(135deg, #f4f6f6, #eaeded);
    border-radius: 20px;
    padding: 10px 18px;
    border: 1px solid rgba(95, 140, 140, 0.15);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    font-size: 13px;
    font-weight: 600;
    color: #2a3a3a;
    text-align: center;
    margin-top: 8px;
}

/* Logout button special styling */
button[data-testid*="logout" i] {
    color: #e08585 !important;
}

button[data-testid*="logout" i]:hover {
    background: rgba(224, 133, 133, 0.1) !important;
    color: #d66b6b !important;
}

/* Remove button focus outline */
[data-testid="stHorizontalBlock"] button:focus {
    outline: none !important;
    box-shadow: none !important;
}

[data-testid="stHorizontalBlock"] button[kind="primary"]:focus {
    box-shadow: 0 2px 8px rgba(95, 140, 140, 0.25) !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Logo path
logo_path = os.path.join(current_dir, "metaflexglove.svg")

# NAVIGATION BAR
pages_list = ["Home", "My Tasks", "Team Tasks", "Archive", "Sales Portal", "Investor Portal"]

# Create navigation layout
col_logo, *nav_cols, col_spacer, col_user, col_logout = st.columns([0.5] + [1]*len(pages_list) + [2, 1, 1])

# Logo
with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=38)
    else:
        st.markdown('<div style="width:38px;height:38px;background:#7a9999;border-radius:8px;"></div>', unsafe_allow_html=True)

# Navigation buttons
for idx, (col, page_name) in enumerate(zip(nav_cols, pages_list)):
    with col:
        is_current = st.session_state.current_page == page_name
        button_type = "primary" if is_current else "secondary"
        
        if st.button(page_name, key=f"nav_{idx}", type=button_type, use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()

# Spacer
with col_spacer:
    st.write("")

# User badge
with col_user:
    st.markdown('<div class="user-badge-nav">Téa</div>', unsafe_allow_html=True)

# Logout
with col_logout:
    if st.button("Logout", key="nav_logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# MAIN CONTENT
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

content_container = st.container()

with content_container:
    functions = {
        "Home": pg.show_dashboard,
        "My Tasks": pg.show_tasks,
        "Team Tasks": pg.show_analytics,
        "Archive": pg.show_archive,
        "Sales Portal": pg.show_sales_portal,
        "Investor Portal": pg.show_settings,
    }

    go_to = functions.get(st.session_state.current_page)
    if go_to:
        go_to()
    else:
        st.error(f"⚠️ Page '{st.session_state.current_page}' is not yet implemented")
        st.info(f"Available pages: {', '.join(functions.keys())}")