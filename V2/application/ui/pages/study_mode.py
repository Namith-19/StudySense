# # # study_mode.py (fixed)
# # import streamlit as st
# # import base64
# # import time
# # import requests
# # import socket
# # import traceback
# # from datetime import datetime
# # from urllib.parse import urlparse, urlunparse
# # from io import BytesIO
# # import streamlit.components.v1 as components
# # import json
# # import numpy as np
# # from collections import deque

# # # ================= CONFIG =================
# # # Inside Docker (server -> inference service)
# # API_URL = "http://inference:8000/predict_emotion"
# # # Browser-accessible endpoint (for live JS streaming). When testing locally, use:
# # # API_URL_LIVE = "http://localhost:8000/predict_emotion"
# # API_URL_LIVE = "http://localhost:8000/predict_emotion"
# # API_TIMEOUT = 7  # seconds
# # MAX_RETRIES = 3
# # RETRY_BACKOFF = 1.5

# # # Smoothing settings for manual capture
# # BUFFER_SIZE = 7
# # CONFIDENCE_THRESHOLD = 0.5

# # # ==========================================
# # THEME_MAP = {
# #     "happy": {"bg": "#fff8e1", "text": "#2b2b2b", "sidebar": "#fff3bf"},
# #     "surprise": {"bg": "#e0f7ff", "text": "#003355", "sidebar": "#b3ecff"},
# #     "sad": {"bg": "#e3f2fd", "text": "#0d47a1", "sidebar": "#bbdefb"},
# #     "angry": {"bg": "#ffebee", "text": "#b71c1c", "sidebar": "#ffcdd2"},
# #     "neutral": {"bg": "#ffffff", "text": "#0f172a", "sidebar": "#f1f5f9"},
# #     "tired": {"bg": "#f3e5f5", "text": "#4a148c", "sidebar": "#e1bee7"},
# #     "fear": {"bg": "#f1f8e9", "text": "#33691e", "sidebar": "#dcedc8"},
# #     "disgust": {"bg": "#f9fbe7", "text": "#827717", "sidebar": "#f0f4c3"},
# # }

# # # -------- Helper functions --------
# # def _try_request(method, url, **kwargs):
# #     for attempt in range(MAX_RETRIES):
# #         try:
# #             return requests.request(method, url, timeout=API_TIMEOUT, **kwargs)
# #         except Exception as e:
# #             if attempt == MAX_RETRIES - 1:
# #                 raise e
# #             time.sleep(RETRY_BACKOFF ** attempt)


# # def try_post_image(api_url, image_bytes: bytes):
# #     """
# #     Post the RAW image bytes to the backend as multipart 'file'.
# #     Backend will do preprocessing itself.
# #     """
# #     files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
# #     return _try_request("POST", api_url, files=files)


# # def probe_api_with_fallbacks(base_url: str):
# #     """
# #     Try a small set of hostnames (container name, localhost, 127.0.0.1) to find a reachable URL.
# #     Returns the first working full URL.
# #     """
# #     parsed = urlparse(base_url)
# #     hostname = parsed.hostname or "localhost"
# #     port = parsed.port or (443 if parsed.scheme == "https" else 80)
# #     candidates = [hostname, "127.0.0.1", "localhost", "inference"]
# #     for host in candidates:
# #         new_netloc = f"{host}:{port}"
# #         new_url = urlunparse(parsed._replace(netloc=new_netloc))
# #         try:
# #             # quick TCP connect test
# #             with socket.create_connection((host, port), timeout=1):
# #                 # try GET (health)
# #                 resp = _try_request("GET", new_url)
# #                 if resp.status_code < 500:
# #                     return new_url
# #         except Exception:
# #             continue
# #     raise ConnectionError("No reachable backend host found")


# # def send_image_bytes_and_get_mood(image_bytes: bytes):
# #     """
# #     Send raw bytes to backend and parse JSON response.
# #     Returns (emotion_label, meta_dict)
# #     """
# #     try:
# #         target_url = probe_api_with_fallbacks(API_URL)
# #         resp = try_post_image(target_url, image_bytes)
# #         if resp.status_code == 200:
# #             data = resp.json()
# #             emotion = data.get("emotion", "neutral")
# #             return emotion, data
# #         return "neutral", {"error": f"Bad status: {resp.status_code}", "text": resp.text}
# #     except Exception as e:
# #         return "neutral", {"error": str(e), "trace": traceback.format_exc()}


# # # ---------- Browser-side live camera streaming component ----------
# # def render_live_camera_sender(api_url: str, interval_seconds: int = 5, width: int = 640, height: int = 480):
# #     # Build HTML as a plain string and substitute placeholders to avoid Python f-string brace issues
# #     template = """
# #     <div style='font-family: Arial; border:1px solid #ccc; padding:10px; border-radius:8px; background:#0f1724; color:#e6eef8'>
# #       <div id='status'>Status: <b>idle</b></div>
# #       <video id='cam' autoplay playsinline width='<<WIDTH>>' height='<<HEIGHT>>' style='border-radius:6px; border:1px solid #999;'></video>
# #       <canvas id='snap' width='<<WIDTH>>' height='<<HEIGHT>>' style='display:none;'></canvas>
# #       <div style='margin-top:8px;'>
# #         <input id='interval' type='number' value='<<INTERVAL>>' min='1' style='width:80px;'> seconds
# #         <button id='startBtn'>Start Streaming</button>
# #         <button id='stopBtn' disabled>Stop</button>
# #       </div>
# #       <pre id='lastResp' style='background:#111827; color:#d1d5db; border:1px solid #374151; padding:6px; max-height:120px; overflow:auto; white-space:pre-wrap;'></pre>
# #       <div style='font-size:12px; color:#9ca3af; margin-top:6px;'>Notes: Browser will ask for camera permission. API must allow CORS for this origin.</div>
# #     </div>

