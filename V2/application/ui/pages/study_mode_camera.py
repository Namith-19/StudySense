# V2/study_mode_camera.py
"""
Camera integration for Study Mode page. Minimal and non-invasive.
Usage (inside your Study Mode streamlit page file):
    from study_mode_camera import attach_camera_to_study_mode
    attach_camera_to_study_mode()
This will render the camera controls and call the inference API.
"""

import os
import io
import time
import requests
import streamlit as st
from typing import Optional, Dict
from ui_adapter import handle_prediction_result

# default inference API (environment override allowed)
DEFAULT_INFERENCE_API = os.getenv("STUDYSENSE_INFERENCE_API", "http://127.0.0.1:8000/predict_emotion")

def send_image_to_api(img_bytes: bytes, api_url: str = DEFAULT_INFERENCE_API, timeout: int = 6) -> Optional[Dict]:
    """
    Send one image (jpeg bytes) to the inference API as form-data.
    Expects JSON response. Returns Python dict or None.
    """
    try:
        files = {"file": ("frame.jpg", img_bytes, "image/jpeg")}
        resp = requests.post(api_url, files=files, timeout=timeout)
        resp.raise_for_status()
        # Accept JSON or attempt to parse text->json
        return resp.json()
    except Exception as e:
        st.error(f"Inference API call failed: {e}")
        return None

def attach_camera_to_study_mode(
    api_url: str = DEFAULT_INFERENCE_API,
    auto_interval: int = 5,
    show_local_overlay: bool = True
):
    """
    Renders camera UI in Streamlit and wires predictions to ui_adapter.
    Call this from your Study Mode page. Returns nothing.
    """
    st.subheader("Study Mode — Emotion-aware UI")
    cols = st.columns([1, 3])
    with cols[0]:
        use_camera = st.checkbox("Enable camera", value=False)
        interval = st.slider("Auto-analysis interval (s)", 1, 10, value=auto_interval)
        one_shot = st.button("Analyze now")
        st.markdown("**Tip:** Allow camera permission in your browser and click 'Take photo' if needed.")
    with cols[1]:
        camera_file = None
        if use_camera:
            camera_file = st.camera_input("Camera: take a photo")
        else:
            st.info("Enable the camera to analyze your face & adapt the UI.")

    # Manual analyze triggered by button
    if one_shot:
        if not camera_file:
            st.warning("No camera image available. Please take a photo.")
        else:
            img_bytes = camera_file.getvalue()
            with st.spinner("Sending frame to inference..."):
                result = send_image_to_api(img_bytes, api_url=api_url)
            if result is None:
                st.error("No response from inference API.")
            else:
                # Delegate to ui_adapter to map & apply UI changes
                handle_prediction_result(result, show_streamlit=show_local_overlay)

    # Auto-sample using session_state timestamp guard
    if use_camera and camera_file:
        # initialize
        if "last_auto_ts" not in st.session_state:
            st.session_state["last_auto_ts"] = 0.0
        now = time.time()
        if now - st.session_state["last_auto_ts"] >= interval:
            st.session_state["last_auto_ts"] = now
            img_bytes = camera_file.getvalue()
            with st.spinner("Auto-sending to inference..."):
                result = send_image_to_api(img_bytes, api_url=api_url)
            if result:
                handle_prediction_result(result, show_streamlit=show_local_overlay)
