# Updated study_mode.py — using 'inference' as backend service for Docker

import streamlit as st
import base64
import time
import requests
import socket
import traceback
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from streamlit_autorefresh import st_autorefresh
from io import BytesIO
import streamlit.components.v1 as components
import json

# ================= CONFIG =================
API_URL = "http://inference:8000/predict_emotion"  # Backend emotion prediction API via Docker service 'inference'
API_TIMEOUT = 7  # seconds
MOOD_POLL_INTERVAL_SECONDS = 5 * 60  # 5 minutes
MAX_RETRIES = 3
RETRY_BACKOFF = 1.5
# ==========================================

THEME_MAP = {
    "happy": {"bg": "#fff8e1", "text": "#2b2b2b", "sidebar": "#fff3bf"},
    "surprise": {"bg": "#e0f7ff", "text": "#003355", "sidebar": "#b3ecff"},
    "sad": {"bg": "#e3f2fd", "text": "#0d47a1", "sidebar": "#bbdefb"},
    "angry": {"bg": "#ffebee", "text": "#b71c1c", "sidebar": "#ffcdd2"},
    "neutral": {"bg": "#ffffff", "text": "#0f172a", "sidebar": "#f1f5f9"},
    "tired": {"bg": "#f3e5f5", "text": "#4a148c", "sidebar": "#e1bee7"},
    "fear": {"bg": "#f1f8e9", "text": "#33691e", "sidebar": "#dcedc8"},
    "disgust": {"bg": "#f9fbe7", "text": "#827717", "sidebar": "#f0f4c3"},
}

