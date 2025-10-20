import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/6858/6858504.png", width=80)
        st.title("StudySense")
        st.markdown("---")

        page = option_menu(
            "Navigation",
            ["Home", "Study Mode", "Dashboard", "Login"],
            icons=["house", "camera-video", "bar-chart", "box-arrow-in-right"],
            default_index=0,
            styles={
                "container": {"background-color": "#202124", "padding": "5px"},
                "icon": {"color": "#4ECDC4", "font-size": "20px"},
                "nav-link": {
                    "color": "#E8E8E8",
                    "font-size": "16px",
                    "--hover-color": "#2C2F33",
                },
                "nav-link-selected": {"background-color": "#4ECDC4", "color": "#000"},
            }
        )
        return page
