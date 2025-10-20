import streamlit as st
from streamlit_option_menu import option_menu

# Configure page
st.set_page_config(page_title="StudySense", layout="wide")

# Initialize session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = 'Login'

# Page routing logic
def navigate(page_name):
    st.session_state.page = page_name

# Import pages dynamically
if st.session_state.page == 'Login':
    import pages.login as login
    login.show_login_page(navigate)

elif st.session_state.page == 'Home':
    import pages.home as home
    home.show_home_page(navigate)

elif st.session_state.page == 'Dashboard':
    import pages.dashboard as dashboard
    dashboard.show_dashboard_page(navigate)

elif st.session_state.page == 'StudyMode':
    import pages.study_mode as study
    study.show_study_mode_page(navigate)
