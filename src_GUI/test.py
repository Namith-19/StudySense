import streamlit as st
import base64
import time

def animated_title():
    words = "StudySense, your customized learning buddy!!"
    text_placeholder = st.empty()   # Reserve one spot
    accumulated = ""                # To hold combined text
    for word in words:
        accumulated += f"<span class='st-title'>{word}</span>"
        text_placeholder.markdown(accumulated, unsafe_allow_html=True)
        time.sleep(0.05)


st.markdown(
    """
    <style>
    .st-title {
        font-size: 20px;       
        font-family: Monospace;      
        color: #D3DAD9;         
        font-weight: bold;

    }      
    .stApp {
        background-color: #37353E;
    }

    .divider-thick {
        border: none;
        height: 100px;  /* thickness */
        background-color: red;  /* color */
        margin: 20px 0;  /* spacing */
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.set_page_config(page_title="PDF Viewer", layout="wide")

# st.title("📄 Simple PDF Viewer in Streamlit")

animated_title()

# st.markdown("<hr class='divider-thick'></hr>", unsafe_allow_html=True)

st.write("---")



# Upload a PDF file
pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

if pdf_file is not None:
    # Read the PDF as bytes
    pdf_bytes = pdf_file.read()

    # Encode to base64
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    # Embed PDF inside an iframe
    pdf_display = f"""
    <center>
    <iframe src="data:application/pdf;base64,{base64_pdf}" width="1300" height="900" type="application/pdf" style="border:5px solid rgb(68, 79, 92); border-radius:50px" ></iframe>
    </center>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)
else:
    st.info("Please upload a PDF file to view it here.")
