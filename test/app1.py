import streamlit as st
import base64

# ---- PAGE CONFIG ----
st.set_page_config(page_title="StudySense", layout="wide")

# ---- INITIAL SESSION STATE ----
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None
if "privacy_agreed" not in st.session_state:
    st.session_state.privacy_agreed = False


# ---- NAVIGATION FUNCTION ----
def navigate(page_name: str):
    st.session_state.page = page_name


# ---- GLOBAL CSS ----
st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
    font-family: "Poppins", sans-serif;
}
.nav-btn {
    background-color: #4A90E2;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 24px;
    margin-right: 10px;
    text-decoration: none;
}
.nav-btn:hover {
    background-color: #357ABD;
}
.centered {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 80vh;
}
.privacy-box {
    background-color: #fff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ---- LOGIN PAGE ----
def login_page():
    st.markdown("<h1 style='text-align:center;'>🔐 StudySense Login</h1>", unsafe_allow_html=True)
    with st.container():
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if username and password:
                    st.session_state.logged_in = True
                    navigate("home")
                    st.rerun()
                else:
                    st.warning("Please enter both username and password.")


# ---- HOME PAGE ----
def home_page():
    st.title("🏠 StudySense Home")
    st.write("Welcome to StudySense! Choose an option below:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            navigate("dashboard")
            st.rerun()
    with col2:
        if st.button("📘 Study Mode", use_container_width=True):
            navigate("study")
            st.rerun()


# ---- DASHBOARD PAGE ----
def dashboard_page():
    st.title("📊 StudySense Dashboard")
    st.write("This section will visualize your focus metrics and study trends.")
    st.info("Graphs and metrics will appear here once backend integration is done.")
    if st.button("⬅ Back to Home"):
        navigate("home")
        st.rerun()


# ---- STUDY MODE PAGE ----
def study_mode_page():
    st.title("📘 StudySense Mode")

    # --- Privacy Notice ---
    if not st.session_state.privacy_agreed:
        st.markdown("### ⚠️ Privacy Notice")
        st.markdown("""
        <div class="privacy-box">
        <p>By enabling StudySense Mode, you allow the application to monitor study-related data 
        and personalize focus tracking, alerts, and break recommendations.</p>
        <p>Your data is processed locally and never stored externally.</p>
        </div>
        """, unsafe_allow_html=True)

        agree = st.checkbox("I have read and agree to the above terms.")
        if agree:
            st.session_state.privacy_agreed = True
            st.rerun()
        else:
            st.stop()

    # --- PDF Upload ---
    uploaded_pdf = st.file_uploader("Upload a PDF to begin studying", type=["pdf"])
    if uploaded_pdf is not None:
        st.session_state.pdf_file = uploaded_pdf
        base64_pdf = base64.b64encode(uploaded_pdf.read()).decode("utf-8")
        pdf_display = f'<center> <iframe src="data:application/pdf;base64,{base64_pdf}" width="93%" height="850" type="application/pdf" style="border:5px solid rgb(68, 79, 92); border-radius:50px" ></iframe> </center>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    # --- Settings Sidebar ---
    st.sidebar.title("⚙️ Settings")
    st.sidebar.checkbox("Enable UI Customization")
    st.sidebar.checkbox("Enable Alerts")
    st.sidebar.checkbox("Enable Break Recommendations")

    if st.button("⬅ Back to Home"):
        navigate("home")
        st.rerun()


# ---- ROUTING LOGIC ----
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "study":
        study_mode_page()
    else:
        home_page()
