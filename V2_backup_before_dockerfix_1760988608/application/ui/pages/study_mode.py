import streamlit as st
import base64
from core.decision_engine import DecisionEngine
from streamlit_autorefresh import st_autorefresh

def render():
    st.title("📖 Study Mode")

    if "privacy_accepted" not in st.session_state:
        st.session_state.privacy_accepted = False
    if "camera_verified" not in st.session_state:
        st.session_state.camera_verified = False
    if "current_mood" not in st.session_state:
        st.session_state.current_mood = "neutral"

    # Step 1: Privacy notice
    if not st.session_state.privacy_accepted:
        st.warning("""
        **Privacy Notice**

        This feature may temporarily access your webcam and local files to analyze focus levels.
        No data is stored or shared externally.
        """)
        if st.button("✅ I Understand and Accept"):
            st.session_state.privacy_accepted = True
            st.rerun()
        return

    # Step 2: Camera check
    if not st.session_state.camera_verified:
        with st.expander("🎥 Camera Permission Test"):
            st.info("Take a snapshot to verify camera access.")
            img = st.camera_input("Camera Test")
            if img:
                st.session_state.camera_verified = True
                st.success("✅ Camera access granted!")
                st.rerun()
        return

    # Step 3: Poll mood every 15s
    st_autorefresh(interval=15 * 1000, key="mood_poll_refresh")

    engine = DecisionEngine()
    mood = engine.get_mood()
    st.session_state.current_mood = mood
    theme = engine.get_theme(mood)

    # Apply dynamic theme
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {theme['bg']} !important;
            color: {theme['text']} !important;
            transition: background-color 1s ease, color 1s ease;
        }}
        .stSidebar {{
            background-color: {theme['sidebar']} !important;
            transition: background-color 1s ease;
        }}
        h1, h2, h3, h4, h5, h6, p, span {{
            color: {theme['text']} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="padding: 15px; border-radius: 10px;
                    background-color:{theme['sidebar']};
                    color:{theme['text']};
                    text-align:center;">
            <h4>🧠 Current Mood: <b>{mood.upper()}</b></h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("---")
    uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
    if uploaded_file:
        st.write(f"### 📘 Uploaded File: **{uploaded_file.name}**")
        base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px"></iframe>',
            unsafe_allow_html=True
        )
    else:
        st.info("Upload a PDF to start reading.")

    st.caption("🔄 Theme automatically updates every 15 seconds based on detected mood.")
