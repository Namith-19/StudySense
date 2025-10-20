import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

def render():
    st.title("📊 Study Session Insights")
    st.write("Track your concentration levels over recent study sessions.")

    # ---- Mock Data (replace with real data if available) ----
    # Simulating last 10 study sessions
    sessions = [f"Session {i}" for i in range(1, 11)]
    timestamps = [datetime.now() - timedelta(days=10 - i) for i in range(10)]
    concentration = [random.uniform(40, 100) for _ in range(10)]  # Random % values

    data = pd.DataFrame({
        "Session": sessions,
        "Date": [t.strftime("%b %d, %Y") for t in timestamps],
        "Concentration (%)": concentration
    })

    # ---- Plotly Graph ----
    fig = px.line(
        data,
        x="Date",
        y="Concentration (%)",
        markers=True,
        title="Concentration Levels Over Last 10 Study Sessions",
    )

    fig.update_traces(line_color="#1f77b4", line_width=3)
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Concentration (%)",
        template="plotly_white",
        hovermode="x unified",
        font=dict(size=14),
    )

    # ---- Render Graph ----
    st.plotly_chart(fig, use_container_width=True)

    # ---- Optional Summary ----
    avg_conc = sum(concentration) / len(concentration)
    st.metric(label="Average Concentration", value=f"{avg_conc:.1f}%")