# #     <script>
# #     const apiUrl = <<API_URL_JS>>;
# #     let stream=null, timer=null;
# #     const vid=document.getElementById('cam');
# #     const canvas=document.getElementById('snap');
# #     const statusEl=document.getElementById('status');
# #     const respEl=document.getElementById('lastResp');
    

# #     async function startCamera(){
# #       try{
# #         stream=await navigator.mediaDevices.getUserMedia({video:{ facingMode: "user" }, audio:false});
# #         vid.srcObject=stream;
# #         return true;
# #       }catch(e){
# #         statusEl.innerHTML='Status: <b style="color:tomato">Camera blocked or unavailable</b>';
# #         console.error('getUserMedia failed', e);
# #         return false;
# #       }
# #     }

# #     function captureFrame(){
# #       const ctx=canvas.getContext('2d');
# #       ctx.drawImage(vid,0,0,canvas.width,canvas.height);
# #       return new Promise(r=>canvas.toBlob(b=>r(b),'image/jpeg',0.9));
# #     }

# #     async function sendFrame(){
# #       if(!stream) return;
# #       try{
# #         statusEl.innerHTML = 'Status: <b>capturing & sending to ' + apiUrl + '</b>';
# #         const blob = await captureFrame();
# #         const fd = new FormData();
# #         fd.append('file', blob, 'frame.jpg');
# #         const resp = await fetch(apiUrl, { method: 'POST', body: fd });
# #         const txt = await resp.text();
# #         respEl.textContent = 'HTTP ' + resp.status + '\\n' + txt;
# #         if (resp.ok) {
# #           statusEl.innerHTML = 'Status: <b style="color:lightgreen">sent</b>';
# #         } else {
# #           statusEl.innerHTML = 'Status: <b style="color:tomato">server error</b>';
# #         }
# #       }catch(e){
# #         statusEl.innerHTML = 'Status: <b style="color:tomato">network error</b>';
# #         respEl.textContent = 'Fetch error: ' + (e && e.message ? e.message : String(e));
# #         console.error('Fetch failed for', apiUrl, e);
# #       }
# #     }

# #     document.getElementById('startBtn').onclick = async ()=>{
# #       const ok = await startCamera();
# #       if(!ok) return;
# #       document.getElementById('startBtn').disabled = true;
# #       document.getElementById('stopBtn').disabled = false;
# #       const interval = parseInt(document.getElementById('interval').value) || 5;
# #       sendFrame();
# #       timer = setInterval(sendFrame, interval * 1000);
# #     };

# #     document.getElementById('stopBtn').onclick = ()=>{
# #       if(timer){ clearInterval(timer); timer = null; }
# #       if(stream){ stream.getTracks().forEach(t => t.stop()); stream = null; }
# #       document.getElementById('startBtn').disabled = false;
# #       document.getElementById('stopBtn').disabled = true;
# #       statusEl.innerHTML = 'Status: <b>stopped</b>';
# #     };
# #     </script>
# #     """
# #     html = template.replace("<<API_URL_JS>>", json.dumps(api_url)).replace("<<WIDTH>>", str(width)).replace("<<HEIGHT>>", str(height)).replace("<<INTERVAL>>", str(interval_seconds))
# #     components.html(html, height=height + 260, scrolling=True)


# # # ---------- Main render function ----------
# # def render():
# #     st.set_page_config(page_title="StudySense — Study Mode", layout="wide")
# #     st.title("📖 Study Mode")

# #     # session state
# #     if "privacy_accepted" not in st.session_state:
# #         st.session_state.privacy_accepted = False
# #     if "pred_buffer" not in st.session_state:
# #         st.session_state.pred_buffer = deque(maxlen=BUFFER_SIZE)
# #     if "current_emotion" not in st.session_state:
# #         st.session_state.current_emotion = "neutral"
# #     if "current_theme" not in st.session_state:
# #         st.session_state.current_theme = THEME_MAP["neutral"]
# #     if "last_auto_meta" not in st.session_state:
# #         st.session_state.last_auto_meta = {}

# #     # privacy
# #     if not st.session_state.privacy_accepted:
# #         st.warning(
# #             """
# #             **Privacy Notice**

# #             This feature will access your camera to analyze emotion for adaptive themes. The backend will process frames and decide the emotion. Please ensure you are comfortable before enabling.
# #             """
# #         )
# #         if st.button("✅ I Understand and Accept"):
# #             st.session_state.privacy_accepted = True
# #             st.rerun()
# #         return

