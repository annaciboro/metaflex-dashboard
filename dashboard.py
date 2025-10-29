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
            padding-left: 35% !important;
            padding-right: 35% !important;
            margin: 0 auto !important;
            position: relative !important;
            z-index: 1 !important;
        }

        /* Login box with green gradient background and border */
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
        }

        /* Force the form's parent containers to be narrow */
        section[data-testid="stForm"] > div,
        section[data-testid="stForm"] form {
            max-width: 100% !important;
        }

        /* Input fields */
        input {
            border-radius: 14px !important;
            border: 2px solid #4d7a40 !important;
            padding: 18px 24px !important;
            font-size: 15px !important;
            background: #ffffff !important;
        }

        input:focus {
            border: 2px solid #d4ff00 !important;
            box-shadow: 0 0 0 4px rgba(212, 255, 0, 0.2) !important;
            outline: none !important;
        }

        /* Login button - centered with dark green */
        button[kind="primary"],
        section[data-testid="stForm"] button[type="submit"],
        section[data-testid="stForm"] button {
            background: linear-gradient(135deg, #4d7a40 0%, #0a4b4b 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 14px !important;
            padding: 16px 32px !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            width: 100% !important;
            display: block !important;
            margin: 0 auto !important;
        }

        button[kind="primary"]:hover,
        section[data-testid="stForm"] button:hover {
            background: linear-gradient(135deg, #5a8a4d 0%, #0d5757 100%) !important;
            transform: translateY(-1px) !important;
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

        /* Form title "Login" - Dark green - multiple selectors */
        section[data-testid="stForm"] h1,
        section[data-testid="stForm"] h2,
        .stForm h1,
        form h1 {
            color: #0a4b4b !important;
            font-weight: 700 !important;
            font-size: 32px !important;
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
            © 2025 SBS
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
    st.session_state.current_page = "Home"

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
    pages_list = ["Home", "My Tasks", "Team Tasks", "Archive", "Sales Portal", "Investor Portal", "Logout"]
elif is_jess:
    # Jess sees team-related pages but not Sales/Investor portals
    pages_list = ["Home", "My Tasks", "Team Tasks", "Archive", "Logout"]
else:
    # Regular users only see Home, My Tasks, Archive, and Logout
    pages_list = ["Home", "My Tasks", "Archive", "Logout"]

nav_container = st.container()

with nav_container:
    nav_items_without_logout = [p for p in pages_list if p != "Logout"]

    # Create columns for navigation - white space on left, logo close to Home
    cols = st.columns([0.15, 0.2] + [1]*len(nav_items_without_logout) + [0.5, 0.1, 0.8])

    # White space column (left side padding)
    with cols[0]:
        st.write("")

    # Logo - controlled by style.css
    with cols[1]:
        if os.path.exists(logo_path):
            st.image(logo_path)

    # Navigation buttons
    for idx, page_name in enumerate(nav_items_without_logout):
        with cols[idx + 2]:
            is_active = st.session_state.current_page == page_name

            # Custom CSS for this specific button - LIME GREEN ACTIVE STATE
            st.markdown(f"""
                <style>
                div[data-testid="column"]:nth-child({idx + 3}) button {{
                    background: {'linear-gradient(135deg, #d4ff00 0%, #c8ff00 100%)' if is_active else 'transparent'} !important;
                    color: {'#1a1a1a' if is_active else '#2d5016'} !important;
                    border: none !important;
                    box-shadow: {'0 4px 12px rgba(212, 255, 0, 0.4), 0 2px 6px rgba(0, 0, 0, 0.1)' if is_active else 'none'} !important;
                    padding: {'14px 28px' if is_active else '12px 24px'} !important;
                    font-size: {'13px' if is_active else '12px'} !important;
                    font-weight: {'900' if is_active else '600'} !important;
                    text-transform: uppercase !important;
                    letter-spacing: {'0.08em' if is_active else '0.05em'} !important;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                    width: 100% !important;
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    border-radius: {'28px' if is_active else '0px'} !important;
                    transform: translateY(0) !important;
                }}
                div[data-testid="column"]:nth-child({idx + 3}) button:hover {{
                    background: {'linear-gradient(135deg, #e0ff1a 0%, #d4ff00 100%)' if is_active else 'rgba(212, 255, 0, 0.15)'} !important;
                    color: {'#1a1a1a' if is_active else '#2d5016'} !important;
                    border: none !important;
                    box-shadow: {'0 6px 16px rgba(212, 255, 0, 0.5), 0 3px 8px rgba(0, 0, 0, 0.12)' if is_active else 'none'} !important;
                    transform: {'translateY(-2px)' if is_active else 'none'} !important;
                    border-radius: {'28px' if is_active else '12px'} !important;
                }}
                div[data-testid="column"]:nth-child({idx + 3}) button:active {{
                    background: linear-gradient(135deg, #d4ff00 0%, #c8ff00 100%) !important;
                    color: #1a1a1a !important;
                    transform: scale(0.98) !important;
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
            div[data-testid="column"]:last-child button {{
                background: transparent !important;
                color: #d17a6f !important;
                border: none !important;
                box-shadow: none !important;
                padding: 12px 24px !important;
                font-size: 12px !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.08em !important;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
                width: 100% !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                border-radius: 24px !important;
            }}
            div[data-testid="column"]:last-child button:hover {{
                color: #b96860 !important;
                background: rgba(209, 122, 111, 0.15) !important;
                border: none !important;
                transform: translateY(-1px) !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        if st.button("Logout", key="nav_logout", use_container_width=True):
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

            # Don't call st.rerun() - let JavaScript handle the redirect

# Neon green gradient line under navigation
st.markdown("""
    <div style='
        width: 100%;
        max-width: 100vw;
        margin: 10px 0 0 0;
        padding: 0;
    '>
        <div style='
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg,
                #d4ff00 0%,
                #b8e600 20%,
                #7fa830 40%,
                #4d7a40 60%,
                #0a4b4b 80%,
                #0a4b4b 100%);
        '></div>
        <div style='
            width: 100%;
            text-align: right;
            padding: 4px 20px 0 0;
            font-size: 8px;
            font-weight: 500;
            letter-spacing: 0.5px;
            color: rgba(10, 75, 75, 0.4);
        '>Architected by SBS</div>
    </div>
""", unsafe_allow_html=True)

# JavaScript to forcefully fix logo height AND make nav sticky with MutationObserver
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

function applyAll() {
    forceLogoHeight();
    makeNavSticky();
}

// Run multiple times to catch Streamlit re-renders
setTimeout(applyAll, 50);
setTimeout(applyAll, 200);
setTimeout(applyAll, 500);
setTimeout(applyAll, 1000);

// Re-run on any Streamlit update
const observer = new MutationObserver(applyAll);
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# Add spacing after nav
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

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
        "Home": pg.show_dashboard,
        "My Tasks": pg.show_tasks,
        "Team Tasks": pg.show_analytics,
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
