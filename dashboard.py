import os
import streamlit as st
import streamlit.components.v1 as components
import pages as pg
import time

st.set_page_config(
    page_title="MetaFlex Ops",
    page_icon="favicon.png",
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
        # Add timestamp to force browser cache refresh
        css_timestamp = str(int(time.time()))
        st.markdown(f"<style>/* CSS TIMESTAMP: {css_timestamp} - PREMIUM NAVIGATION v4.0 */\n{css_content}</style>", unsafe_allow_html=True)
        print(f"CSS loaded with timestamp: {css_timestamp}")  # DEBUG
else:
    st.error(f"⚠️ CSS FILE NOT FOUND at: {css_path}")  # VISIBLE ERROR

# Match the HTML preview exactly - frosted glass nav with pill buttons
components.html("""
<script>
(function() {
  console.log('✨ MATCHING HTML PREVIEW DESIGN...');

  const doc = window.parent.document;
  let buttonsFound = false;

  function forceButtonStyles() {
    // Find all navigation buttons
    let buttons = doc.querySelectorAll('[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button');

    if (buttons.length === 0) {
      buttons = doc.querySelectorAll('button[kind="primary"], button[kind="secondary"]');
    }

    if (buttons.length === 0) {
      return false;
    }

    if (!buttonsFound) {
      console.log(`🎉 FOUND ${buttons.length} BUTTONS! Applying HTML preview styles...`);
      buttonsFound = true;
    }

    buttons.forEach((button, index) => {
      const isPrimary = button.getAttribute('kind') === 'primary';

      // MATCH nav_preview.html EXACTLY with perfect vertical alignment
      if (isPrimary) {
        // Active button - filled gradient pill (exactly like nav_preview.html)
        button.style.cssText = `
          background: linear-gradient(135deg, #7a9999, #6a8989) !important;
          color: #ffffff !important;
          font-weight: 600 !important;
          border-radius: 24px !important;
          padding: 10px 20px !important;
          margin: 0 3px !important;
          border: none !important;
          box-shadow: 0 2px 8px rgba(95, 140, 140, 0.25), inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
          font-size: 14px !important;
          letter-spacing: 0.01em !important;
          white-space: nowrap !important;
          overflow: visible !important;
          text-overflow: clip !important;
          transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          line-height: 1 !important;
          vertical-align: middle !important;
        `;
      } else {
        // Inactive button - transparent pill (exactly like nav_preview.html)
        button.style.cssText = `
          background: transparent !important;
          color: #516060 !important;
          font-weight: 500 !important;
          border-radius: 24px !important;
          padding: 10px 20px !important;
          margin: 0 3px !important;
          border: none !important;
          box-shadow: none !important;
          font-size: 14px !important;
          letter-spacing: 0.01em !important;
          white-space: nowrap !important;
          overflow: visible !important;
          text-overflow: clip !important;
          transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          line-height: 1 !important;
          vertical-align: middle !important;
        `;
      }

      // Also style the inner elements of the button for perfect centering
      const buttonChildren = button.querySelectorAll('*');
      buttonChildren.forEach(child => {
        child.style.display = 'flex';
        child.style.alignItems = 'center';
        child.style.justifyContent = 'center';
        child.style.lineHeight = '1';
      });
    });

    return true;
  }

  // Continuously apply styles
  setInterval(forceButtonStyles, 50);

  // Watch for DOM changes
  const observer = new MutationObserver(forceButtonStyles);
  observer.observe(doc.body, { childList: true, subtree: true });

  // Style the logout button separately (coral/red color) - NUCLEAR OPTION
  function styleLogoutButton() {
    const doc = window.parent.document;

    // Find ALL buttons in navigation
    const allButtons = doc.querySelectorAll('[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button');

    allButtons.forEach(btn => {
      const btnText = btn.textContent.trim();

      // If this is the Logout button, force red color
      if (btnText === 'Logout') {
        // Completely replace style attribute
        btn.setAttribute('style', `
          background: transparent !important;
          background-color: transparent !important;
          background-image: none !important;
          color: #e08585 !important;
          font-weight: 500 !important;
          border-radius: 24px !important;
          padding: 10px 20px !important;
          margin: 0 !important;
          border: none !important;
          box-shadow: none !important;
          font-size: 14px !important;
          letter-spacing: 0.01em !important;
          white-space: nowrap !important;
          transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          line-height: 1 !important;
        `);

        // Force all child elements to be red too
        const logoutChildren = btn.querySelectorAll('*');
        logoutChildren.forEach(child => {
          child.style.color = '#e08585';
          child.style.setProperty('color', '#e08585', 'important');
        });
      }
    });
  }

  setInterval(styleLogoutButton, 50);

  // EXTREME NUCLEAR OPTION - requestAnimationFrame (60 times per second)
  let frameCount = 0;
  function extremeForceStyling() {
    const doc = window.parent.document;

    // 1. FORCE NAV BACKGROUND TO WHITE - ENHANCED with more pop
    const navContainer = doc.querySelector('[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child');
    if (navContainer) {
      // Brighter white background with stronger blur
      navContainer.style.backgroundImage = 'none';
      navContainer.style.background = 'rgba(255, 255, 255, 0.98)';
      navContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
      navContainer.style.backdropFilter = 'blur(20px) saturate(180%)';
      navContainer.style.webkitBackdropFilter = 'blur(20px) saturate(180%)';

      // Enhanced shadow for depth
      navContainer.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.05), 0 1px 0 rgba(255, 255, 255, 0.8) inset';
      navContainer.style.borderBottom = '1.5px solid rgba(95, 140, 140, 0.2)';

      // Log once every 60 frames (1 second)
      if (frameCount % 60 === 0) {
        console.log('✨ Enhanced nav - bg:', window.getComputedStyle(navContainer).backgroundColor);
      }

      // Force ALL child elements to be transparent
      const allChildren = navContainer.querySelectorAll('*');
      allChildren.forEach(child => {
        if (child.tagName !== 'BUTTON' && child.tagName !== 'IMG') {
          child.style.backgroundImage = 'none';
          child.style.background = 'transparent';
          child.style.backgroundColor = 'transparent';
        }
      });
    }

    // 2. FORCE LOGOUT BUTTON TO BE CORAL/RED - ULTRA AGGRESSIVE
    const allNavButtons = doc.querySelectorAll('[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:first-child button');
    allNavButtons.forEach(btn => {
      const btnText = btn.textContent.trim();
      if (btnText === 'Logout') {
        // Force color with priority
        btn.style.setProperty('color', '#e08585', 'important');
        btn.style.cssText += 'color: #e08585 !important;';

        if (frameCount % 60 === 0) {
          console.log('Logout button color:', window.getComputedStyle(btn).color);
        }

        // Force ALL nested elements with maximum priority
        const allNestedElements = btn.querySelectorAll('*');
        allNestedElements.forEach(el => {
          el.style.setProperty('color', '#e08585', 'important');
          el.style.cssText += 'color: #e08585 !important;';
        });
      }
    });

    frameCount++;
    requestAnimationFrame(extremeForceStyling);
  }

  // Start the animation frame loop
  extremeForceStyling();

  console.log('✅ EXTREME FORCE active - running on every frame (60fps)');
})();
</script>
""", height=0)

# Initialize session state for navigation (KEEP THIS)
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Logo path
logo_path = os.path.join(current_dir, "metaflexglove.png")

pages_list = ["Home", "My Tasks", "Team Tasks", "Archive", "Sales Portal", "Investor Portal", "Logout"]

# WRAP NAVIGATION IN A CONTAINER
nav_container = st.container()

with nav_container:
    nav_items_without_logout = [p for p in pages_list if p != "Logout"]

    # One-line navigation layout: compact buttons on left, spacer, then logout on right
    # Logo + 6 nav buttons with custom spacing: Home, My Tasks, Team Tasks, Archive, Sales Portal, Investor Portal
    col_logo, *nav_item_cols, col_spacer, col_separator, col_user = st.columns([0.8, 1.6, 1.6, 1.4, 1.3, 1.6, 1.6, 1.5, 0.05, 0.8])

    # Logo
    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=38)

    # Navigation items (excluding Logout)
    for idx, (col, page_name) in enumerate(zip(nav_item_cols, nav_items_without_logout)):
        with col:
            # Check if this is the current page
            is_current = st.session_state.current_page == page_name

            # Use type="primary" for current page to style it differently
            button_type = "primary" if is_current else "secondary"

            if st.button(page_name, key=f"nav_{idx}", type=button_type):
                st.session_state.current_page = page_name
                st.rerun()

    # Spacer column (empty to push user section to right)
    with col_spacer:
        st.write("")

    # Separator line before logout
    with col_separator:
        st.markdown("""
            <div style="height: 56px; display: flex; align-items: center; justify-content: center;">
                <div style="width: 1px; height: 28px; background: rgba(42, 74, 74, 0.25);"></div>
            </div>
        """, unsafe_allow_html=True)

    # Logout button on right
    with col_user:
        if st.button("Logout", key="nav_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Add spacing div to push content down
st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

# MAIN CONTENT AREA - This is where pages render
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

    # Call the appropriate page function
    go_to = functions.get(st.session_state.current_page)
    if go_to:
        go_to()
    else:
        st.error(f"⚠️ Page '{st.session_state.current_page}' is not yet implemented")
        st.info(f"Available pages: {', '.join(functions.keys())}")