# #     st.subheader("Camera Options")
# #     live = st.checkbox("Enable automatic camera streaming (requires CORS)", value=False)

# #     if live:
# #         st.info("Your browser will request camera permission and send frames automatically to the API.")
# #         render_live_camera_sender(API_URL_LIVE, interval_seconds=5)
# #     else:
# #         cam_img = st.camera_input("Capture image manually")
# #         if cam_img and st.button("Send to API"):
# #             img_bytes = cam_img.getvalue()
# #             # send raw bytes to backend (server will preprocess the image)
# #             mood, meta = send_image_bytes_and_get_mood(img_bytes)
# #             # smoothing: only add confident labels
# #             conf = meta.get("confidence", 0.0) if isinstance(meta, dict) else 0.0
# #             label = mood
# #             if conf > CONFIDENCE_THRESHOLD and label not in (None, "Error"):
# #                 st.session_state.pred_buffer.append(label)
# #             if len(st.session_state.pred_buffer) > 0:
# #                 vals, counts = np.unique(np.array(list(st.session_state.pred_buffer)), return_counts=True)
# #                 stable = vals[np.argmax(counts)]
# #             else:
# #                 stable = label
# #             st.session_state.current_emotion = stable
# #             st.session_state.current_theme = THEME_MAP.get(stable.lower(), THEME_MAP["neutral"]) if isinstance(stable, str) else THEME_MAP["neutral"]
# #             st.session_state.last_auto_meta = meta
# #             st.success(f"Detected emotion: {stable} (confidence: {meta.get('confidence')})")

# #     st.write("---")
# #     st.markdown(f"### Current Emotion: **{st.session_state.current_emotion}**")
# #     theme = st.session_state.current_theme
# #     st.markdown(f"<div style='background:{theme['bg']}; color:{theme['text']}; padding:10px; border-radius:8px;'>Sample Theme Area</div>", unsafe_allow_html=True)

# #     st.write("---")
# #     st.subheader("📄 Study Material")
# #     pdf_file = st.file_uploader("Upload a PDF", type="pdf")
# #     if pdf_file:
# #         st.success("PDF loaded successfully. Rendering below:")
# #         base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
# #         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
# #         st.markdown(pdf_display, unsafe_allow_html=True)

# #     with st.expander("Debug Info"):
# #         st.json(st.session_state.last_auto_meta)
# #         st.write({"buffer": list(st.session_state.pred_buffer)})


# # if __name__ == "__main__":
# #     render()


# # study_mode_dynamic_theme.py
# """
# Study Mode (dynamic theme) — Streamlit page
# - Applies dynamic theme changes by injecting CSS based on detected emotion
# - Supports manual capture (sends raw image to backend which performs preprocessing + inference)
# - Supports live streaming (browser->backend) and polls a /last_mood endpoint on the backend to pick up the latest mood

# Note: For live streaming to update the app theme automatically, the backend should expose a lightweight endpoint
# `/last_mood` that returns the most recent inference result:
#     {"emotion": "Happy", "confidence": 0.92, "meta": {...}}

# If your backend does not store the last mood, enable that behaviour (I can update the backend file too).
# """

# import streamlit as st
# import base64
# import time
# import requests
# import socket
# import traceback
# from datetime import datetime
# from urllib.parse import urlparse, urlunparse
# from io import BytesIO
# import streamlit.components.v1 as components
# import json
# import numpy as np
# from collections import deque
# from streamlit_autorefresh import st_autorefresh

# # ================= CONFIG =================
# # Inside Docker (server -> inference service)
# API_URL = "http://inference:8000/predict_emotion"
# # Browser-accessible endpoint (for live JS streaming). When testing locally, use:
# API_URL_LIVE = "http://localhost:8000/predict_emotion"
# API_TIMEOUT = 7  # seconds
# MAX_RETRIES = 3
# RETRY_BACKOFF = 1.5

# # Endpoint to poll for latest mood (backend must expose this)
# API_LAST_MOOD_PATH = "/last_mood"
# API_POLL_INTERVAL_SECONDS = 3  # how often Streamlit polls backend for latest mood when live is on

# # Smoothing settings for manual capture
# BUFFER_SIZE = 7
# CONFIDENCE_THRESHOLD = 0.5

# # ==========================================
# THEME_MAP = {
#     "happy": {"bg": "#fff8e1", "text": "#2b2b2b", "sidebar": "#fff3bf"},
#     "surprise": {"bg": "#e0f7ff", "text": "#003355", "sidebar": "#b3ecff"},
#     "sad": {"bg": "#e3f2fd", "text": "#0d47a1", "sidebar": "#bbdefb"},
#     "angry": {"bg": "#ffebee", "text": "#b71c1c", "sidebar": "#ffcdd2"},
#     "neutral": {"bg": "#ffffff", "text": "#0f172a", "sidebar": "#f1f5f9"},
#     "tired": {"bg": "#f3e5f5", "text": "#4a148c", "sidebar": "#e1bee7"},
#     "fear": {"bg": "#f1f8e9", "text": "#33691e", "sidebar": "#dcedc8"},
#     "disgust": {"bg": "#f9fbe7", "text": "#827717", "sidebar": "#f0f4c3"},
# }

