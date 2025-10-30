import os
import streamlit as st
import streamlit.components.v1 as components
import pages as pg
import time
import base64
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

st.set_page_config(
    page_title="MetaFlex Ops",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# HANDLE LOGOUT QUERY PARAMETER
# ============================================
# Check if we're in logout mode - clear everything BEFORE loading authenticator
query_params = st.query_params
if "logout" in query_params:
    # Clear all session state except critical keys
    keys_to_clear = [k for k in list(st.session_state.keys()) if k not in ['_is_running_with_streamlit']]
    for key in keys_to_clear:
        try:
            del st.session_state[key]
        except:
            pass

    # Force authentication status to None
    st.session_state.authentication_status = None
    st.session_state.name = None
    st.session_state.username = None

    # Remove logout query param and redirect to clean page
    st.query_params.clear()
    st.rerun()

# ============================================
# AUTHENTICATION
# ============================================
# Load credentials from config.yaml
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize authenticator
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# MetaFlex styled login page
if st.session_state.get("authentication_status") is None:
    # Load logo for the X
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()

    # Massive METAFLE[X] OPERATIONS header at top
    st.markdown(f"""
        <div style="text-align: center; padding-top: 3rem; margin-bottom: 3rem;">
            <div style="
                font-size: 64px;
                font-weight: 900;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                letter-spacing: -0.03em;
                display: flex;
                align-items: baseline;
                justify-content: center;
                line-height: 1;
            ">
                <span style="
                    background: linear-gradient(135deg, #4d7a40 0%, #0a4b4b 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                ">METAFLE</span><img
                    src="data:image/png;base64,{logo_data}"
                    style="
                        height: 52px;
                        width: auto;
                        margin: 0 6px;
                        display: inline-block;
                        vertical-align: middle;
                        transform: translateY(2px);
                        filter: drop-shadow(0 4px 12px rgba(10, 75, 75, 0.3));
                    "
                /><span style="
                    margin-left: 8px;
                    color: #0a4b4b;
                ">OPERATIONS</span>
            </div>
            <div style="
                font-size: 16px;
                font-weight: 800;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                color: #4d7a40;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                margin-top: 12px;
            ">Custom Enterprise System</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        /* Login page background - Super soft grey */
        .main, section.main, [data-testid="stAppViewContainer"] {
            background: #f7f8f9 !important;
            position: relative !important;
            min-height: 100vh !important;
        }

        /* Center everything with ULTRA massive side space */
        .main .block-container {
            max-width: 100% !important;
            padding-top: 8rem !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            margin: 0 auto !important;
            position: relative !important;
            z-index: 1 !important;
        }

        /* Center the form container */
        .main .block-container > div:first-child {
            display: flex !important;
            justify-content: center !important;
            align-items: flex-start !important;
            width: 100% !important;
        }

        /* Login box with green gradient background and border - CENTERED */
        section[data-testid="stForm"] {
            background: linear-gradient(135deg,
                #f8fdf5 0%,
                #f0f9ec 25%,
                #e5f3df 50%,
                #d8ecce 75%,
                #cce5bd 100%) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-radius: 24px !important;
            padding: 48px 40px !important;
            box-shadow:
                0 8px 32px rgba(10, 75, 75, 0.12),
                0 4px 16px rgba(0, 0, 0, 0.08) !important;
            border: 3px solid transparent !important;
            border-image: linear-gradient(135deg, #4d7a40 0%, #0a4b4b 100%) 1 !important;
            position: relative !important;
            margin: 0 auto !important;
            width: 100% !important;
            max-width: 600px !important;
        }

        /* Force the form's parent containers to be narrow */
        section[data-testid="stForm"] > div,
        section[data-testid="stForm"] form {
            max-width: 100% !important;
        }

        /* Input fields - Override all Streamlit defaults */
        input,
        input[type="text"],
        input[type="password"],
        section[data-testid="stForm"] input,
        input[aria-invalid="false"],
        input[aria-invalid="true"],
        .st-ba.st-bb.st-bc.st-bd.st-be.st-bf.st-bg.st-bh.st-bi.st-bj input,
        div[data-baseweb="base-input"] input {
            border-radius: 14px !important;
            border: 2px solid #4d7a40 !important;
            border-color: #4d7a40 !important;
            border-style: solid !important;
            padding: 18px 24px !important;
            font-size: 15px !important;
            background: #ffffff !important;
            caret-color: #4d7a40 !important;
            outline: none !important;
            box-shadow: none !important;
        }

        input:focus,
        input[type="text"]:focus,
        input[type="password"]:focus,
        section[data-testid="stForm"] input:focus,
        input:focus-visible,
        input[type="text"]:focus-visible,
        input[type="password"]:focus-visible,
        input[aria-invalid="false"]:focus,
        input[aria-invalid="true"]:focus,
        .st-ba.st-bb.st-bc.st-bd.st-be.st-bf.st-bg.st-bh.st-bi.st-bj input:focus,
        div[data-baseweb="base-input"] input:focus {
            border: 2px solid #d4ff00 !important;
            border-color: #d4ff00 !important;
            border-style: solid !important;
            box-shadow: 0 0 0 4px rgba(212, 255, 0, 0.2) !important;
            outline: none !important;
            caret-color: #4d7a40 !important;
        }

        /* Remove any red error styling from Streamlit */
        input[aria-invalid="true"],
        input[aria-invalid="false"] {
            border: 2px solid #4d7a40 !important;
            border-color: #4d7a40 !important;
        }

        input[aria-invalid="true"]:focus,
        input[aria-invalid="false"]:focus {
            border: 2px solid #d4ff00 !important;
            border-color: #d4ff00 !important;
            box-shadow: 0 0 0 4px rgba(212, 255, 0, 0.2) !important;
        }

        /* Target Streamlit's baseweb input wrapper */
        div[data-baseweb="base-input"],
        div[data-baseweb="input"] {
            border: none !important;
            box-shadow: none !important;
        }

        /* Override any Streamlit emotion cache classes */
        [class*="st-emotion-cache"] input,
        [class*="st-ba"] input {
            border: 2px solid #4d7a40 !important;
            border-color: #4d7a40 !important;
        }

        [class*="st-emotion-cache"] input:focus,
        [class*="st-ba"] input:focus {
            border: 2px solid #d4ff00 !important;
            border-color: #d4ff00 !important;
            box-shadow: 0 0 0 4px rgba(212, 255, 0, 0.2) !important;
        }

        /* Center the submit button container - ULTRA AGGRESSIVE */
        section[data-testid="stForm"] [data-testid="stFormSubmitButton"],
        section[data-testid="stForm"] div[data-testid="stFormSubmitButton"],
        [data-testid="stFormSubmitButton"],
        div[data-testid="stFormSubmitButton"],
        .stFormSubmitButton,
        section[data-testid="stForm"] > div:last-child {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            text-align: center !important;
        }

        /* Login button - dark MetaFlex green gradient with white text - ULTRA AGGRESSIVE */
        button[kind="primary"],
        section[data-testid="stForm"] button[type="submit"],
        section[data-testid="stForm"] button,
        form button,
        form button[type="submit"],
        [data-testid="stForm"] button,
        [data-testid="stFormSubmitButton"] button,
        div[data-testid="stFormSubmitButton"] > button,
        [class*="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #4d7a40 0%, #0a4b4b 100%) !important;
            background-color: #4d7a40 !important;
            background-image: linear-gradient(135deg, #4d7a40 0%, #0a4b4b 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-color: transparent !important;
            border-width: 0 !important;
            border-style: none !important;
            border-radius: 14px !important;
            padding: 16px 32px !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            width: auto !important;
            min-width: 200px !important;
            max-width: 300px !important;
            display: inline-block !important;
            margin: 0 !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 8px rgba(10, 75, 75, 0.3) !important;
            outline: none !important;
        }

        /* Force white text on button and all nested elements - UPPERCASE */
        section[data-testid="stForm"] button,
        section[data-testid="stForm"] button *,
        section[data-testid="stForm"] button p,
        section[data-testid="stForm"] button div,
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stFormSubmitButton"] button * {
            color: #ffffff !important;
            text-transform: uppercase !important;
            font-size: 13px !important;
            letter-spacing: 0.1em !important;
            font-weight: 700 !important;
        }

        /* Hover state - slightly lighter */
        button[kind="primary"]:hover,
        section[data-testid="stForm"] button:hover,
        form button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #5a8a4d 0%, #0d5757 100%) !important;
            background-image: linear-gradient(135deg, #5a8a4d 0%, #0d5757 100%) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(10, 75, 75, 0.4) !important;
            border: none !important;
        }

        /* Active/Clicked state - neon green with dark green text */
        button[kind="primary"]:active,
        section[data-testid="stForm"] button:active,
        section[data-testid="stForm"] button[type="submit"]:active,
        form button:active,
        [data-testid="stFormSubmitButton"] button:active {
            background: linear-gradient(135deg, #d4ff00 0%, #c8ff00 100%) !important;
            background-image: linear-gradient(135deg, #d4ff00 0%, #c8ff00 100%) !important;
            color: #0a4b4b !important;
            transform: translateY(0) !important;
            box-shadow: 0 0 0 4px rgba(212, 255, 0, 0.3) !important;
            border: none !important;
        }

        /* Force dark green text when active */
        section[data-testid="stForm"] button:active,
        section[data-testid="stForm"] button:active *,
        [data-testid="stFormSubmitButton"] button:active,
        [data-testid="stFormSubmitButton"] button:active * {
            color: #0a4b4b !important;
        }

        /* Password field container - needs relative positioning */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"] {
            position: relative !important;
        }

        /* Password visibility toggle button - make it smaller and styled */
        button[kind="icon"],
        button[kind="iconButton"],
        div[data-baseweb="input"] button,
        section[data-testid="stForm"] button[kind="icon"],
        [data-testid="stForm"] button[kind="icon"] {
            background: transparent !important;
            background-color: transparent !important;
            background-image: none !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 6px !important;
            width: 36px !important;
            min-width: 36px !important;
            max-width: 36px !important;
            height: 36px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            box-shadow: none !important;
            color: #4d7a40 !important;
            position: absolute !important;
            right: 8px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            z-index: 10 !important;
        }

        button[kind="icon"]:hover,
        button[kind="iconButton"]:hover,
        section[data-testid="stForm"] button[kind="icon"]:hover {
            background: rgba(77, 122, 64, 0.1) !important;
            color: #0a4b4b !important;
            transform: translateY(-50%) scale(1.1) !important;
        }

        /* Ensure password input has padding for the button */
        input[type="password"] {
            padding-right: 50px !important;
        }

        /* Labels - Dark green */
        label,
        section[data-testid="stForm"] label,
        .stTextInput label,
        div[class*="stText"] label {
            color: #0a4b4b !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin-bottom: 8px !important;
        }

        /* Form title "Login" - Dark green - centered - multiple selectors */
        section[data-testid="stForm"] h1,
        section[data-testid="stForm"] h2,
        .stForm h1,
        form h1 {
            color: #0a4b4b !important;
            font-weight: 700 !important;
            font-size: 32px !important;
            text-align: center !important;
            width: 100% !important;
        }

        /* Copyright footer at bottom */
        .copyright-footer {
            position: fixed;
            bottom: 16px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 11px;
            color: #6b7878;
            font-weight: 500;
            z-index: 999;
        }
        </style>
    """, unsafe_allow_html=True)

    # Copyright footer
    st.markdown("""
        <div class="copyright-footer">
            © 2025 SBS ARCHITECTED
        </div>
    """, unsafe_allow_html=True)

# Render login form
authenticator.login(location="main", fields={"Form name": "Login"})

# Check authentication status
if st.session_state.get("authentication_status") is False:
    st.error("❌ Username or password is incorrect")
    st.stop()

elif st.session_state.get("authentication_status") is None:
    st.stop()

# If authenticated, continue with the app
# ============================================
# INITIALIZE SESSION STATE
# ============================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Overview"

# ============================================
# NAVIGATION BAR
# ============================================
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

# Get the logged-in user's name
user_name = st.session_state.get("name", "")
user_email = st.session_state.get("username", "")
is_tea = "tea" in user_name.lower() or "téa" in user_name.lower()
is_jess = user_email.lower() == "jess@metaflexglove.com"

# Different navigation based on user type
if is_tea:
    # Tea (admin) sees all pages
    pages_list = ["Overview", "My Tasks", "All Tasks", "Archive", "Sales Portal", "Investor Portal", "Logout"]
elif is_jess:
    # Jess sees team-related pages but not Sales/Investor portals
    pages_list = ["Overview", "My Tasks", "All Tasks", "Archive", "Logout"]
else:
    # Regular users only see Overview, My Tasks, Archive, and Logout
    pages_list = ["Overview", "My Tasks", "Archive", "Logout"]

nav_container = st.container()

with nav_container:
    nav_items_without_logout = [p for p in pages_list if p != "Logout"]

    # Create columns for navigation - white space on left, logo, spacer, then nav buttons
    cols = st.columns([0.15, 0.2, 0.05] + [1]*len(nav_items_without_logout) + [0.3, 0.05, 1.5])

    # White space column (left side padding)
    with cols[0]:
        st.write("")

    # Logo - controlled by style.css
    with cols[1]:
        if os.path.exists(logo_path):
            st.image(logo_path)

    # Spacer after logo
    with cols[2]:
        st.write("")

    # Navigation buttons - start at column 3
    for idx, page_name in enumerate(nav_items_without_logout):
        with cols[idx + 3]:
            is_active = st.session_state.current_page == page_name

            # Custom CSS for this specific button - GREEN UNDERLINE FOR ACTIVE STATE
            # No extra padding needed - buttons align naturally next to logo
            extra_padding = ''
            # Active state gets green gradient underline
            if is_active:
                border_bottom_style = '''
                    border-bottom: 3px solid #d4ff00 !important;
                    border-image: linear-gradient(90deg, #d4ff00 0%, #c8ff00 100%) 1 !important;
                    border-image-slice: 1 !important;
                '''
            else:
                border_bottom_style = 'border-bottom: 3px solid transparent !important;'

            st.markdown(f"""
                <style>
                /* ULTRA SPECIFIC Target for column {idx + 4} - Override emotion cache */
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl.e8vg11g2,
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl,
                html body div[data-testid="column"]:nth-child({idx + 4}) button.e8vg11g2,
                html body div[data-testid="column"]:nth-child({idx + 4}) button[kind="secondary"],
                html body div[data-testid="column"]:nth-child({idx + 4}) button[data-testid="stBaseButton-secondary"],
                html body div[data-testid="column"]:nth-child({idx + 4}) .stButton > button,
                html body div[data-testid="column"]:nth-child({idx + 4}) button {{
                    background: transparent !important;
                    background-color: transparent !important;
                    background-image: none !important;
                    color: #2d5016 !important;
                    border: none !important;
                    border-top: none !important;
                    border-left: none !important;
                    border-right: none !important;
                    {border_bottom_style}
                    box-shadow: none !important;
                    outline: none !important;
                    padding: 12px 24px !important;
                    padding-bottom: 9px !important;
                    {extra_padding}
                    font-size: 12px !important;
                    font-weight: 600 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                    width: 100% !important;
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    border-radius: 0px !important;
                    transform: translateY(0) !important;
                    min-height: auto !important;
                    line-height: 1.6 !important;
                }}

                /* Hover state */
                html body div[data-testid="column"]:nth-child({idx + 4}) button:hover,
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl:hover,
                html body div[data-testid="column"]:nth-child({idx + 4}) button[kind="secondary"]:hover {{
                    background: transparent !important;
                    background-color: transparent !important;
                    background-image: none !important;
                    color: #2d5016 !important;
                    border: none !important;
                    border-top: none !important;
                    border-left: none !important;
                    border-right: none !important;
                    {border_bottom_style}
                    box-shadow: none !important;
                    transform: translateY(-2px) !important;
                    border-radius: 0px !important;
                }}

                /* Active/click state */
                html body div[data-testid="column"]:nth-child({idx + 4}) button:active,
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl:active {{
                    background: transparent !important;
                    background-color: transparent !important;
                    color: #2d5016 !important;
                    transform: translateY(0) !important;
                }}

                /* Force text color on nested elements - TARGET EXACT STREAMLIT CLASSES */
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl.e8vg11g2 .st-emotion-cache-12j140x.et2rgd20,
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl.e8vg11g2 .st-emotion-cache-12j140x.et2rgd20 p,
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl .st-emotion-cache-12j140x,
                html body div[data-testid="column"]:nth-child({idx + 4}) .st-emotion-cache-12j140x.et2rgd20,
                html body div[data-testid="column"]:nth-child({idx + 4}) .st-emotion-cache-12j140x.et2rgd20 p,
                html body div[data-testid="column"]:nth-child({idx + 4}) button *,
                html body div[data-testid="column"]:nth-child({idx + 4}) button p,
                html body div[data-testid="column"]:nth-child({idx + 4}) button div,
                html body div[data-testid="column"]:nth-child({idx + 4}) button.st-emotion-cache-5qfegl p,
                html body div[data-testid="column"]:nth-child({idx + 4}) button .st-emotion-cache-12j140x,
                html body div[data-testid="column"]:nth-child({idx + 4}) button .st-emotion-cache-12j140x p,
                html body div[data-testid="column"]:nth-child({idx + 4}) button[data-testid="stBaseButton-secondary"] p,
                html body div[data-testid="column"]:nth-child({idx + 4}) div[data-testid="stMarkdownContainer"] p {{
                    color: #2d5016 !important;
                    text-transform: uppercase !important;
                    font-size: 12px !important;
                    font-weight: 600 !important;
                    font-variant-caps: normal !important;
                    letter-spacing: 0.05em !important;
                }}
                </style>
            """, unsafe_allow_html=True)

            if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

    # Spacer
    with cols[len(nav_items_without_logout) + 2]:
        st.write("")

    # Separator before logout
    with cols[len(nav_items_without_logout) + 3]:
        st.markdown("""
            <div style="height: 56px; display: flex; align-items: center; justify-content: center;">
                <div style="
                    width: 1px;
                    height: 40px;
                    background: linear-gradient(180deg,
                        rgba(212, 255, 0, 0.4) 0%,
                        rgba(10, 75, 75, 0.4) 100%);
                "></div>
            </div>
        """, unsafe_allow_html=True)

    # Logout button - VIBRANT CORAL
    with cols[len(nav_items_without_logout) + 4]:
        st.markdown(f"""
            <style>
            /* Force column and all parent containers to not wrap */
            div[data-testid="column"]:last-child,
            div[data-testid="column"]:last-child > div,
            div[data-testid="column"]:last-child > div > div,
            div[data-testid="column"]:last-child .stButton {{
                min-width: 120px !important;
                flex-shrink: 0 !important;
                width: auto !important;
            }}

            div[data-testid="column"]:last-child button {{
                background: transparent !important;
                color: #6b7280 !important;
                border: none !important;
                box-shadow: none !important;
                padding: 8px 16px !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                text-transform: none !important;
                letter-spacing: normal !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                width: auto !important;
                max-width: 120px !important;
                min-width: 80px !important;
                white-space: nowrap !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                flex-direction: row !important;
                transition: all 0.2s ease !important;
                border-radius: 8px !important;
            }}

            /* ULTRA AGGRESSIVE - Force text to stay on one line */
            div[data-testid="column"]:last-child button *,
            div[data-testid="column"]:last-child button p,
            div[data-testid="column"]:last-child button div,
            div[data-testid="column"]:last-child button span,
            div[data-testid="column"]:last-child button [data-testid="stMarkdownContainer"] {{
                white-space: nowrap !important;
                display: inline !important;
                flex-direction: row !important;
                writing-mode: horizontal-tb !important;
                text-orientation: mixed !important;
            }}

            div[data-testid="column"]:last-child button:hover {{
                color: #b96860 !important;
                background: rgba(209, 122, 111, 0.15) !important;
                border: none !important;
                transform: translateY(-1px) !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        if st.button("Logout", key="nav_logout"):
            # ULTIMATE LOGOUT FIX: Use st.components.html for immediate execution
            # This executes BEFORE Streamlit can interfere

            # Clear authentication-related session state only
            auth_keys = ['authentication_status', 'name', 'username', 'logout', 'login']
            for key in auth_keys:
                if key in st.session_state:
                    try:
                        del st.session_state[key]
                    except:
                        pass

            # Force authentication status to None explicitly
            st.session_state.authentication_status = None
            st.session_state.name = None
            st.session_state.username = None

            # Call authenticator logout
            try:
                authenticator.logout(location='unrendered', key='unique_logout_key')
            except:
                pass

            # Use components.html for IMMEDIATE JavaScript execution
            components.html(
                """
                <script>
                // This executes immediately in an iframe, then redirects parent
                (function() {
                    // Clear all cookies in parent window
                    var cookies = document.cookie.split(";");
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = cookies[i];
                        var eqPos = cookie.indexOf("=");
                        var name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
                        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
                        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=" + window.location.hostname;
                        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=." + window.location.hostname;
                    }

                    // Clear storage
                    try { window.localStorage.clear(); } catch(e) {}
                    try { window.sessionStorage.clear(); } catch(e) {}

                    // Try to access parent window and clear cookies there too
                    try {
                        var parentCookies = window.parent.document.cookie.split(";");
                        for (var i = 0; i < parentCookies.length; i++) {
                            var cookie = parentCookies[i];
                            var eqPos = cookie.indexOf("=");
                            var name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
                            window.parent.document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
                            window.parent.document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=" + window.location.hostname;
                            window.parent.document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=." + window.location.hostname;
                        }

                        // Clear parent storage
                        try { window.parent.localStorage.clear(); } catch(e) {}
                        try { window.parent.sessionStorage.clear(); } catch(e) {}
                    } catch(e) {
                        console.log("Could not access parent:", e);
                    }

                    // Force redirect after brief delay
                    setTimeout(function() {
                        window.top.location.href = window.location.origin + "?logout=1&_=" + Date.now();
                    }, 100);
                })();
                </script>
                """,
                height=0,
                width=0
            )

            # Also set query param for backup
            st.query_params["logout"] = "1"

            # Force immediate rerun to show login page
            st.rerun()

# Subtle gradient accent line under navigation - premium SaaS style
st.markdown("""
    <div style='
        width: 100%;
        max-width: 100vw;
        margin: 0;
        padding: 0;
        height: 1px;
        background: linear-gradient(90deg,
            #e5e7eb 0%,
            #d1d5db 50%,
            #e5e7eb 100%);
    '></div>
""", unsafe_allow_html=True)

# Logo styling for navigation bar
st.markdown("""
<style>
.st-emotion-cache-iun7dp {
    padding: 0rem 0px 0.0rem 0.0rem !important;
    position: absolute !important;
    top: -3rem !important;
    right: 0px !important;
    transition: none !important;
    opacity: 0 !important;
}

.st-emotion-cache-7czcpc > img {
    border-radius: 0.0rem !important;
    width: 300% !important;
    max-width: 300% !important;
}

img, svg {
    border-radius: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# JavaScript to forcefully fix logo height, make nav sticky, AND force button styling
st.markdown("""
<script>
function forceLogoHeight() {
    const logo = document.querySelector('[data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"] img');
    if (logo) {
        logo.removeAttribute('style');
        logo.style.cssText = 'width: auto !important; height: 140px !important; max-width: none !important; border-radius: 0px !important;';
    }
}

function makeNavSticky() {
    const nav = document.querySelector('[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child');
    if (nav) {
        nav.style.position = 'fixed';
        nav.style.top = '0';
        nav.style.left = '0';
        nav.style.right = '0';
        nav.style.zIndex = '99999';
    }
}

function forceButtonStyling() {
    console.log('🔍 Starting forceButtonStyling()...');

    // Try multiple selectors and log each attempt
    const selector1 = document.querySelectorAll('[data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"]:first-child button');
    console.log('Selector 1 (stVerticalBlock): ' + selector1.length + ' buttons');

    const selector2 = document.querySelectorAll('.st-emotion-cache-5qfegl.e8vg11g2');
    console.log('Selector 2 (.st-emotion-cache-5qfegl.e8vg11g2): ' + selector2.length + ' buttons');

    const selector3 = document.querySelectorAll('button[kind="secondary"]');
    console.log('Selector 3 (kind="secondary"): ' + selector3.length + ' buttons');

    const selector4 = document.querySelectorAll('button[data-testid="stBaseButton-secondary"]');
    console.log('Selector 4 (stBaseButton-secondary): ' + selector4.length + ' buttons');

    // Get ALL navigation buttons using multiple selectors
    const navButtons = document.querySelectorAll(
        '[data-testid="stVerticalBlock"] [data-testid="stHorizontalBlock"]:first-child button, ' +
        '[class*="st-emotion-cache"] button[kind="secondary"], ' +
        '.st-emotion-cache-5qfegl.e8vg11g2, ' +
        '.st-emotion-cache-5qfegl, ' +
        '.e8vg11g2, ' +
        'button[data-testid="stBaseButton-secondary"]'
    );

    console.log('📊 TOTAL Found ' + navButtons.length + ' navigation buttons to style');

    navButtons.forEach((button) => {
        // Check if button is in navigation (not logout or other buttons)
        const isNavButton = button.closest('[data-testid="stVerticalBlock"]');
        if (!isNavButton) return;

        // Force transparent background and remove all borders except bottom
        button.style.setProperty('background', 'transparent', 'important');
        button.style.setProperty('background-color', 'transparent', 'important');
        button.style.setProperty('background-image', 'none', 'important');
        button.style.setProperty('border', 'none', 'important');
        button.style.setProperty('border-top', 'none', 'important');
        button.style.setProperty('border-left', 'none', 'important');
        button.style.setProperty('border-right', 'none', 'important');
        button.style.setProperty('border-bottom', '3px solid transparent', 'important');
        button.style.setProperty('box-shadow', 'none', 'important');
        button.style.setProperty('outline', 'none', 'important');
        button.style.setProperty('border-radius', '0px', 'important');
        button.style.setProperty('padding', '12px 24px 9px 24px', 'important');
        button.style.setProperty('font-size', '12px', 'important');
        button.style.setProperty('font-weight', '600', 'important');
        button.style.setProperty('text-transform', 'uppercase', 'important');
        button.style.setProperty('letter-spacing', '0.05em', 'important');
        button.style.setProperty('color', '#e8f5e9', 'important');
        button.style.setProperty('font-family', "'Inter', -apple-system, BlinkMacSystemFont, sans-serif", 'important');
        button.style.setProperty('transition', 'all 0.2s ease', 'important');
        button.style.setProperty('transform', 'translateY(0)', 'important');

        // Force uppercase on text content - target ALL nested elements INCLUDING EXACT STREAMLIT CLASSES
        const textElements = button.querySelectorAll(
            'p, div, span, ' +
            '[data-testid="stMarkdownContainer"], ' +
            '.st-emotion-cache-12j140x, ' +
            '.st-emotion-cache-12j140x.et2rgd20, ' +
            '.et2rgd20'
        );
        textElements.forEach(el => {
            el.style.setProperty('text-transform', 'uppercase', 'important');
            el.style.setProperty('color', '#e8f5e9', 'important');
            el.style.setProperty('font-variant-caps', 'normal', 'important');
            el.style.setProperty('font-size', '12px', 'important');
            el.style.setProperty('font-weight', '600', 'important');
        });

        // Also force on button itself
        button.style.setProperty('text-transform', 'uppercase', 'important');
        button.style.setProperty('font-variant-caps', 'normal', 'important');
    });

    console.log('Button styling applied!');
}

function applyAll() {
    forceLogoHeight();
    makeNavSticky();
    forceButtonStyling();
}

// Run multiple times to catch Streamlit re-renders with MORE aggressive timing
console.log('Starting button styling timers...');
setTimeout(applyAll, 10);
setTimeout(applyAll, 50);
setTimeout(applyAll, 100);
setTimeout(applyAll, 200);
setTimeout(applyAll, 500);
setTimeout(applyAll, 1000);
setTimeout(applyAll, 2000);
setTimeout(applyAll, 3000);
setTimeout(applyAll, 5000);

// Re-run on any Streamlit update
const observer = new MutationObserver(() => {
    console.log('DOM mutation detected, reapplying styles...');
    applyAll();
});
observer.observe(document.body, { childList: true, subtree: true });

console.log('Button styling observer initialized!');

// Expose applyAll globally for manual debugging
window.applyMetaFlexStyling = applyAll;
console.log('✅ Run window.applyMetaFlexStyling() in console to manually apply styling');
</script>
""", unsafe_allow_html=True)

# Add spacing after nav
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# ULTRA AGGRESSIVE NAVIGATION BUTTON OVERRIDE - LOAD LAST
st.markdown("""
<style>
/* DARK THEME NAVIGATION CONTAINER */
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child {
    background: linear-gradient(135deg, #0a2f2f 0%, #0d3a3a 100%) !important;
    box-shadow: 0 0 20px rgba(212, 255, 0, 0.2), 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    border-bottom: 2px solid #2d5016 !important;
    padding: 10px 48px !important;
}

/* FINAL NUCLEAR OVERRIDE FOR NAVIGATION BUTTONS */
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button,
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button[kind="secondary"],
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button[kind="primary"],
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child [class*="st-emotion"] button,
html body div[data-testid="column"] button {
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    border: none !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    border-bottom: 3px solid transparent !important;
    box-shadow: none !important;
    outline: none !important;
    border-radius: 0px !important;
    padding: 12px 24px 9px 24px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #e8f5e9 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    transition: all 0.2s ease !important;
    transform: translateY(0) !important;
    opacity: 0.8;
}

/* Force uppercase on all text inside buttons */
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button *,
html body div[data-testid="column"] button * {
    text-transform: uppercase !important;
    color: #e8f5e9 !important;
}

/* Hover - DARK THEME */
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button:hover,
html body div[data-testid="column"] button:hover {
    background: rgba(212, 255, 0, 0.1) !important;
    transform: translateY(-2px) !important;
    border-bottom: 3px solid transparent !important;
    color: #d4ff00 !important;
    opacity: 1 !important;
}

/* Active button - DARK THEME */
html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button[kind="primary"] {
    background: linear-gradient(135deg, #2d5016, #3a6520) !important;
    color: #d4ff00 !important;
    border-bottom: 3px solid #d4ff00 !important;
    opacity: 1 !important;
}

html body [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button[kind="primary"] * {
    color: #d4ff00 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# GET CURRENT DIRECTORY
# ============================================
current_dir = os.path.dirname(os.path.abspath(__file__))

# ============================================
# LOAD METAFLEX BRAND DNA (CSS + JS)
# ============================================

def inject_css(path):
    """Embed CSS into Streamlit app with aggressive cache busting."""
    if os.path.exists(path):
        with open(path) as f:
            css = f.read()
            # Add timestamp for cache busting
            cache_buster = int(time.time() * 1000)  # Millisecond precision
            st.markdown(f'<style id="metaflex-css-{cache_buster}">{css}</style>', unsafe_allow_html=True)
            # VISIBLE indicator that CSS loaded
            st.markdown(f'<div style="position: fixed; bottom: 10px; right: 10px; background: #d4ff00; color: #000; padding: 5px 10px; border-radius: 5px; font-size: 10px; z-index: 999999;">CSS v{cache_buster}</div>', unsafe_allow_html=True)
            print(f"✅ MetaFlex CSS loaded with cache buster v{cache_buster}")
    else:
        st.error(f"⚠️ CSS file not found: {path}")

def inject_js(path):
    """Embed JS safely inside Streamlit iframe."""
    if os.path.exists(path):
        with open(path) as f:
            js = f.read()
            st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)
            print(f"✅ MetaFlex JS injected")
    else:
        st.warning(f"⚠️ JS file not found: {path}")

# --- Apply brand files ---
css_path = os.path.join(current_dir, "style.css")
js_path = os.path.join(current_dir, "static", "metaflex.js")

inject_css(css_path)
inject_js(js_path)





# ============================================
# MAIN CONTENT AREA
# ============================================
content_container = st.container()

with content_container:
    functions = {
        "Overview": pg.show_dashboard,
        "My Tasks": pg.show_tasks,
        "All Tasks": pg.show_analytics,
        "Archive": pg.show_archive,
        "Sales Portal": pg.show_sales_portal,
        "Investor Portal": pg.show_investor_portal,
    }

    go_to = functions.get(st.session_state.current_page)
    if go_to:
        go_to()
    else:
        st.error(f"⚠️ Page '{st.session_state.current_page}' is not yet implemented")
        st.info(f"Available pages: {', '.join(functions.keys())}")
