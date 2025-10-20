import streamlit as st

def render():
    st.title("🧠 AI Insights")
    st.write("Get actionable recommendations from your recent study patterns.")

    st.info("⚡ You were most focused between 9–11 AM this week.")
    st.warning("😔 Slight dip in mood detected during evening sessions.")
    st.success("🎯 Recommendation: Schedule critical study sessions in the morning.")