# # -------- Helper functions (unchanged networking helpers) --------
# def _try_request(method, url, **kwargs):
#     for attempt in range(MAX_RETRIES):
#         try:
#             return requests.request(method, url, timeout=API_TIMEOUT, **kwargs)
#         except Exception as e:
#             if attempt == MAX_RETRIES - 1:
#                 raise e
#             time.sleep(RETRY_BACKOFF ** attempt)


# def try_post_image(api_url, image_bytes: bytes):
#     files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
#     return _try_request("POST", api_url, files=files)


# def probe_api_with_fallbacks(base_url: str):
#     parsed = urlparse(base_url)
#     hostname = parsed.hostname or "localhost"
#     port = parsed.port or (443 if parsed.scheme == "https" else 80)
#     candidates = [hostname, "127.0.0.1", "localhost", "inference"]
#     for host in candidates:
#         new_netloc = f"{host}:{port}"
#         new_url = urlunparse(parsed._replace(netloc=new_netloc))
#         try:
#             with socket.create_connection((host, port), timeout=1):
#                 resp = _try_request("GET", new_url)
#                 if resp.status_code < 500:
#                     return new_url
#         except Exception:
#             continue
#     raise ConnectionError("No reachable backend host found")


# def send_image_bytes_and_get_mood(image_bytes: bytes):
#     try:
#         target_url = probe_api_with_fallbacks(API_URL)
#         resp = try_post_image(target_url, image_bytes)
#         if resp.status_code == 200:
#             data = resp.json()
#             emotion = data.get("emotion", "neutral")
#             return emotion, data
#         return "neutral", {"error": f"Bad status: {resp.status_code}", "text": resp.text}
#     except Exception as e:
#         return "neutral", {"error": str(e), "trace": traceback.format_exc()}


# # ---------- Theme application (inject CSS) ----------

# def apply_theme(theme: dict):
#     """Inject CSS to approximate a theme change across the page.
#     Streamlit doesn't currently support swapping the full built-in theme at runtime,
#     so we inject CSS to mimic background, text and sidebar colors.
#     """
#     if not isinstance(theme, dict):
#         return
#     bg = theme.get("bg", "#ffffff")
#     text = theme.get("text", "#000000")
#     sidebar = theme.get("sidebar", bg)

#     css = f"""
#     <style>
#     /* App background */
#     .stApp {{ background-color: {bg} !important; color: {text} !important; }}
#     /* Markdown/text colors */
#     .stMarkdown, .stText, .stText p, .stMetric {{ color: {text} !important; }}
#     /* Sidebar */
#     .css-1d391kg, .css-1lcbmhc, .stSidebar {{ background-color: {sidebar} !important; }}
#     /* Cards and containers */
#     .stButton>button, .stDownloadButton>button {{ border-radius: 8px; }}
#     /* Small adjustments to ensure contrast */
#     .stApp .stButton>button, .stApp .stDownloadButton>button {{ color: {text} !important; }}
#     </style>
#     """
#     st.markdown(css, unsafe_allow_html=True)


# # ---------- Poll backend for last mood (used by live streaming flow) ----------

# def fetch_last_mood_from_backend():
#     """Attempts to fetch last mood from backend's /last_mood endpoint. Returns (emotion, meta) or (None, err).
#     Backend must support persisting the last inference and returning it at this path.
#     """
#     try:
#         base = probe_api_with_fallbacks(API_URL)
#         # replace predict path with last_mood path
#         if base.endswith('/predict_emotion'):
#             base = base.replace('/predict_emotion', API_LAST_MOOD_PATH)
#         else:
#             base = base.rstrip('/') + API_LAST_MOOD_PATH
#         resp = _try_request('GET', base)
#         if resp.status_code == 200:
#             j = resp.json()
#             emo = j.get('emotion') or j.get('mood') or None
#             return emo, j
#         return None, {'error': f'bad status {resp.status_code}', 'text': resp.text}
#     except Exception as e:
#         return None, {'error': str(e)}


# # ---------- Browser-side live camera streaming component (unchanged) ----------
# def render_live_camera_sender(api_url: str, interval_seconds: int = 5, width: int = 640, height: int = 480):
#     template = """
#     <div style='font-family: Arial; border:1px solid #ccc; padding:10px; border-radius:8px; background:#0f1724; color:#e6eef8'>
#       <div id='status'>Status: <b>idle</b></div>
#       <video id='cam' autoplay playsinline width='<<WIDTH>>' height='<<HEIGHT>>' style='border-radius:6px; border:1px solid #999;'></video>
#       <canvas id='snap' width='<<WIDTH>>' height='<<HEIGHT>>' style='display:none;'></canvas>
#       <div style='margin-top:8px;'>
#         <input id='interval' type='number' value='<<INTERVAL>>' min='1' style='width:80px;'> seconds
#         <button id='startBtn'>Start Streaming</button>
#         <button id='stopBtn' disabled>Stop</button>
#       </div>
#       <pre id='lastResp' style='background:#111827; color:#d1d5db; border:1px solid #374151; padding:6px; max-height:120px; overflow:auto; white-space:pre-wrap;'></pre>
#       <div style='font-size:12px; color:#9ca3af; margin-top:6px;'>Notes: Browser will ask for camera permission. API must allow CORS for this origin.</div>
#     </div>

