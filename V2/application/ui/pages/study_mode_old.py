# import streamlit as st
# import base64
# from core.decision_engine import DecisionEngine
# from streamlit_autorefresh import st_autorefresh
# # import study_mode_camera.py.attach_camera_to_study_mode as attach_camera_to_study_mode
# # attach_camera_to_study_mode() 

# def render():
#     st.title("📖 Study Mode")

#     if "privacy_accepted" not in st.session_state:
#         st.session_state.privacy_accepted = False
#     if "camera_verified" not in st.session_state:
#         st.session_state.camera_verified = False
#     if "current_mood" not in st.session_state:
#         st.session_state.current_mood = "neutral"

#     # Step 1: Privacy notice
#     if not st.session_state.privacy_accepted:
#         st.warning("""
#         **Privacy Notice**

#         This feature may temporarily access your webcam and local files to analyze focus levels.
#         No data is stored or shared externally.
#         """)
#         if st.button("✅ I Understand and Accept"):
#             st.session_state.privacy_accepted = True
#             st.rerun()
#         return

#     # Step 2: Camera check
#     if not st.session_state.camera_verified:
#         with st.expander("🎥 Camera Permission Test"):
#             st.info("Take a snapshot to verify camera access.")
#             img = st.camera_input("Camera Test")
#             if img:
#                 st.session_state.camera_verified = True
#                 st.success("✅ Camera access granted!")
#                 st.rerun()
#         return

#     # Step 3: Poll mood every 15s
#     st_autorefresh(interval=15 * 1000, key="mood_poll_refresh")

#     engine = DecisionEngine()
#     mood = engine.get_mood()
#     st.session_state.current_mood = mood
#     theme = engine.get_theme(mood)

#     # Apply dynamic theme
#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-color: {theme['bg']} !important;
#             color: {theme['text']} !important;
#             transition: background-color 1s ease, color 1s ease;
#         }}
#         .stSidebar {{
#             background-color: {theme['sidebar']} !important;
#             transition: background-color 1s ease;
#         }}
#         h1, h2, h3, h4, h5, h6, p, span {{
#             color: {theme['text']} !important;
#         }}
#         </style>
#         """,
#         unsafe_allow_html=True
#     )

#     st.markdown(
#         f"""
#         <div style="padding: 15px; border-radius: 10px;
#                     background-color:{theme['sidebar']};
#                     color:{theme['text']};
#                     text-align:center;">
#             <h4>🧠 Current Mood: <b>{mood.upper()}</b></h4>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     st.write("---")
#     uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
#     if uploaded_file:
#         st.write(f"### 📘 Uploaded File: **{uploaded_file.name}**")
#         base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
#         st.markdown(
#             f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px"></iframe>',
#             unsafe_allow_html=True
#         )
#     else:
#         st.info("Upload a PDF to start reading.")

#     st.caption("🔄 Theme automatically updates every 15 seconds based on detected mood.")


# import streamlit as st
# import base64
# import time
# import requests
# import socket
# import traceback
# from datetime import datetime
# from urllib.parse import urlparse, urlunparse
# from io import BytesIO
# from streamlit_autorefresh import st_autorefresh

# # ================= Configuration =================
# API_URL = "http://127.0.0.1:8000/predict_emotion"  # your endpoint
# API_TIMEOUT = 7
# MOOD_POLL_INTERVAL_SECONDS = 5 * 60
# # =================================================

# # ---------- Theme mapping ----------
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

# # ---------- Utilities ----------
# def check_tcp_connect(host: str, port: int, timeout: float = 2.0) -> bool:
#     try:
#         with socket.create_connection((host, port), timeout=timeout):
#             return True
#     except Exception:
#         return False

# def get_reachable_url():
#     """Return a reachable URL among docker/host variations."""
#     parsed = urlparse(API_URL)
#     base_path = parsed.path
#     for host in ["127.0.0.1", "host.docker.internal", "172.17.0.1", "172.18.0.1"]:
#         test_url = f"http://{host}:{parsed.port or 8000}{base_path}"
#         if check_tcp_connect(host, parsed.port or 8000):
#             return test_url
#     return API_URL

# def post_snapshot(img_bytes: bytes):
#     """Send the snapshot to the inference API and return emotion result."""
#     try:
#         url = get_reachable_url()
#         files = {"file": ("frame.jpg", img_bytes, "image/jpeg")}
#         resp = requests.post(url, files=files, timeout=API_TIMEOUT)
#         resp.raise_for_status()
#         return resp.json()
#     except Exception as e:
#         st.error(f"❌ API error: {e}")
#         return None

