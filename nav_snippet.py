# Clean hamburger menu navigation
nav_container = st.container()

with nav_container:
    # Simple navigation: Logo, Current Page Title, Hamburger Menu
    cols = st.columns([0.8, 3, 0.8])

    # Logo
    with cols[0]:
        if os.path.exists(logo_path):
            st.image(logo_path, width=50)

    # Current Page Title
    with cols[1]:
        st.markdown(f"""
            <h1 style='
                margin: 0;
                padding: 12px 0;
                font-size: 1.5rem;
                font-weight: 700;
                color: #0a4b4b;
                letter-spacing: -0.02em;
            '>{st.session_state.current_page}</h1>
        """, unsafe_allow_html=True)

    # Hamburger Menu
    with cols[2]:
        with st.popover("☰", use_container_width=True):
            st.markdown("### Navigation")

            for page_name in pages_list:
                if page_name == "Logout":
                    st.markdown("---")  # Separator before logout
                    if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                        # Clear authentication-related session state
                        auth_keys = ['authentication_status', 'name', 'username', 'logout', 'login']
                        for key in auth_keys:
                            if key in st.session_state:
                                try:
                                    del st.session_state[key]
                                except:
                                    pass

                        # Force authentication status to None
                        st.session_state.authentication_status = None
                        st.session_state.name = None
                        st.session_state.username = None

                        # Call authenticator logout
                        try:
                            authenticator.logout(location='unrendered', key='unique_logout_key')
                        except:
                            pass

                        # Set query param
                        st.query_params["logout"] = "1"

                        # Force immediate rerun
                        st.rerun()
                else:
                    # Navigation button
                    is_current = st.session_state.current_page == page_name
                    button_label = f"{'✓ ' if is_current else ''}{page_name}"

                    if st.button(button_label, key=f"nav_{page_name}", use_container_width=True, type="primary" if is_current else "secondary"):
                        st.session_state.current_page = page_name
                        st.rerun()
