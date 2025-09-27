import streamlit as st
import cv2
import numpy as np
import tempfile
import base64

# ------------------------
# Setup
# ------------------------
st.set_page_config(page_title="StudySense - Emotion Detection", layout="wide")
st.title("📘 StudySense – Emotion & Stress Detection")

# Navigation
menu = ["📄 PDF Viewer", "🎥 Live Emotion Detection", "📊 Dashboard"]
choice = st.sidebar.radio("Navigation", menu)

# ------------------------
# PDF Viewer
# ------------------------
if choice == "📄 PDF Viewer":
    st.header("📄 Subject PDF Viewer")
    pdf_file = st.file_uploader("Upload a PDF file", type="pdf")
    if pdf_file is not None:
        base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")
        pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="1000" type="application/pdf"></iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("Please upload a PDF file to view it.")

# ------------------------
# Live Emotion Detection (Demo)
# ------------------------
elif choice == "🎥 Live Emotion Detection":
    st.header("🎥 Real-Time Emotion Detection")

    run = st.checkbox("Run Webcam")
    FRAME_WINDOW = st.image([])

    camera = cv2.VideoCapture(0)

    class_labels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

    while run:
        ret, frame = camera.read()
        if not ret:
            st.warning("⚠️ Could not access webcam")
            break

        # Convert frame to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Placeholder for prediction (replace with model inference later)
        fake_prediction = np.random.choice(class_labels)
        cv2.putText(frame, f"Emotion: {fake_prediction}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        FRAME_WINDOW.image(frame)

    camera.release()
    st.write("Webcam stopped.")

# ------------------------
# Dashboard (Placeholder)
# ------------------------
elif choice == "📊 Dashboard":
    st.header("📊 Emotion Analysis Dashboard")

    st.info("This section will show: \n"
            "- Emotion frequency over time\n"
            "- Stress/Boredom trends\n"
            "- Alerts when stress/boredom is high")

    # Placeholder demo chart
    st.line_chart({"Happy": [5, 10, 15, 20, 10],
                   "Sad": [1, 2, 2, 3, 4],
                   "Neutral": [3, 5, 7, 6, 8]})
