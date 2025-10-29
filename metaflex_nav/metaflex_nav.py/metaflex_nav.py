"""
MetaFlex Navigation Component
Helper module to load the navigation header in Streamlit apps
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path


def load_navigation(current_page: str = "Home", user_name: str = "Téa"):
    """
    Load the MetaFlex navigation header component.

    Args:
        current_page: The current page name (e.g., "Home", "My Tasks")
        user_name: The name to display in the user badge

    Returns:
        The selected page from navigation clicks, or None if no navigation occurred
    """
    
    # Paths
    base_dir = Path(__file__).parent
    nav_js_path = base_dir / "metaflex_nav.js"
    css_path = base_dir / "style.css"

    # Load JS
    if not nav_js_path.exists():
        st.error(f"Navigation JS file not found at {nav_js_path}")
        return None

    with open(nav_js_path, 'r', encoding="utf-8") as f:
        nav_js = f.read()

    # Load CSS
    nav_css = ""
    if css_path.exists():
        with open(css_path, 'r', encoding="utf-8") as f:
            nav_css = f.read()
    else:
        st.warning("⚠️ style.css not found. Using default nav styles.")

    # Create HTML
    navigation_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            {nav_css}

            body {{
                margin: 0;
                padding: 0;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }}
        </style>
    </head>
    <body>
        <script>
            // Config injected into JS runtime
            const CONFIG = {{
                navItems: [
                    {{ id: 'home', label: 'Home', page: 'Home' }},
                    {{ id: 'my_tasks', label: 'My Tasks', page: 'My Tasks' }},
                    {{ id: 'team_tasks', label: 'Team Tasks', page: 'Team Tasks' }},
                    {{ id: 'archive', label: 'Archive', page: 'Archive' }},
                    {{ id: 'sales_portal', label: 'Sales Portal', page: 'Sales Portal' }},
                    {{ id: 'investor_portal', label: 'Investor Portal', page: 'Investor Portal' }}
                ],
                logoText: 'X',
                userBadgeText: '{user_name}',
                logoutText: 'Logout',
                currentPage: '{current_page}'
            }};
            {nav_js}
        </script>
    </body>
    </html>
    """

    # Render
    selected_page = components.html(
        navigation_html,
        height=70,
        scrolling=False
    )

    return selected_page


def example_usage():
    """Demonstration of using the navigation component."""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    selected = load_navigation(
        current_page=st.session_state.current_page,
        user_name="Téa"
    )

    if selected and selected != "LOGOUT":
        st.session_state.current_page = selected
        st.rerun()
    elif selected == "LOGOUT":
        st.session_state.clear()
        st.rerun()

    page = st.session_state.current_page
    st.title(f"📄 {page} Page")
