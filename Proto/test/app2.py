
import streamlit as st
import base64
from ui_config import MOOD_THEMES, UI_TRANSITION, DEFAULT_MOOD

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
if "mood" not in st.session_state:
    st.session_state.mood = DEFAULT_MOOD

def hex_to_rgb(hex_color: str):
    """Return tuple (r,g,b) for hex color like '#rrggbb' or 'rrggbb' or '#rgb'."""
    if not isinstance(hex_color, str):
        raise ValueError("hex_color must be a string")
    s = hex_color.lstrip("#").strip()
    if len(s) == 3:
        s = ''.join([c*2 for c in s])
    if len(s) != 6:
        raise ValueError("hex must be 3 or 6 digits")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return r, g, b

def relative_luminance(r, g, b):
    """Compute relative luminance (0..1) from sRGB 0..255"""
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    R, G, B = chan(r), chan(g), chan(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def pick_contrast_text(hex_bg: str, light="#F9FAFB", dark="#0F172A"):
    """Return light (for dark bg) or dark (for light bg) text color depending on background luminance.
       Use WCAG-like threshold: luminance < 0.5 -> light text, else dark text."""
    try:
        r, g, b = hex_to_rgb(hex_bg)
        lum = relative_luminance(r, g, b)
        return light if lum < 0.5 else dark
    except Exception:
        # fallback to theme-managed text (we'll return dark by default)
        return dark

def apply_theme(mood_name: str):
    theme = MOOD_THEMES.get(mood_name, MOOD_THEMES.get(DEFAULT_MOOD, {}))
    # UI_TRANSITION might be a dict or something else; handle both
    if isinstance(UI_TRANSITION, dict):
        duration = UI_TRANSITION.get("duration", 1.2)
        timing_function = UI_TRANSITION.get("timing_function", "ease-in-out")
    else:
        duration = 1.2
        timing_function = "ease-in-out"

    # Compute page text color based on background luminance (reliable)
    bg = theme.get("background", "#111827")
    page_text_color = pick_contrast_text(bg, light="#F9FAFB", dark="#0F172A")

    # Compute button text color depending on primary button background
    primary = theme.get("primary", "#3B82F6")
    btn_text_color = pick_contrast_text(primary, light="#F9FAFB", dark="#0F172A")

    accent = theme.get("accent", primary)

    st.markdown(f"""
    <style>
        /* Page background + text */
        .stApp, body, .main, .block-container {{
            background-color: {bg} !important;
            color: {page_text_color} !important;
            transition: background-color {duration}s {timing_function}, color {duration}s {timing_function};
        }}

        /* Buttons */
        div.stButton > button {{
            background-color: {primary} !important;
            color: {btn_text_color} !important;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            padding: 10px 20px;
            transition: background-color 0.35s ease, color 0.35s ease, transform 0.25s ease;
        }}
        div.stButton > button:hover {{
            background-color: {accent} !important;
            color: {pick_contrast_text(accent, light="#F9FAFB", dark="#0F172A")} !important;
            transform: scale(1.03);
        }}

        /* Privacy box */
        .privacy-box {{
            background-color: rgba(255,255,255,0.02);
            color: {page_text_color} !important;
            border-left: 4px solid {primary};
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
            transition: border-color {duration}s {timing_function}, color {duration}s {timing_function};
        }}

        /* Headings & text */
        h1,h2,h3,h4,h5,h6, p, label, span {{
            color: {page_text_color} !important;
            transition: color {duration}s {timing_function};
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {bg} !important;
            color: {page_text_color} !important;
            transition: background-color {duration}s {timing_function}, color {duration}s {timing_function};
        }}

        /* Inputs - keep readable on both bg types */
        .stTextInput > div > div > input, .stTextArea textarea {{
            background-color: rgba(255,255,255,0.03);
            color: {page_text_color} !important;
            border: 1px solid rgba(255,255,255,0.06);
        }}

        /* Iframe PDF border transition */
        iframe {{
            transition: border-color {duration}s {timing_function};
        }}
    </style>
    """, unsafe_allow_html=True)

if st.session_state.page != "login":
    apply_theme(st.session_state.mood)

if st.session_state.page != "login":
    st.sidebar.title("🎨 UI Mood Settings")
    selected_mood = st.sidebar.selectbox(
        "Select a mood theme:",
        list(MOOD_THEMES.keys()),
        index=list(MOOD_THEMES.keys()).index(st.session_state.mood)
    )
    if selected_mood != st.session_state.mood:
        st.session_state.mood = selected_mood
        apply_theme(selected_mood)
        st.rerun()

def navigate(page_name: str):
    st.session_state.page = page_name

def login_page():
    st.markdown("""
    <style>
        body, .stApp, .main, .block-container {
            background-color: #0f172a !important;
            color: #e6eef8 !important;
        }
        div.stButton > button {
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 8px;
            padding: 10px 18px;
        }
        div.stButton > button:hover {
            background-color: #3b82f6 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
            color: #e6eef8 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;color:#60a5fa;'>StudySense</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#e6eef8;'>Login</h2>", unsafe_allow_html=True)

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

def home_page():
    st.title("🏠 Home")
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

def dashboard_page():
    st.title("📊 StudySense Dashboard")
    st.write("This section will visualize your focus metrics and study trends.")
    st.info("Graphs and metrics will appear here once backend integration is done.")
    if st.button("⬅ Back to Home"):
        navigate("home")
        st.rerun()

def study_mode_page():
    st.title("📘 StudySense Mode")

    # --- Privacy Notice ---
    if not st.session_state.privacy_agreed:
        st.markdown("### ⚠️ Privacy Notice")
        st.markdown(f"""
        <div class="privacy-box">
            <p>
                <strong>Privacy Notice:</strong> Enabling <em>StudySense Mode</em> activates intelligent focus tracking, 
                study behavior analysis, and adaptive UI optimization for mental calmness.
            </p>
            <p>
                All processing is performed <strong>locally</strong> on your device — no personal data is stored, shared, or transmitted.
            </p>
            <p>
                The application uses insights from cognitive science and color psychology to help sustain focus, manage stress, 
                and recommend mindful breaks when needed.
            </p>
            <p>
                By enabling this mode, you agree to local, anonymous behavioral analysis for the purpose of improving your learning experience.
            </p>
        </div>
        """, unsafe_allow_html=True)

        agree = st.checkbox("✅ I have read and agree to the above terms.")
        if agree:
            st.session_state.privacy_agreed = True
            st.rerun()
        else:
            st.stop()

    uploaded_pdf = st.file_uploader("📄 Upload a PDF to begin studying", type=["pdf"])
    if uploaded_pdf is not None:
        st.session_state.pdf_file = uploaded_pdf
        base64_pdf = base64.b64encode(uploaded_pdf.read()).decode("utf-8")
        pdf_display = f'''
        <center>
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="93%" height="850"
        style="border:5px solid {MOOD_THEMES[st.session_state.mood]['primary']}; border-radius:20px;">
        </iframe>
        </center>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)

    st.sidebar.title("⚙️ Study Mode Settings")
    st.sidebar.checkbox("Enable UI Customization", value=True)
    st.sidebar.checkbox("Enable Alerts", value=True)
    st.sidebar.checkbox("Enable Break Recommendations", value=True)

    if st.button("⬅ Back to Home"):
        navigate("home")
        st.rerun()

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
