"""
MetaFlex Navigation Component
"""

import streamlit as st
import streamlit.components.v1 as components


def load_navigation(current_page: str = "Home", user_name: str = "Téa"):
    """
    Load the MetaFlex navigation header with lime green active state.
    
    Args:
        current_page: The current page name (e.g., "Home", "My Tasks")
        user_name: The name to display in the user badge
    
    Returns:
        The selected page from navigation clicks, or None
    """
    
    navigation_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; background: transparent; overflow: hidden; }}
            
            .nav-container {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(12px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                padding: 0 48px;
                height: 68px;
                display: flex;
                align-items: center;
                gap: 12px;
                position: relative;
            }}
            
            .nav-container::after {{
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, #d4ff00 0%, #b8e600 25%, #7fa830 50%, #4d7a40 75%, #0a4b4b 100%);
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                margin-right: 20px;
                padding-right: 40px;
                border-right: 1px solid rgba(95, 140, 140, 0.1);
            }}
            
            .logo {{
                width: 38px;
                height: 38px;
                border-radius: 8px;
                background: linear-gradient(135deg, #7a9999, #6a8989);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
                font-size: 18px;
            }}
            
            .nav-items {{
                display: flex;
                align-items: center;
                gap: 8px;
                flex: 1;
            }}
            
            .nav-button {{
                background: transparent;
                border: none;
                color: #516060;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 24px;
                transition: all 0.2s ease;
                cursor: pointer;
                letter-spacing: 0.5px;
                border-radius: 24px;
                text-transform: uppercase;
            }}
            
            .nav-button:hover:not(.active) {{
                color: #5f8c8c;
                background: rgba(95, 140, 140, 0.1);
            }}
            
            .nav-button.active {{
                background: #d4ff00;
                color: #1a1a1a;
                font-weight: 700;
                box-shadow: 0 2px 8px rgba(212, 255, 0, 0.3);
            }}
            
            .user-section {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-left: auto;
                padding-left: 40px;
                border-left: 1px solid rgba(95, 140, 140, 0.1);
            }}
            
            .user-badge {{
                background: linear-gradient(135deg, #f4f6f6, #eaeded);
                border-radius: 20px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 600;
                color: #2a3a3a;
            }}
            
            .logout-button {{
                background: linear-gradient(135deg, #fafbfc 0%, #f5f7f7 100%);
                border: none;
                border-radius: 24px;
                color: #ff6b6b;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 24px;
                cursor: pointer;
                text-transform: uppercase;
            }}
        </style>
    </head>
    <body>
        <div class="nav-container">
            <div class="logo-section">
                <div class="logo">X</div>
            </div>
            
            <div class="nav-items">
                <button class="nav-button {('active' if current_page == 'Home' else '')}" onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: 'Home'}}, '*')">Home</button>
                <button class="nav-button {('active' if current_page == 'My Tasks' else '')}" onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: 'My Tasks'}}, '*')">My Tasks</button>
                <button class="nav-button {('active' if current_page == 'Team Tasks' else '')}" onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: 'Team Tasks'}}, '*')">Team Tasks</button>
                <button class="nav-button {('active' if current_page == 'Archive' else '')}" onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: 'Archive'}}, '*')">Archive</button>
                <button class="nav-button {('active' if current_page == 'Sales Portal' else '')}" onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: 'Sales Portal'}}, '*')">Sales Portal</button>
                <button class="nav-button {('active' if current_page == 'Investor Portal' else '')}" onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: 'Investor Portal'}}, '*')">Investor Portal</button>
            </div>
            
            <div class="user-section">
                <div class="user-badge">{user_name}</div>
                <button class="logout-button" onclick="parent.postMessage({{type: 'streamlit:setComponentValue', value: 'LOGOUT'}}, '*')">Logout</button>
            </div>
        </div>
    </body>
    </html>
    """
    
    return components.html(navigation_html, height=72, scrolling=False)