#     <script>
#     const apiUrl = <<API_URL_JS>>;
#     let stream=null, timer=null;
#     const vid=document.getElementById('cam');
#     const canvas=document.getElementById('snap');
#     const statusEl=document.getElementById('status');
#     const respEl=document.getElementById('lastResp');

#     async function startCamera(){
#       try{
#         stream=await navigator.mediaDevices.getUserMedia({video:{ facingMode: "user" }, audio:false});
#         vid.srcObject=stream;
#         return true;
#       }catch(e){
#         statusEl.innerHTML='Status: <b style="color:tomato">Camera blocked or unavailable</b>';
#         console.error('getUserMedia failed', e);
#         return false;
#       }
#     }

#     function captureFrame(){
#       const ctx=canvas.getContext('2d');
#       ctx.drawImage(vid,0,0,canvas.width,canvas.height);
#       return new Promise(r=>canvas.toBlob(b=>r(b),'image/jpeg',0.9));
#     }

#     async function sendFrame(){
#       if(!stream) return;
#       try{
#         statusEl.innerHTML = 'Status: <b>capturing & sending to ' + apiUrl + '</b>';
#         const blob = await captureFrame();
#         const fd = new FormData();
#         fd.append('file', blob, 'frame.jpg');
#         const resp = await fetch(apiUrl, { method: 'POST', body: fd });
#         const txt = await resp.text();
#         respEl.textContent = 'HTTP ' + resp.status + '\\n' + txt;
#         if (resp.ok) {
#           statusEl.innerHTML = 'Status: <b style="color:lightgreen">sent</b>';
#         } else {
#           statusEl.innerHTML = 'Status: <b style="color:tomato">server error</b>';
#         }
#       }catch(e){
#         statusEl.innerHTML = 'Status: <b style="color:tomato">network error</b>';
#         respEl.textContent = 'Fetch error: ' + (e && e.message ? e.message : String(e));
#         console.error('Fetch failed for', apiUrl, e);
#       }
#     }

#     document.getElementById('startBtn').onclick = async ()=>{
#       const ok = await startCamera();
#       if(!ok) return;
#       document.getElementById('startBtn').disabled = true;
#       document.getElementById('stopBtn').disabled = false;
#       const interval = parseInt(document.getElementById('interval').value) || 5;
#       sendFrame();
#       timer = setInterval(sendFrame, interval * 1000);
#     };

#     document.getElementById('stopBtn').onclick = ()=>{
#       if(timer){ clearInterval(timer); timer = null; }
#       if(stream){ stream.getTracks().forEach(t => t.stop()); stream = null; }
#       document.getElementById('startBtn').disabled = false;
#       document.getElementById('stopBtn').disabled = true;
#       statusEl.innerHTML = 'Status: <b>stopped</b>';
#     };
#     </script>
#     """
#     html = template.replace("<<API_URL_JS>>", json.dumps(api_url)).replace("<<WIDTH>>", str(width)).replace("<<HEIGHT>>", str(height)).replace("<<INTERVAL>>", str(interval_seconds))
#     components.html(html, height=height + 260, scrolling=True)


# # ---------- Main render function ----------
# def render():
#     st.set_page_config(page_title="StudySense — Study Mode", layout="wide")
#     st.title("📖 Study Mode")

#     # session state
#     if "privacy_accepted" not in st.session_state:
#         st.session_state.privacy_accepted = False
#     if "pred_buffer" not in st.session_state:
#         st.session_state.pred_buffer = deque(maxlen=BUFFER_SIZE)
#     if "current_emotion" not in st.session_state:
#         st.session_state.current_emotion = "neutral"
#     if "current_theme" not in st.session_state:
#         st.session_state.current_theme = THEME_MAP["neutral"]
#     if "last_auto_meta" not in st.session_state:
#         st.session_state.last_auto_meta = {}

#     # privacy
#     if not st.session_state.privacy_accepted:
#         st.warning(
#             """
#             **Privacy Notice**

#             This feature will access your camera to analyze emotion for adaptive themes. The backend will process frames and decide the emotion. Please ensure you are comfortable before enabling.
#             """
#         )
#         if st.button("✅ I Understand and Accept"):
#             st.session_state.privacy_accepted = True
#             st.rerun()
#         return

#     st.subheader("Camera Options")
#     live = st.checkbox("Enable automatic camera streaming (requires CORS)", value=False)

#     if live:
#         st.info("Your browser will request camera permission and send frames automatically to the API.")
#         render_live_camera_sender(API_URL_LIVE, interval_seconds=5)

