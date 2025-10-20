import streamlit as st
from backend.database import DatabaseManager

db_manager = DatabaseManager()

def create_account_page():
    st.title("🆕 Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        elif db_manager.user_exists(username):
            st.error("Username already taken.")
        else:
            db_manager.create_user(username, password)
            st.success("Account created successfully! Please log in.")
            if st.button("Go to Login"):
                st.session_state.page = "login"
                st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()
