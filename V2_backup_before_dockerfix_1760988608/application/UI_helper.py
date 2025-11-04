import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def show_dashboard(username):
    st.title(f"📊 Welcome, {username}")
    st.subheader("Concentration Levels Overview")

    time = np.arange(0, 10, 0.5)
    concentration = np.sin(time) * 10 + 70 + np.random.randn(len(time)) * 2

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(time, concentration, marker='o')
    ax.set_title("Concentration Over Time")
    ax.set_xlabel("Session Time (min)")
    ax.set_ylabel("Concentration (%)")
    st.pyplot(fig)

def show_studymode():
    st.title("🎧 Study Mode")
    st.write("Focus mode is ON — distractions are off. Let's get to work!")
