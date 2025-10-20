import streamlit as st

def render():
    st.title("⚙️ Settings")
    st.subheader("Theme & Preferences")

    theme = st.selectbox("Select Theme", ["Dark Pastel", "Light Minimal", "Cyber Neon"])
    notify = st.checkbox("Enable Session Reminders", True)
    model = st.selectbox("Select AI Model", ["FER+ CNN", "EmotionNet v2", "Custom Model"])

    st.markdown("---")
    st.button("💾 Save Settings")
