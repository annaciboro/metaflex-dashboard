import os
import streamlit as st
import streamlit.components.v1 as components
import pages as pg
import time
import base64

def get_base64_image(image_path):
    """Convert image to base64 for embedding in HTML"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

st.set_page_config(
    page_title="MetaFlex Ops",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# ============================================
# LOAD METAFLEX CSS
# ============================================
css_path = os.path.join(current_dir, "style.css")

if os.path.exists(css_path):
    with open(css_path, 'r') as f:
        css_content = f.read()
        # Add timestamp to force browser cache refresh
        css_timestamp = str(int(time.time()))
        st.markdown(
            f"<style>/* CSS TIMESTAMP: {css_timestamp} - METAFLEX */\n{css_content}</style>",
            unsafe_allow_html=True
        )
        print(f"✅ MetaFlex CSS loaded with timestamp: {css_timestamp}")
else:
    st.error(f"⚠️ CSS FILE NOT FOUND at: {css_path}")

# ============================================
# LOAD METAFLEX JAVASCRIPT - AFTER CSS TO OVERRIDE
# ============================================
js_path = os.path.join(current_dir, "static", "metaflex_interactions.js")
if os.path.exists(js_path):
    with open(js_path, 'r') as f:
        js_code = f.read()

    # BASE64 encode the JavaScript to avoid ALL escaping issues
    js_b64 = base64.b64encode(js_code.encode('utf-8')).decode('utf-8')

    # DIRECT INJECTION using base64 - NO ESCAPING NEEDED
    st.components.v1.html(
        f"""
        <script>
        (function() {{
            try {{
                const parent = window.parent;
                const doc = parent.document;

                if (parent.metaflexInjected) {{
                    console.log('[IFRAME] ✅ MetaFlex already injected');
                    return;
                }}

                parent.metaflexInjected = true;
                console.log('[IFRAME] 💥 Injecting MetaFlex into PARENT window...');

                // Decode base64 JavaScript
                const jsCode = atob('{js_b64}');

                // Create script in parent
                const script = doc.createElement('script');
                script.id = 'metaflex-system';
                script.textContent = jsCode;

                doc.head.appendChild(script);
                console.log('[IFRAME] ✅ MetaFlex injected into <head>');

            }} catch (error) {{
                console.error('[IFRAME] ❌ Injection failed:', error);
                console.log('[IFRAME] ⚠️ Running in iframe (limited functionality)...');

                // Fallback: decode and run in iframe
                const jsCode = atob('{js_b64}');
                const script = document.createElement('script');
                script.textContent = jsCode;
                document.head.appendChild(script);
            }}
        }})();
        </script>
        """,
        height=0
    )
    print(f"✅ MetaFlex JavaScript NUCLEAR INJECTED from: {js_path}")
else:
    print(f"⚠️ MetaFlex JavaScript not found at: {js_path}")
    st.warning("MetaFlex interactions could not be loaded.")

# ============================================
# LOAD NAV OVERRIDE JAVASCRIPT - DISABLED (using custom HTML nav now)
# ============================================
# nav_js_path = os.path.join(current_dir, "static", "nav_override.js")
# Nav override is disabled because we're using pure HTML navigation with query params

# ============================================
# INITIALIZE SESSION STATE
# ============================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# ============================================
# NAVIGATION BAR
# ============================================
logo_path = os.path.join(current_dir, "metaflexglove.png")
pages_list = ["Home", "My Tasks", "Team Tasks", "Archive", "Sales Portal", "Investor Portal", "Logout"]

nav_container = st.container()

with nav_container:
    nav_items_without_logout = [p for p in pages_list if p != "Logout"]

    # Create columns for navigation
    cols = st.columns([0.3] + [1]*len(nav_items_without_logout) + [0.5, 0.1, 0.8])

    # Logo
    with cols[0]:
        if os.path.exists(logo_path):
            st.image(logo_path, width=38)

    # Navigation buttons
    for idx, page_name in enumerate(nav_items_without_logout):
        with cols[idx + 1]:
            is_active = st.session_state.current_page == page_name

            # Custom CSS for this specific button
            st.markdown(f"""
                <style>
                div[data-testid="column"]:nth-child({idx + 2}) button {{
                    background: transparent !important;
                    color: #0d4d3d !important;
                    border: none !important;
                    box-shadow: none !important;
                    padding: 10px 20px !important;
                    font-size: 13px !important;
                    font-weight: {'700' if is_active else '600'} !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.8px !important;
                    font-family: 'Inter', sans-serif !important;
                    width: 100% !important;
                    text-shadow: {'0 0 10px #d4ff00, 0 0 20px #d4ff00, 0 0 30px #d4ff00' if is_active else 'none'} !important;
                    transition: all 0.3s ease !important;
                    border-radius: 0 !important;
                }}
                div[data-testid="column"]:nth-child({idx + 2}) button:hover {{
                    text-shadow: 0 0 8px #d4ff00, 0 0 15px #d4ff00 !important;
                    border: none !important;
                }}
                </style>
            """, unsafe_allow_html=True)

            if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

    # Spacer
    with cols[len(nav_items_without_logout) + 1]:
        st.write("")

    # Separator before logout
    with cols[len(nav_items_without_logout) + 2]:
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

    # Logout button
    with cols[len(nav_items_without_logout) + 3]:
        st.markdown(f"""
            <style>
            div[data-testid="column"]:last-child button {{
                background: transparent !important;
                color: #0d4d3d !important;
                border: none !important;
                box-shadow: none !important;
                padding: 10px 20px !important;
                font-size: 13px !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.8px !important;
                font-family: 'Inter', sans-serif !important;
                width: 100% !important;
                transition: all 0.3s ease !important;
                border-radius: 0 !important;
            }}
            div[data-testid="column"]:last-child button:hover {{
                text-shadow: 0 0 8px #d4ff00, 0 0 15px #d4ff00 !important;
                border: none !important;
            }}
            </style>
        """, unsafe_allow_html=True)

        if st.button("Logout", key="nav_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Neon green gradient line under navigation - full width in container
st.markdown("""
    <div style='
        width: 100%;
        max-width: 100vw;
        margin: 10px 0 20px 0;
        padding: 0;
    '>
        <div style='
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg,
                #d4ff00 0%,
                #b8e600 20%,
                #7fa830 40%,
                #4d7a40 60%,
                #0f6a6a 80%,
                #0a4b4b 100%);
        '></div>
    </div>
""", unsafe_allow_html=True)

# Add spacing after nav
st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

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