#         # Start a small poll loop using st_autorefresh to query backend's last mood
#         # The call below will refresh the page every API_POLL_INTERVAL_SECONDS * 1000 ms
#         st_autorefresh(interval=API_POLL_INTERVAL_SECONDS * 1000, key="live_poll")
#         # Attempt to fetch last mood; if found, update state and apply theme
#         emo, meta = fetch_last_mood_from_backend()
#         if emo:
#             st.session_state.current_emotion = emo
#             theme = THEME_MAP.get(emo.lower(), THEME_MAP["neutral"]) if isinstance(emo, str) else THEME_MAP["neutral"]
#             st.session_state.current_theme = theme
#             apply_theme(theme)
#             st.session_state.last_auto_meta = meta
#     else:
#         cam_img = st.camera_input("Capture image manually")
#         if cam_img and st.button("Send to API"):
#             img_bytes = cam_img.getvalue()
#             # send raw bytes to backend (server will preprocess the image)
#             mood, meta = send_image_bytes_and_get_mood(img_bytes)
#             # smoothing: only add confident labels
#             conf = meta.get("confidence", 0.0) if isinstance(meta, dict) else 0.0
#             label = mood
#             if conf > CONFIDENCE_THRESHOLD and label not in (None, "Error"):
#                 st.session_state.pred_buffer.append(label)
#             if len(st.session_state.pred_buffer) > 0:
#                 vals, counts = np.unique(np.array(list(st.session_state.pred_buffer)), return_counts=True)
#                 stable = vals[np.argmax(counts)]
#             else:
#                 stable = label
#             st.session_state.current_emotion = stable
#             theme = THEME_MAP.get(stable.lower(), THEME_MAP["neutral"]) if isinstance(stable, str) else THEME_MAP["neutral"]
#             st.session_state.current_theme = theme
#             apply_theme(theme)
#             st.session_state.last_auto_meta = meta
#             st.success(f"Detected emotion: {stable} (confidence: {meta.get('confidence')})")

#     st.write("---")
#     st.markdown(f"### Current Emotion: **{st.session_state.current_emotion}**")
#     theme = st.session_state.current_theme
#     st.markdown(f"<div style='background:{theme['bg']}; color:{theme['text']}; padding:10px; border-radius:8px;'>Sample Theme Area</div>", unsafe_allow_html=True)

#     st.write("---")
#     st.subheader("📄 Study Material")
#     pdf_file = st.file_uploader("Upload a PDF", type="pdf")
#     if pdf_file:
#         st.success("PDF loaded successfully. Rendering below:")
#         base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
#         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
#         st.markdown(pdf_display, unsafe_allow_html=True)

#     with st.expander("Debug Info"):
#         st.json(st.session_state.last_auto_meta)
#         st.write({"buffer": list(st.session_state.pred_buffer)})


# if __name__ == "__main__":
#     render()


# study_mode_dynamic_theme.py
"""
Study Mode (dynamic theme) — Streamlit page
- Applies dynamic theme changes by injecting CSS based on detected emotion
- Supports manual capture (sends raw image to backend which performs preprocessing + inference)
- Supports live streaming (browser->backend) and polls a /last_mood endpoint on the backend to pick up the latest mood

Note: For live streaming to update the app theme automatically, the backend should expose a lightweight endpoint
`/last_mood` that returns the most recent inference result:
    {"emotion": "Happy", "confidence": 0.92, "meta": {...}}

If your backend does not store the last mood, enable that behaviour (I can update the backend file too).
"""

import streamlit as st
import base64
import time
import requests
import socket
import traceback
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from io import BytesIO
import streamlit.components.v1 as components
import json
import numpy as np
from collections import deque
from streamlit_autorefresh import st_autorefresh

# ================= CONFIG =================
# Inside Docker (server -> inference service)
API_URL = "http://inference:8000/predict_emotion"
# Browser-accessible endpoint (for live JS streaming). When testing locally, use:
API_URL_LIVE = "http://localhost:8000/predict_emotion"
API_TIMEOUT = 7  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF = 1.5

# Endpoint to poll for latest mood (backend must expose this)
API_LAST_MOOD_PATH = "/last_mood"
API_POLL_INTERVAL_SECONDS = 3  # how often Streamlit polls backend for latest mood when live is on

# Smoothing settings for manual capture
BUFFER_SIZE = 7
CONFIDENCE_THRESHOLD = 0.5

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

