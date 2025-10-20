import streamlit as st


# Dark pastel theme injection (call at top of each page)
def load_dark_pastel_theme():
    st.set_page_config(layout="wide")
    st.markdown("""
    <style>
    html, body, [class*="css"] {
    color: #ECEFF4;
    background-color: #121212;
    font-family: 'Inter', sans-serif;
    }
    section[data-testid="stSidebar"] {
    background-color: #1E1E1E;
    border-right: 1px solid #2C2C2C;
    }
    div.stButton > button {
    color: #ECEFF4;
    background-color: #2C2C2C;
    border: 1px solid #2C2C2C;
    border-radius: 8px;
    padding: 0.5em 1.2em;
    transition: 0.2s;
    }
    div.stButton > button:hover {
    background-color: #3B3B3B;
    border: 1px solid #7E8CE0;
    }
    input, textarea {
    background-color: #1E1E1E !important;
    color: #ECEFF4 !important;
    border-radius: 6px;
    border: 1px solid #2C2C2C !important;
    }
    iframe { border: 1px solid #2C2C2C; border-radius: 12px; }
    .card { background: #1E1E1E; border-radius: 12px; padding: 1rem; }
    </style>
    """, unsafe_allow_html=True)


# map emotion to accent color
EMOTION_ACCENTS = {
'Fatigued': '#7E8CE0',
'Energized': '#A3BE8C',
'Frustrated': '#BF616A',
'Neutral': '#88C0D0'
}


def apply_emotion_theme(emotion):
    accent = EMOTION_ACCENTS.get(emotion, '#7E8CE0')
    st.markdown(f"""
    <style>
    .stProgress > div > div > div > div {{ background-color: {accent} !important; }}
    .stButton > button:hover {{ background-color: {accent}55 !important; border: 1px solid {accent} !important; }}
    """, unsafe_allow_html=True)

