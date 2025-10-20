import streamlit as st

def show_login_page(navigate):
    st.title("🔐 StudySense Login")
    st.subheader("Welcome back! Please sign in to continue.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        # Placeholder: skip real validation for now
        if username and password:
            st.session_state.authenticated = True
            navigate("Home")
        else:
            st.error("Please enter both username and password.")