# -------- Helper functions (unchanged networking helpers) --------
def _try_request(method, url, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return requests.request(method, url, timeout=API_TIMEOUT, **kwargs)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise e
            time.sleep(RETRY_BACKOFF ** attempt)


def try_post_image(api_url, image_bytes: bytes):
    files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
    return _try_request("POST", api_url, files=files)


def probe_api_with_fallbacks(base_url: str):
    parsed = urlparse(base_url)
    hostname = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    candidates = [hostname, "127.0.0.1", "localhost", "inference"]
    for host in candidates:
        new_netloc = f"{host}:{port}"
        new_url = urlunparse(parsed._replace(netloc=new_netloc))
        try:
            with socket.create_connection((host, port), timeout=1):
                resp = _try_request("GET", new_url)
                if resp.status_code < 500:
                    return new_url
        except Exception:
            continue
    raise ConnectionError("No reachable backend host found")


def send_image_bytes_and_get_mood(image_bytes: bytes):
    try:
        target_url = probe_api_with_fallbacks(API_URL)
        resp = try_post_image(target_url, image_bytes)
        if resp.status_code == 200:
            data = resp.json()
            emotion = data.get("emotion", "neutral")
            return emotion, data
        return "neutral", {"error": f"Bad status: {resp.status_code}", "text": resp.text}
    except Exception as e:
        return "neutral", {"error": str(e), "trace": traceback.format_exc()}


# ---------- Theme application (inject CSS) ----------

def apply_theme(theme: dict):
    """Inject CSS to approximate a theme change across the page.
    Streamlit doesn't currently support swapping the full built-in theme at runtime,
    so we inject CSS to mimic background, text and sidebar colors.
    """
    if not isinstance(theme, dict):
        return
    bg = theme.get("bg", "#ffffff")
    text = theme.get("text", "#000000")
    sidebar = theme.get("sidebar", bg)

    css = f"""
    <style>
    /* App background */
    .stApp {{ background-color: {bg} !important; color: {text} !important; }}
    /* Markdown/text colors */
    .stMarkdown, .stText, .stText p, .stMetric {{ color: {text} !important; }}
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc, .stSidebar {{ background-color: {sidebar} !important; }}
    /* Cards and containers */
    .stButton>button, .stDownloadButton>button {{ border-radius: 8px; }}
    /* Small adjustments to ensure contrast */
    .stApp .stButton>button, .stApp .stDownloadButton>button {{ color: {text} !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ---------- Poll backend for last mood (used by live streaming flow) ----------

def fetch_last_mood_from_backend():
    """Attempts to fetch last mood from backend's /last_mood endpoint. Returns (emotion, meta) or (None, err).
    Backend must support persisting the last inference and returning it at this path.
    """
    try:
        base = probe_api_with_fallbacks(API_URL)
        # replace predict path with last_mood path
        if base.endswith('/predict_emotion'):
            base = base.replace('/predict_emotion', API_LAST_MOOD_PATH)
        else:
            base = base.rstrip('/') + API_LAST_MOOD_PATH
        resp = _try_request('GET', base)
        if resp.status_code == 200:
            j = resp.json()
            emo = j.get('emotion') or j.get('mood') or None
            return emo, j
        return None, {'error': f'bad status {resp.status_code}', 'text': resp.text}
    except Exception as e:
        return None, {'error': str(e)}


# ---------- Browser-side live camera streaming component (unchanged) ----------
def render_live_camera_sender(api_url: str, interval_seconds: int = 5, width: int = 640, height: int = 480):
    template = """
    <div style='font-family: Arial; border:1px solid #ccc; padding:10px; border-radius:8px; background:#0f1724; color:#e6eef8'>
      <div id='status'>Status: <b>idle</b></div>
      <video id='cam' autoplay playsinline width='<<WIDTH>>' height='<<HEIGHT>>' style='border-radius:6px; border:1px solid #999;'></video>
      <canvas id='snap' width='<<WIDTH>>' height='<<HEIGHT>>' style='display:none;'></canvas>
      <div style='margin-top:8px;'>
        <input id='interval' type='number' value='<<INTERVAL>>' min='1' style='width:80px;'> seconds
        <button id='startBtn'>Start Streaming</button>
        <button id='stopBtn' disabled>Stop</button>
      </div>
      <pre id='lastResp' style='background:#111827; color:#d1d5db; border:1px solid #374151; padding:6px; max-height:120px; overflow:auto; white-space:pre-wrap;'></pre>
      <div style='font-size:12px; color:#9ca3af; margin-top:6px;'>Notes: Browser will ask for camera permission. API must allow CORS for this origin.</div>
    </div>

    <script>
    const apiUrl = <<API_URL_JS>>;
    let stream=null, timer=null;
    const vid=document.getElementById('cam');
    const canvas=document.getElementById('snap');
    const statusEl=document.getElementById('status');
    const respEl=document.getElementById('lastResp');

    async function startCamera(){
      try{
        stream=await navigator.mediaDevices.getUserMedia({video:{ facingMode: "user" }, audio:false});
        vid.srcObject=stream;
        return true;
      }catch(e){
        statusEl.innerHTML='Status: <b style="color:tomato">Camera blocked or unavailable</b>';
        console.error('getUserMedia failed', e);
        return false;
      }
    }

    function captureFrame(){
      const ctx=canvas.getContext('2d');
      ctx.drawImage(vid,0,0,canvas.width,canvas.height);
      return new Promise(r=>canvas.toBlob(b=>r(b),'image/jpeg',0.9));
    }

    async function sendFrame(){
      if(!stream) return;
      try{
        statusEl.innerHTML = 'Status: <b>capturing & sending to ' + apiUrl + '</b>';
        const blob = await captureFrame();
        const fd = new FormData();
        fd.append('file', blob, 'frame.jpg');
        const resp = await fetch(apiUrl, { method: 'POST', body: fd });
        const txt = await resp.text();
        respEl.textContent = 'HTTP ' + resp.status + '\\n' + txt;
        if (resp.ok) {
          statusEl.innerHTML = 'Status: <b style="color:lightgreen">sent</b>';
        } else {
          statusEl.innerHTML = 'Status: <b style="color:tomato">server error</b>';
        }
      }catch(e){
        statusEl.innerHTML = 'Status: <b style="color:tomato">network error</b>';
        respEl.textContent = 'Fetch error: ' + (e && e.message ? e.message : String(e));
        console.error('Fetch failed for', apiUrl, e);
      }
    }

    document.getElementById('startBtn').onclick = async ()=>{
      const ok = await startCamera();
      if(!ok) return;
      document.getElementById('startBtn').disabled = true;
      document.getElementById('stopBtn').disabled = false;
      const interval = parseInt(document.getElementById('interval').value) || 5;
      sendFrame();
      timer = setInterval(sendFrame, interval * 1000);
    };

    document.getElementById('stopBtn').onclick = ()=>{
      if(timer){ clearInterval(timer); timer = null; }
      if(stream){ stream.getTracks().forEach(t => t.stop()); stream = null; }
      document.getElementById('startBtn').disabled = false;
      document.getElementById('stopBtn').disabled = true;
      statusEl.innerHTML = 'Status: <b>stopped</b>';
    };
    </script>
    """
    html = template.replace("<<API_URL_JS>>", json.dumps(api_url)).replace("<<WIDTH>>", str(width)).replace("<<HEIGHT>>", str(height)).replace("<<INTERVAL>>", str(interval_seconds))
    components.html(html, height=height + 260, scrolling=True)


# ---------- Main render function ----------
def render():
    st.set_page_config(page_title="StudySense — Study Mode", layout="wide")
    st.title("📖 Study Mode")

    # session state
    if "privacy_accepted" not in st.session_state:
        st.session_state.privacy_accepted = False
    if "pred_buffer" not in st.session_state:
        st.session_state.pred_buffer = deque(maxlen=BUFFER_SIZE)
    if "current_emotion" not in st.session_state:
        st.session_state.current_emotion = "neutral"
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = THEME_MAP["neutral"]
    if "last_auto_meta" not in st.session_state:
        st.session_state.last_auto_meta = {}

    # privacy
    if not st.session_state.privacy_accepted:
        st.warning(
            """
            **Privacy Notice**

            This feature will access your camera to analyze emotion for adaptive themes. The backend will process frames and decide the emotion. Please ensure you are comfortable before enabling.
            """
        )
        if st.button("✅ I Understand and Accept"):
            st.session_state.privacy_accepted = True
            st.rerun()
        return

    st.subheader("Camera Options")
    live = st.checkbox("Enable automatic camera streaming (requires CORS)", value=False)

    if live:
        st.info("Your browser will request camera permission and send frames automatically to the API.")
        render_live_camera_sender(API_URL_LIVE, interval_seconds=5)

        # Start a small poll loop using st_autorefresh to query backend's last mood
        # The call below will refresh the page every API_POLL_INTERVAL_SECONDS * 1000 ms
        st_autorefresh(interval=API_POLL_INTERVAL_SECONDS * 1000, key="live_poll")
        # Attempt to fetch last mood; if found, update state and apply theme
        emo, meta = fetch_last_mood_from_backend()
        if emo:
            st.session_state.current_emotion = emo
            theme = THEME_MAP.get(emo.lower(), THEME_MAP["neutral"]) if isinstance(emo, str) else THEME_MAP["neutral"]
            st.session_state.current_theme = theme
            apply_theme(theme)
            st.session_state.last_auto_meta = meta
    else:
        cam_img = st.camera_input("Capture image manually")
        if cam_img and st.button("Send to API"):
            img_bytes = cam_img.getvalue()
            # send raw bytes to backend (server will preprocess the image)
            mood, meta = send_image_bytes_and_get_mood(img_bytes)
            # smoothing: only add confident labels
            conf = meta.get("confidence", 0.0) if isinstance(meta, dict) else 0.0
            label = mood
            if conf > CONFIDENCE_THRESHOLD and label not in (None, "Error"):
                st.session_state.pred_buffer.append(label)
            if len(st.session_state.pred_buffer) > 0:
                vals, counts = np.unique(np.array(list(st.session_state.pred_buffer)), return_counts=True)
                stable = vals[np.argmax(counts)]
            else:
                stable = label
            st.session_state.current_emotion = stable
            theme = THEME_MAP.get(stable.lower(), THEME_MAP["neutral"]) if isinstance(stable, str) else THEME_MAP["neutral"]
            st.session_state.current_theme = theme
            apply_theme(theme)
            st.session_state.last_auto_meta = meta
            st.success(f"Detected emotion: {stable} (confidence: {meta.get('confidence')})")

    st.write("---")
    st.markdown(f"### Current Emotion: **{st.session_state.current_emotion}**")
    theme = st.session_state.current_theme
    st.markdown(f"<div style='background:{theme['bg']}; color:{theme['text']}; padding:10px; border-radius:8px;'>Sample Theme Area</div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("📄 Study Material")
    pdf_file = st.file_uploader("Upload a PDF", type="pdf")
    if pdf_file:
        st.success("PDF loaded successfully. Rendering below:")
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

    with st.expander("Debug Info"):
        st.json(st.session_state.last_auto_meta)
        st.write({"buffer": list(st.session_state.pred_buffer)})


if __name__ == "__main__":
    render()
