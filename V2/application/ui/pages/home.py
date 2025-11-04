import streamlit as st
from datetime import datetime
import random

def show_home():
    # --- Greeting Section ---
    username = st.session_state.get("username", "User")
    st.markdown(f"<h2 style='text-align: center;'>👋 Welcome back, {username}!</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af;'>\"Your focus determines your reality.\"</p>", unsafe_allow_html=True)
    st.markdown("---")

    # --- Quick Stats Section (Dummy placeholders for now) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📈 Focus Score", f"{random.randint(70, 100)}%")
    col2.metric("🧠 Avg Duration", f"{random.randint(30, 90)} min")
    col3.metric("🔁 Sessions", random.randint(5, 25))
    col4.metric("🕓 Last Active", datetime.now().strftime("%I:%M %p"))

    st.markdown("---")

    # --- Navigation Buttons ---
    st.markdown("### 🚀 Quick Actions")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📊 Go to Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    with c2:
        if st.button("🎯 Start Study Mode", use_container_width=True):
            st.session_state.current_page = "Study Mode"
            st.rerun()

    st.markdown("---")

    # --- Recent Activity ---
    st.subheader("📚 Recent Session Summary")
    st.info("Last session: 45 mins | Focus Level: 82% | Emotion: Calm 😌")

    # --- Tip of the Day ---
    tips = [
        "Take short breaks every 50 minutes to reset focus.",
        "Keep your study environment distraction-free.",
        "Use the Pomodoro timer to maintain rhythm.",
        "Hydrate often — dehydration reduces cognitive performance.",
        "Review your notes for 5 minutes before starting a new topic."
    ]
    st.markdown("### 💡 Tip of the Day")
    st.success(random.choice(tips))
