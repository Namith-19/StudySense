import streamlit as st

def show_home_page(navigate):
    st.title("🏠 StudySense Home")
    st.write("Choose an action to get started:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Go to Dashboard", use_container_width=True):
            navigate("Dashboard")

    with col2:
        if st.button("📚 Enter Study Mode", use_container_width=True):
            navigate("StudyMode")
