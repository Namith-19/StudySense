import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def show_dashboard_page(navigate):
    st.title("📊 StudySense Dashboard")
    st.subheader("Track your daily concentration performance")

    # Placeholder data
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    concentration = np.random.randint(50, 100, size=7)
    df = pd.DataFrame({"Day": days, "Concentration": concentration})

    st.line_chart(df, x="Day", y="Concentration", height=300)

    st.info("More detailed analytics and reports will appear here once database integration is done.")
