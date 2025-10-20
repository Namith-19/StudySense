# V2/application/app.py
import streamlit as st
import importlib
from pathlib import Path

# ---- Try to import your existing auth and pages (if present) ----
try:
    from auth import login_user, create_user, user_exists
except Exception:
    # safe fallback stubs (won't overwrite auth.py)
    def login_user(u, p):
        return (u == "admin" and p == "1234")
    def create_user(u, p):
        return False
    def user_exists(u):
        return False

# Try to import pages package; fall back to placeholders if missing
pages_pkg = None
try:
    pages_pkg = importlib.import_module("ui.pages")
except Exception:
    pages_pkg = None

# ---- Load CSS if present (non-invasive) ----
css_path = Path(__file__).parent / "ui" / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="StudySense", layout="wide", initial_sidebar_state="expanded")

# -----------------------
# Session init
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "login"
if "current_page" not in st.session_state:  # [NEW]
    st.session_state.current_page = "Home"

# -----------------------
# Safe rerun helper (compat)
# -----------------------
def safe_rerun():
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            pass

# -----------------------
# Placeholder renderers (used if ui.pages.* missing)
# -----------------------
def placeholder_home():
    st.title("Home")
    st.write("Home placeholder.")

def placeholder_study_mode():
    st.title("Study Mode")
    st.write("Study Mode placeholder.")

def placeholder_dashboard():
    st.title("Dashboard")
    st.write("Dashboard placeholder.")

# -----------------------
# Login / Create Account Forms (main area)
# -----------------------
def render_login_main():
    st.title("🔐 Login to StudySense")
    username = st.text_input("Username", key="login_user_input")
    password = st.text_input("Password", type="password", key="login_pass_input")
    if st.button("Login", key="login_btn"):
        try:
            ok = login_user(username, password)
        except Exception:
            ok = False
        if ok:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully.")
            st.session_state.page = "Home"
            st.session_state.current_page = "Home"  # [NEW]
            safe_rerun()
        else:
            st.error("Invalid username or password.")

def render_create_account_main():
    st.title("🆕 Create a StudySense Account")
    new_user = st.text_input("Choose username", key="create_user_input")
    new_pass = st.text_input("Choose password", type="password", key="create_pass_input")
    confirm = st.text_input("Confirm password", type="password", key="create_confirm_input")
    if st.button("Create Account", key="create_account_btn"):
        if not new_user or not new_pass:
            st.error("All fields are required.")
        elif new_pass != confirm:
            st.error("Passwords do not match.")
        else:
            try:
                if user_exists(new_user):
                    st.error("Username already exists.")
                else:
                    create_user(new_user, new_pass)
                    st.success("Account created. Please login.")
                    st.session_state.page = "login"
                    safe_rerun()
            except Exception:
                st.error("Account creation failed (auth backend error).")

# -----------------------
# Sidebar behavior
# -----------------------
if not st.session_state.logged_in:
    # Sidebar limited to login/create only
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/6858/6858504.png", width=72)
        st.title("StudySense")
        st.markdown("---")
        st.write("Please sign in or create an account to continue.")

        if st.button("🔐 Login", key="sidebar_login_btn"):
            st.session_state.page = "login"
        if st.button("🆕 Create Account", key="sidebar_create_btn"):
            st.session_state.page = "create_account"

        st.markdown("---")
        st.write("No navigation available until you log in.")
    if st.session_state.page == "login":
        render_login_main()
    else:
        render_create_account_main()
    st.stop()

# -----------------------
# Logged-in users: Full navigation + synced routing
# -----------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6858/6858504.png", width=72)
    st.title("StudySense")
    st.markdown("---")

    # [UPDATED] Use session_state.current_page to maintain nav sync
    pages = ["Home", "Study Mode", "Dashboard", "Logout"]
    choice = st.radio("Navigate", pages, index=pages.index(st.session_state.current_page))
    st.session_state.current_page = choice  # keep it synced

    st.markdown("---")
    st.write(f"Signed in as: **{st.session_state.username or 'User'}**")

# handle logout
if st.session_state.current_page == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page = "login"
    st.session_state.current_page = "Home"
    safe_rerun()

# -----------------------
# Page Routing
# -----------------------
if st.session_state.current_page == "Home":
    try:
        from ui.pages.home import show_home  # [NEW: your integrated home]
        show_home()
    except Exception:
        placeholder_home()

elif st.session_state.current_page == "Study Mode":
    try:
        # Dynamically import the Study Mode page
        study_mode_module = importlib.import_module("ui.pages.study_mode")
        if hasattr(study_mode_module, "render"):
            study_mode_module.render()
        else:
            st.warning("⚠️ 'render()' function not found in study_mode.py")
            placeholder_study_mode()
    except ModuleNotFoundError as e:
        st.error(f"Study Mode module not found: {e}")
        placeholder_study_mode()
    except Exception as e:
        st.error(f"Error loading Study Mode page: {e}")
        placeholder_study_mode()


elif st.session_state.current_page == "Dashboard":
    try:
        # Explicit import fallback — guarantees dashboard loads correctly
        dashboard_module = importlib.import_module("ui.pages.dashboard")
        if hasattr(dashboard_module, "render"):
            dashboard_module.render()
        else:
            st.warning("⚠️ 'render()' function not found in dashboard.py")
            placeholder_dashboard()
    except ModuleNotFoundError as e:
        st.error(f"Dashboard module not found: {e}")
        placeholder_dashboard()
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        placeholder_dashboard()


else:
    st.error("Unknown page selection.")