# def map_emotion_to_theme(emotion: str):
#     """Normalize emotion text and map to theme."""
#     if not emotion:
#         return THEME_MAP["neutral"]
#     emotion = emotion.strip().lower()
#     return THEME_MAP.get(emotion, THEME_MAP["neutral"])

# # ---------- UI ----------
# def render():
#     st.title("📖 Study Mode")

#     if "current_emotion" not in st.session_state:
#         st.session_state.current_emotion = "neutral"
#     if "current_theme" not in st.session_state:
#         st.session_state.current_theme = THEME_MAP["neutral"]
#     if "last_check" not in st.session_state:
#         st.session_state.last_check = None

#     st_autorefresh(interval=MOOD_POLL_INTERVAL_SECONDS * 1000, key="auto_refresh")

#     # --- Take snapshot ---
#     with st.expander("🎥 Take or upload a snapshot for mood detection", expanded=True):
#         img = st.camera_input("Take snapshot")
#         uploaded_img = st.file_uploader("Or upload image", type=["jpg", "jpeg", "png"])
#         if st.button("📡 Detect Mood"):
#             if img or uploaded_img:
#                 file = img or uploaded_img
#                 result = post_snapshot(file.getvalue())
#                 if result:
#                     emotion = result.get("emotion") or result.get("mood") or "neutral"
#                     conf = result.get("confidence", 0)
#                     theme = map_emotion_to_theme(emotion)
#                     st.session_state.current_emotion = emotion
#                     st.session_state.current_theme = theme
#                     st.session_state.last_check = datetime.utcnow()

#                     st.success(f"Detected emotion: **{emotion.upper()}** (confidence: {conf:.2f})")
#                 else:
#                     st.error("Could not detect mood.")
#             else:
#                 st.warning("Please take or upload an image first.")

#     # --- Apply theme ---
#     theme = st.session_state.current_theme
#     emotion = st.session_state.current_emotion
#     st.markdown(
#         f"""
#         <style>
#         .stApp {{
#             background-color: {theme['bg']} !important;
#             color: {theme['text']} !important;
#             transition: background-color 1s ease, color 1s ease;
#         }}
#         .stSidebar {{
#             background-color: {theme['sidebar']} !important;
#         }}
#         h1,h2,h3,h4,h5,h6,p,span {{ color: {theme['text']} !important; }}
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

#     # --- Display current mood ---
#     st.markdown(
#         f"""
#         <div style="padding: 15px; border-radius: 10px;
#                     background-color:{theme['sidebar']};
#                     color:{theme['text']};
#                     text-align:center;">
#             <h4>🧠 Current Emotion: <b>{emotion.upper()}</b></h4>
#             <small>Last checked: {st.session_state.last_check.strftime('%Y-%m-%d %H:%M:%S UTC') if st.session_state.last_check else 'N/A'}</small>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     # --- PDF viewer ---
#     st.write("---")
#     uploaded_file = st.file_uploader("📄 Upload a PDF to read", type=["pdf"])
#     if uploaded_file:
#         st.write(f"### 📘 {uploaded_file.name}")
#         base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
#         st.markdown(
#             f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px"></iframe>',
#             unsafe_allow_html=True,
#         )
#     else:
#         st.info("Upload a PDF to start reading.")

#     st.caption("Theme updates based on detected emotion (auto every 5 min).")

# if __name__ == "__main__":
#     render()


# study_mode.py
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

# ================= CONFIG =================
API_URL = "http://127.0.0.1:8000/predict_emotion"  # your endpoint
API_TIMEOUT = 7  # seconds
MOOD_POLL_INTERVAL_SECONDS = 5 * 60  # 5 minutes
MAX_RETRIES = 3
RETRY_BACKOFF = 1.5
# ==========================================

# ---------- Theme mapping ----------
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
# -----------------------------------