# -------- Helper functions from your previous version --------
def check_tcp_connect(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception:
        return False

def _build_url_with_host(base_url: str, new_host: str) -> str:
    p = urlparse(base_url)
    return urlunparse(p._replace(netloc=f"{new_host}:{p.port or 80}"))

def find_reachable_host_candidates(base_url: str):
    parsed = urlparse(base_url)
    hostname = parsed.hostname or "localhost"
    candidates = [hostname, "127.0.0.1", "localhost", "inference"]
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return [(c, port) for c in candidates]

def _try_request(method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return requests.request(method, url, timeout=API_TIMEOUT, **kwargs)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            time.sleep(RETRY_BACKOFF ** attempt)

# ---------- Backend communication helpers ----------
def try_post_image(api_url, image_bytes: bytes):
    files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
    return _try_request("POST", api_url, files=files)

def probe_api_with_fallbacks(base_url):
    for host, port in find_reachable_host_candidates(base_url):
        new_url = _build_url_with_host(base_url, host)
        if check_tcp_connect(host, port):
            try:
                resp = _try_request("GET", new_url)
                if resp.status_code < 500:
                    return new_url
            except Exception:
                pass
    raise ConnectionError("No reachable backend host found")

def send_image_bytes_and_get_mood(image_bytes: bytes):
    try:
        target_url = probe_api_with_fallbacks(API_URL)
        resp = try_post_image(target_url, image_bytes)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("emotion", "neutral"), data
        return "neutral", {"error": f"Bad status: {resp.status_code}"}
    except Exception as e:
        return "neutral", {"error": str(e), "trace": traceback.format_exc()}

# ---------- New browser-side live camera streaming component ----------
def render_live_camera_sender(api_url: str, interval_seconds: int = 5, width: int = 640, height: int = 480):
    api_url_js = json.dumps(api_url)
    html = f"""
    <div style='font-family: Arial; border:1px solid #ccc; padding:10px; border-radius:8px;'>
      <div id='status'>Status: <b>idle</b></div>
      <video id='cam' autoplay playsinline width='{width}' height='{height}' style='border-radius:6px; border:1px solid #999;'></video>
      <canvas id='snap' width='{width}' height='{height}' style='display:none;'></canvas>
      <div style='margin-top:8px;'>
        <input id='interval' type='number' value='{interval_seconds}' min='1' style='width:80px;'> seconds
        <button id='startBtn'>Start Streaming</button>
        <button id='stopBtn' disabled>Stop</button>
      </div>
      <pre id='lastResp' style='background:#f9f9f9; border:1px solid #ddd; padding:6px; max-height:100px; overflow:auto;'></pre>
    </div>

    <script>
    const apiUrl = {api_url_js};
    let stream=null, timer=null;
    const vid=document.getElementById('cam');
    const canvas=document.getElementById('snap');
    const statusEl=document.getElementById('status');
    const respEl=document.getElementById('lastResp');

    async function startCamera(){{
      try{{
        stream=await navigator.mediaDevices.getUserMedia({{video:true}});
        vid.srcObject=stream;
        return true;
      }}catch(e){{
        statusEl.innerHTML='Status: <b style="color:red">Camera blocked</b>';
        return false;
      }}
    }}

    function captureFrame(){{
      const ctx=canvas.getContext('2d');
      ctx.drawImage(vid,0,0,canvas.width,canvas.height);
      return new Promise(r=>canvas.toBlob(b=>r(b),'image/jpeg',0.8));
    }}

    async function sendFrame(){{
      if(!stream)return;
      const blob=await captureFrame();
      const fd=new FormData();
      fd.append('file',blob,'frame.jpg');
      try{{
        const resp=await fetch(apiUrl,{{method:'POST',body:fd}});
        const txt=await resp.text();
        respEl.textContent=txt;
        statusEl.innerHTML='Status: <b style="color:green">sent</b>';
      }}catch(e){{
        statusEl.innerHTML='Status: <b style="color:red">error</b>';
        respEl.textContent=e;
      }}
    }}

    document.getElementById('startBtn').onclick=async()=>{{
      const ok=await startCamera();
      if(!ok)return;
      document.getElementById('startBtn').disabled=true;
      document.getElementById('stopBtn').disabled=false;
      const interval=parseInt(document.getElementById('interval').value)||{interval_seconds};
      sendFrame();
      timer=setInterval(sendFrame,interval*1000);
    }};

    document.getElementById('stopBtn').onclick=()=>{{
      clearInterval(timer);
      if(stream)stream.getTracks().forEach(t=>t.stop());
      document.getElementById('startBtn').disabled=false;
      document.getElementById('stopBtn').disabled=true;
      statusEl.innerHTML='Status: <b>stopped</b>';
    }};
    </script>
    """
    components.html(html, height=height+200, scrolling=True)

# ---------- Main render function ----------
def render():
    st.title("📖 Study Mode")

    defaults = {
        "privacy_accepted": False,
        "camera_verified": False,
        "current_emotion": "neutral",
        "current_theme": THEME_MAP["neutral"],
        "auto_poll_enabled": False,
        "auto_snapshot_bytes": None,
        "last_auto_meta": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if not st.session_state.privacy_accepted:
        st.warning("""**Privacy Notice**\n\nThis feature will access your camera to analyze emotion for adaptive themes. No data is stored externally unless handled by your backend.""")
        if st.button("✅ I Understand and Accept"):
            st.session_state.privacy_accepted = True
            st.rerun()
        return

    st.subheader("Camera Options")
    live = st.checkbox("Enable automatic camera streaming (requires CORS)", value=False)

    if live:
        st.info("Your browser will request camera permission and send frames automatically to the API.")
        render_live_camera_sender(API_URL, interval_seconds=5)
    else:
        cam_img = st.camera_input("Capture image manually")
        if cam_img and st.button("Send to API"):
            mood, meta = send_image_bytes_and_get_mood(cam_img.getvalue())
            st.session_state.current_emotion = mood
            st.session_state.current_theme = THEME_MAP.get(mood, THEME_MAP["neutral"])
            st.session_state.last_auto_meta = meta
            st.success(f"Detected emotion: {mood}")

    st.write("---")
    st.markdown(f"### Current Emotion: **{st.session_state.current_emotion}**")

    st.write("#### Theme Preview:")
    theme = st.session_state.current_theme
    st.markdown(f"<div style='background:{theme['bg']}; color:{theme['text']}; padding:10px; border-radius:8px;'>Sample Theme Area</div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("📄 Study Material")
    pdf_file = st.file_uploader("Upload a PDF", type="pdf")
    if pdf_file:
        st.success("PDF loaded successfully. Rendering below:")
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    with st.expander("Debug Info"):
        st.json(st.session_state.last_auto_meta)

if __name__ == "__main__":
    render()
