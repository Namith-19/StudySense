import streamlit as st

def render():
    st.title("🔐 Login to StudySense")
    st.markdown("Please log in to continue using the StudySense assistant.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success("✅ Login successful! Loading dashboard...")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")