# ---------- Networking utils ----------
def check_tcp_connect(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def _build_url_with_host(original_url: str, host: str) -> str:
    parsed = urlparse(original_url)
    netloc = f"{host}:{parsed.port}" if parsed.port else host
    new_parsed = parsed._replace(netloc=netloc)
    return urlunparse(new_parsed)

def find_reachable_host_candidates(original_url: str):
    parsed = urlparse(original_url)
    orig_host = parsed.hostname or "127.0.0.1"
    orig_port = parsed.port or (443 if parsed.scheme == "https" else 80)

    # Common candidates: host.docker.internal and various docker bridge addresses
    candidates = [(orig_host, orig_port),
                  ("host.docker.internal", orig_port),
                  ("172.17.0.1", orig_port),
                  ("172.18.0.1", orig_port)]

    # try to discover local outbound IP (best-effort)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        candidates.append((local_ip, orig_port))
    except Exception:
        pass

    debug_attempts = []
    selected = None
    for host, port in candidates:
        reachable = check_tcp_connect(host, port, timeout=1.0)
        debug_attempts.append((host, port, reachable))
        if reachable and selected is None:
            selected = (host, port)
    if selected:
        sel_host, sel_port = selected
        selected_url = _build_url_with_host(original_url, sel_host)
        return selected_url, sel_host, sel_port, debug_attempts
    else:
        return None, None, None, debug_attempts

# ---------- HTTP helpers ----------
def _try_request(session, url, method="GET", timeout=API_TIMEOUT):
    try:
        if method == "GET":
            resp = session.get(url, timeout=timeout)
        elif method == "POST":
            resp = session.post(url, json={}, timeout=timeout, headers={"Content-Type": "application/json"})
        else:
            raise ValueError("Unsupported method")
        resp.raise_for_status()
        return True, resp
    except Exception as e:
        return False, e

def try_post_image(session, url, img_bytes: bytes, fname="frame.jpg"):
    try:
        files = {"file": (fname, img_bytes, "image/jpeg")}
        resp = session.post(url, files=files, timeout=API_TIMEOUT)
        resp.raise_for_status()
        return True, resp
    except Exception as e:
        return False, e

# ---------- Probe / image senders ----------
def probe_api_with_fallbacks():
    """Lightweight probe: tries reachable hosts, GET then POST(empty) — returns structured dict."""
    result = {
        "mood": "neutral",
        "theme": THEME_MAP["neutral"],
        "meta": {
            "configured_url": API_URL,
            "used_url": None,
            "tcp_ok": None,
            "host_attempts": [],
            "method_tried": None,
            "attempts": 0,
            "http_status": None,
            "raw_response": None,
            "error": None,
            "traceback": None,
        },
    }

    parsed = urlparse(API_URL)
    orig_host = parsed.hostname or "127.0.0.1"
    orig_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    tcp_ok = check_tcp_connect(orig_host, orig_port, timeout=1.0)
    result["meta"]["tcp_ok"] = tcp_ok

    if not tcp_ok:
        selected_url, sel_host, sel_port, debug_attempts = find_reachable_host_candidates(API_URL)
        result["meta"]["host_attempts"] = [{"host":h,"port":p,"reachable":r} for (h,p,r) in debug_attempts]
        if selected_url:
            request_url = selected_url
            result["meta"]["used_url"] = selected_url
        else:
            result["meta"]["error"] = f"TCP unreachable for all tried hosts: {result['meta']['host_attempts']}"
            return result
    else:
        request_url = API_URL
        result["meta"]["used_url"] = API_URL

    session = requests.Session()
    backoff = 1.0
    last_exc = None
    for attempt in range(1, MAX_RETRIES+1):
        ok, resp_or_exc = _try_request(session, request_url, method="GET")
        result["meta"]["attempts"] = attempt
        result["meta"]["method_tried"] = "GET"
        if ok:
            resp = resp_or_exc
            result["meta"]["http_status"] = resp.status_code
            try:
                data = resp.json()
            except Exception:
                data = resp.text
            result["meta"]["raw_response"] = data
            if isinstance(data, dict):
                # Accept both 'emotion' and 'mood'
                emotion = data.get("emotion") or data.get("mood") or data.get("current_mood")
                theme = data.get("theme")
                if emotion:
                    result["mood"] = emotion.lower()
                    result["theme"] = theme if isinstance(theme, dict) and all(k in theme for k in ("bg","text","sidebar")) else THEME_MAP.get(result["mood"], THEME_MAP["neutral"])
                    return result
            # else return raw for debugging
            result["meta"]["error"] = "GET succeeded but response did not contain 'emotion'/'mood'."
            return result
        else:
            exc = resp_or_exc
            last_exc = exc
            sc = None
            if hasattr(exc, "response") and exc.response is not None:
                sc = getattr(exc.response, "status_code", None)
            if sc == 405 or "405" in str(exc):
                okp, resp_or_excp = _try_request(session, request_url, method="POST")
                result["meta"]["method_tried"] = "POST (fallback from 405)"
                if okp:
                    resp = resp_or_excp
                    result["meta"]["http_status"] = resp.status_code
                    try:
                        data = resp.json()
                    except Exception:
                        data = resp.text
                    result["meta"]["raw_response"] = data
                    if isinstance(data, dict):
                        emotion = data.get("emotion") or data.get("mood") or data.get("current_mood")
                        theme = data.get("theme")
                        if emotion:
                            result["mood"] = emotion.lower()
                            result["theme"] = theme if isinstance(theme, dict) and all(k in theme for k in ("bg","text","sidebar")) else THEME_MAP.get(result["mood"], THEME_MAP["neutral"])
                            return result
                    result["meta"]["error"] = "POST succeeded but response did not contain 'emotion'/'mood'."
                    return result
            st.warning(f"Attempt {attempt}/{MAX_RETRIES} failed: {str(exc)}")
            time.sleep(backoff)
            backoff *= RETRY_BACKOFF

    result["meta"]["error"] = repr(last_exc)
    result["meta"]["traceback"] = traceback.format_exc()
    return result

def send_image_bytes_and_get_mood(img_bytes: bytes):
    """POST image as multipart/form-data (field name 'file')."""
    result = {
        "mood": "neutral",
        "theme": THEME_MAP["neutral"],
        "meta": {
            "configured_url": API_URL,
            "used_url": None,
            "tcp_ok": None,
            "host_attempts": [],
            "method_tried": "POST (image)",
            "attempts": 0,
            "http_status": None,
            "raw_response": None,
            "error": None,
            "traceback": None,
        },
    }

    parsed = urlparse(API_URL)
    orig_host = parsed.hostname or "127.0.0.1"
    orig_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    tcp_ok = check_tcp_connect(orig_host, orig_port, timeout=1.0)
    result["meta"]["tcp_ok"] = tcp_ok

    if not tcp_ok:
        selected_url, sel_host, sel_port, debug_attempts = find_reachable_host_candidates(API_URL)
        result["meta"]["host_attempts"] = [{"host":h,"port":p,"reachable":r} for (h,p,r) in debug_attempts]
        if selected_url:
            request_url = selected_url
            result["meta"]["used_url"] = selected_url
        else:
            result["meta"]["error"] = f"TCP unreachable for hosts tried: {result['meta']['host_attempts']}"
            return result
    else:
        request_url = API_URL
        result["meta"]["used_url"] = API_URL

    session = requests.Session()
    ok, resp_or_exc = try_post_image(session, request_url, img_bytes)
    if ok:
        resp = resp_or_exc
        result["meta"]["http_status"] = resp.status_code
        try:
            data = resp.json()
        except Exception:
            data = resp.text
        result["meta"]["raw_response"] = data
        if isinstance(data, dict):
            emotion = data.get("emotion") or data.get("mood") or data.get("current_mood")
            theme = data.get("theme")
            if emotion:
                result["mood"] = emotion.lower()
                result["theme"] = theme if isinstance(theme, dict) and all(k in theme for k in ("bg","text","sidebar")) else THEME_MAP.get(result["mood"], THEME_MAP["neutral"])
                return result
            else:
                result["meta"]["error"] = "POST(image) succeeded but response did not contain 'emotion'/'mood'."
                return result
        else:
            result["meta"]["error"] = "POST(image) returned non-dict response."
            return result
    else:
        exc = resp_or_exc
        result["meta"]["error"] = repr(exc)
        result["meta"]["traceback"] = traceback.format_exc()
        if hasattr(exc, "response") and exc.response is not None:
            try:
                result["meta"]["http_status"] = exc.response.status_code
                try:
                    result["meta"]["raw_response"] = exc.response.json()
                except Exception:
                    result["meta"]["raw_response"] = exc.response.text
            except Exception:
                pass
        return result

# ---------- UI & Auto-Poll logic ----------
def render():
    st.title("📖 Study Mode — Auto Poll")

    # session init
    if "privacy_accepted" not in st.session_state:
        st.session_state.privacy_accepted = False
    if "camera_verified" not in st.session_state:
        st.session_state.camera_verified = False
    if "current_emotion" not in st.session_state:
        st.session_state.current_emotion = "neutral"
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = THEME_MAP["neutral"]
    if "last_check" not in st.session_state:
        st.session_state.last_check = None
    if "auto_poll_enabled" not in st.session_state:
        st.session_state.auto_poll_enabled = False
    if "auto_snapshot_bytes" not in st.session_state:
        st.session_state.auto_snapshot_bytes = None
    if "last_auto_meta" not in st.session_state:
        st.session_state.last_auto_meta = {}

    # privacy & camera verification (same flow)
    if not st.session_state.privacy_accepted:
        st.warning(
            """
            **Privacy Notice**

            This feature may temporarily access your webcam and local files to analyze focus levels.
            No data is stored or shared externally.
            """
        )
        if st.button("✅ I Understand and Accept"):
            st.session_state.privacy_accepted = True
            st.rerun()
        return

    if not st.session_state.camera_verified:
        with st.expander("🎥 Camera Permission Test"):
            st.info("Take a snapshot to verify camera access.")
            img_test = st.camera_input("Camera Test")
            if img_test:
                st.session_state.camera_verified = True
                st.success("✅ Camera access granted!")
                st.rerun()
        return

    # autorefresh triggers each browser reload/refresh
    st_autorefresh(interval=MOOD_POLL_INTERVAL_SECONDS * 1000, key="auto_mood_poll")

    # Controls for automatic polling
    st.markdown("### 🔁 Auto-poll settings")
    col1, col2 = st.columns([2,3])
    with col1:
        auto_enable = st.checkbox("Enable auto-poll every 5 minutes", value=st.session_state.auto_poll_enabled)
    with col2:
        use_snapshot_for_auto = st.checkbox("Use stored snapshot for auto-poll (capture below)", value=bool(st.session_state.auto_snapshot_bytes))

    st.session_state.auto_poll_enabled = auto_enable

    # Snapshotcapture area (user must capture once to allow auto-image polling)
    st.markdown("### 🔬 Snapshot for manual checks or auto-poll")
    with st.expander("Take or upload a snapshot (you must capture at least once to enable image-based auto-poll)", expanded=True):
        cam_img = st.camera_input("Take snapshot for sending (optional) — click capture then press 'Store for auto-poll'")
        uploaded_img = st.file_uploader("Or upload an image (jpg/png)", type=["jpg","jpeg","png"])
        store_btn = st.button("💾 Store this snapshot for auto-polling")
        if store_btn:
            selected = cam_img or uploaded_img
            if not selected:
                st.warning("Please take a snapshot or upload an image first.")
            else:
                # save bytes into session_state for reuse
                try:
                    img_bytes = selected.getvalue()
                    st.session_state.auto_snapshot_bytes = img_bytes
                    st.success("Stored snapshot for auto-polling. This image will be reused every 5 minutes while auto-poll is enabled.")
                except Exception as e:
                    st.error(f"Could not read image bytes: {e}")

        if st.session_state.auto_snapshot_bytes:
            st.info("A stored snapshot is available for auto-polling. You can replace it by taking/uploading another and clicking 'Store this snapshot'.")
            st.image(BytesIO(st.session_state.auto_snapshot_bytes), caption="Stored snapshot preview", use_column_width=False)

    # Manual send button for on-demand checks (same as before)
    st.markdown("### ▶ Manual check (send snapshot now)")
    with st.expander("Take/upload and send a snapshot to inference API", expanded=False):
        cam_img_now = st.camera_input("Snapshot (manual send)", key="manual_send_camera")
        upload_img_now = st.file_uploader("Or upload image for manual send", type=["jpg","jpeg","png"], key="manual_send_upload")
        send_now = st.button("📡 Send snapshot now")
        if send_now:
            selected_img = cam_img_now or upload_img_now
            if not selected_img:
                st.warning("Please capture or upload an image first.")
            else:
                with st.spinner("Sending snapshot..."):
                    send_result = send_image_bytes_and_get_mood(selected_img.getvalue())
                # update UI based on result
                st.session_state.last_auto_meta = send_result.get("meta", {})
                if send_result.get("meta", {}).get("http_status") is not None and int(send_result["meta"]["http_status"]) >= 400:
                    st.error(f"API returned status {send_result['meta']['http_status']}. See debug panel for details.")
                else:
                    st.session_state.current_emotion = send_result.get("mood", "neutral")
                    st.session_state.current_theme = send_result.get("theme", THEME_MAP["neutral"])
                    st.session_state.last_check = datetime.utcnow()
                    st.success(f"Detected emotion: {st.session_state.current_emotion.upper()}")

    # Auto-poll behavior on refresh:
    now = datetime.utcnow()
    do_auto = st.session_state.auto_poll_enabled
    # compute whether to run based on last_check time
    should_auto_run = False
    if do_auto:
        if st.session_state.last_check is None:
            should_auto_run = True
        else:
            elapsed = (now - st.session_state.last_check).total_seconds()
            if elapsed >= MOOD_POLL_INTERVAL_SECONDS:
                should_auto_run = True

    if should_auto_run and do_auto:
        with st.spinner("Auto-polling inference API..."):
            if use_snapshot_for_auto and st.session_state.auto_snapshot_bytes:
                # send stored snapshot bytes
                auto_res = send_image_bytes_and_get_mood(st.session_state.auto_snapshot_bytes)
                st.session_state.last_auto_meta = auto_res.get("meta", {})
                if auto_res.get("mood"):
                    st.session_state.current_emotion = auto_res.get("mood", "neutral")
                    st.session_state.current_theme = auto_res.get("theme", THEME_MAP["neutral"])
                    st.session_state.last_check = datetime.utcnow()
            else:
                # no stored snapshot: try lightweight probe (GET/POST empty)
                auto_res = probe_api_with_fallbacks()
                st.session_state.last_auto_meta = auto_res.get("meta", {})
                # If probe returned a mood/emotion use it and update
                if auto_res.get("mood"):
                    st.session_state.current_emotion = auto_res.get("mood", "neutral")
                    st.session_state.current_theme = auto_res.get("theme", THEME_MAP["neutral"])
                    st.session_state.last_check = datetime.utcnow()
                # otherwise keep previous theme and expose debug info

    # Apply theme
    theme = st.session_state.current_theme
    emotion = st.session_state.current_emotion
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {theme['bg']} !important; color: {theme['text']} !important; transition: background-color 1s ease, color 1s ease; }}
        .stSidebar {{ background-color: {theme['sidebar']} !important; transition: background-color 1s ease; }}
        h1,h2,h3,h4,h5,h6,p,span {{ color: {theme['text']} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="padding: 15px; border-radius: 10px; background-color:{theme['sidebar']}; color:{theme['text']}; text-align:center;">
            <h4>🧠 Current Emotion: <b>{emotion.upper()}</b></h4>
            <small>Last checked: {st.session_state.last_check.strftime('%Y-%m-%d %H:%M:%S UTC') if st.session_state.last_check else 'N/A'}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Debug / meta info
    with st.expander("⚙️ Mood API Debug Info (expand for details)", expanded=False):
        meta = st.session_state.get("last_auto_meta", {})
        st.write("Configured API URL:", API_URL)
        st.write("Used URL:", meta.get("used_url") or meta.get("configured_url"))
        st.write("TCP reachable (original):", meta.get("tcp_ok"))
        st.write("Host attempts (host, port, reachable):")
        for h in meta.get("host_attempts", []):
            st.write(h)
        st.write("Method tried:", meta.get("method_tried"))
        st.write("Attempts:", meta.get("attempts"))
        st.write("HTTP status:", meta.get("http_status"))
        if meta.get("raw_response") is not None:
            st.write("Raw response (truncated):")
            raw = meta.get("raw_response")
            if isinstance(raw, (dict, list)):
                st.json(raw)
            else:
                st.code(str(raw)[:2000])
        if meta.get("error"):
            st.error(f"Error: {meta.get('error')}")
        if meta.get("traceback"):
            st.text("Traceback (most recent):")
            st.code(meta.get("traceback")[:2000])

        if meta.get("http_status") == 422:
            st.warning("422 Unprocessable Entity: endpoint expects a different payload shape (file key name or JSON schema). Use 'Store snapshot' then 'Enable auto-poll' and try again.")

    # PDF viewer
    st.write("---")
    uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
    if uploaded_file:
        st.write(f"### 📘 Uploaded File: **{uploaded_file.name}**")
        base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px"></iframe>', unsafe_allow_html=True)
    else:
        st.info("Upload a PDF to start reading.")

    st.caption("Auto-poll: every 5 minutes. Note: browser security requires you capture/upload an image once if you want the app to send an image automatically on each poll.")

if __name__ == "__main__":
    render()
