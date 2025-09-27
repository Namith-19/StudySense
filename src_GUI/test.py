import streamlit as st
import base64

st.set_page_config(page_title="StudySense", layout="wide")

st.title("StudySense")

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
    <iframe src="data:application/pdf;base64,{base64_pdf}" width="1500" height="800" type="application/pdf" style="border:5px solid rgb(68, 79, 92); border-radius:50px" ></iframe>
    </center>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)
else:
    st.info("Please upload a PDF file to view it here.")
