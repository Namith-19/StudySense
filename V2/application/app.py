import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import numpy as np, cv2, base64, io, time
import requests, json
from ui_helpers import load_dark_pastel_theme, apply_emotion_theme
from auth import register_user, validate_user

load_dark_pastel_theme()

INFERENCE_HOST = st.secrets.get('INFERENCE_HOST') or (st.experimental_get_query_params().get('inference_host', ['inference'])[0])
INFERENCE_URL = f"http://{INFERENCE_HOST}:8000/predict"

# Simple routing
if 'page' not in st.session_state:
    st.session_state.page = 'home'

with st.sidebar:
    st.title("StudySense")
    page = st.radio("Navigation", ["Home", "Study Mode", "Dashboard", "Settings"] )
    st.session_state.page = page

if st.session_state.page == 'Home':
    st.header("StudySense — AI Emotion Aware Study Assistant")
    st.write("Welcome. Use Study Mode to start a study session. Toggle settings in Settings.")
    if st.button("Quick Start: Study Mode"):
        st.session_state.page = 'Study Mode'
        st.experimental_rerun()

elif st.session_state.page == 'Settings':
    st.header("Settings (local demo)")
    st.write("This demo stores aggregated session data in MySQL. Camera inference goes to the local inference service.")

elif st.session_state.page == 'Dashboard':
    st.header("Dashboard")
    st.write("Coming soon: session charts and history (reads from MySQL).")

elif st.session_state.page == 'Study Mode':
    st.header("📘 Study Mode")
    if 'consented' not in st.session_state:
        with st.form('consent'):
            st.write("**Privacy notice**: Camera frames are sent to a local inference service only if you accept. No frames are stored by default.")
            agree = st.checkbox('I consent to local processing for this session')
            if st.form_submit_button('Start') and agree:
                st.session_state.consented = True
                st.experimental_rerun()
        st.stop()

    st.write("Camera active — inference sent to local inference service.")

    # Display webcam and run a lightweight transformer that sends small JPEGs to inference
    class RemoteTransformer(VideoTransformerBase):
        def __init__(self):
            self.last_sent = 0
            self.current_emotion = 'Neutral'
            self.current_conf = 0.0

        def transform(self, frame):
            img = frame.to_ndarray(format='bgr24')
            # simple face detection (grayscale, haar cascades omitted for brevity)
            now = time.time()
            # throttle to 1fps
            if now - self.last_sent > 1.0:
                _, jpg = cv2.imencode('.jpg', cv2.resize(img, (160,160)))
                b64 = base64.b64encode(jpg.tobytes()).decode()
                try:
                    r = requests.post(INFERENCE_URL, json={'image_b64': b64}, timeout=1.5)
                    j = r.json()
                    st.session_state['current_emotion'] = j.get('label', 'Neutral')
                    st.session_state['current_confidence'] = j.get('confidence', 0.0)
                except Exception as e:
                    # inference failed; keep previous
                    pass
                self.last_sent = now
            # annotate frame with label
            label = st.session_state.get('current_emotion', 'Neutral')
            cv2.putText(img, label, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200,200,200), 2)
            return img

    webrtc_ctx = webrtc_streamer(key="study-sense", video_transformer_factory=RemoteTransformer,
                   