import streamlit as st

st.markdown(
    """
    <style>
    .divider-thick {
        border: none;
        height: 100px;
        background-color: #2196F3;
        margin: 20px 0;
        border-radius: 4px;
    }
    .divider-thin {
        border: none;
        height: 1px;
        background-color: #999;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("Above custom divider")
st.markdown("<hr class='divider-thick'>", unsafe_allow_html=True)
st.write("Below custom divider")