# V2/ui_adapter.py
"""
UI Adapter: maps emotion predictions to UI updates and calls your existing UI engine (if available).
This module is designed to be non-invasive: it will try a few common function names on your UI engine
and otherwise apply Streamlit-based UI changes (background color, emoji, text).
"""

from typing import Optional, Dict, Any
import streamlit as st
import importlib
import logging

LOGGER = logging.getLogger("ui_adapter")

# ---- Emotion -> presentation mapping ----
EMOTION_THEME = {
    # emotion: (background_css_color, emoji, message)
    "happy": ("#fff7e6", "😄", "You're focused and happy — keep going!"),
    "sad": ("#e6f0ff", "😔", "Looks low — take a short break or try a breathing exercise."),
    "neutral": ("#ffffff", "😐", "Neutral mood — steady progress."),
    "angry": ("#fff0f0", "😡", "Take a breath — maybe a short pause will help."),
    "surprise": ("#fff5f7", "😮", "Something surprising! Stay curious."),
    "disgust": ("#f6fff2", "🤢", "Maybe switch tasks for a minute."),
    "fear": ("#f8f0ff", "😨", "Take a slow breath and re-center."),
    # fallback
    "default": ("#ffffff", "🙂", "Keep going — you've got this.")
}

# If your UI engine module is named differently, set this to the import path
# e.g. "app.ui.engine" or "ui.engine"
UI_ENGINE_IMPORT_PATHS = [
    "ui_engine",           # common name
    "app.ui_engine",       # alternate
    "app.ui.engine",       # nested
    "ui.engine",           # alternate
]

def load_ui_engine():
    """Try to import the user's UI engine from common import paths. Return module or None."""
    for path in UI_ENGINE_IMPORT_PATHS:
        try:
            mod = importlib.import_module(path)
            LOGGER.info(f"Loaded UI engine from {path}")
            return mod
        except Exception:
            continue
    LOGGER.debug("No UI engine module found in common paths.")
    return None

# Try to find engine on import
_UI_ENGINE = load_ui_engine()

def map_emotion_to_theme(emotion: Optional[str]) -> Dict[str, str]:
    """Return color, emoji and message for given emotion (case-insensitive)."""
    if not emotion:
        emotion = "default"
    e = emotion.lower()
    return {
        "color": EMOTION_THEME.get(e, EMOTION_THEME["default"])[0],
        "emoji": EMOTION_THEME.get(e, EMOTION_THEME["default"])[1],
        "message": EMOTION_THEME.get(e, EMOTION_THEME["default"])[2],
        "emotion": e
    }

# ---- Streamlit helper: apply simple theme changes ----
def apply_streamlit_theme(color: str):
    """
    Apply a simple background color to Streamlit app using injected CSS.
    Non-invasive and reversible on next reload.
    """
    css = f"""
    <style>
    .stApp {{
        background: {color};
    }}
    /* small box for the overlay */
    .emotion-overlay {{
        position: fixed;
        top: 12px;
        right: 12px;
        z-index: 9999;
        padding: 10px 14px;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        background: rgba(255,255,255,0.85);
        font-size: 18px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def show_emotion_overlay(emoji: str, message: str):
    """Render a small floating overlay with emoji and message."""
    html = f"""
    <div class="emotion-overlay">
      <div style="font-size:28px;">{emoji}</div>
      <div style="font-size:13px;color:#222">{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---- UI engine integration ----
def call_ui_engine(emotion: str, score: float = None) -> bool:
    """
    Try to call common hooks on the user's UI engine, return True if a call was made.
    Common hook names tried:
     - update_ui_state(emotion=..., score=...)
     - set_emotion(emotion, score)
     - engine.apply_emotion(emotion, score)
    """
    if not _UI_ENGINE:
        return False

    try:
        # 1) update_ui_state(emotion=..., score=...)
        if hasattr(_UI_ENGINE, "update_ui_state"):
            try:
                _UI_ENGINE.update_ui_state(emotion=emotion, score=score)
                return True
            except TypeError:
                # try with positional args
                _UI_ENGINE.update_ui_state(emotion, score)
                return True
    except Exception as e:
        LOGGER.debug("update_ui_state failed: %s", e)

    try:
        if hasattr(_UI_ENGINE, "set_emotion"):
            _UI_ENGINE.set_emotion(emotion, score)
            return True
    except Exception as e:
        LOGGER.debug("set_emotion failed: %s", e)

    try:
        # nested object e.g. ui_engine.engine.apply_emotion
        if hasattr(_UI_ENGINE, "engine") and hasattr(_UI_ENGINE.engine, "apply_emotion"):
            _UI_ENGINE.engine.apply_emotion(emotion, score)
            return True
    except Exception as e:
        LOGGER.debug("engine.apply_emotion failed: %s", e)

    return False

# ---- Public function used by camera integration ----
def handle_prediction_result(prediction: Dict[str, Any], show_streamlit: bool = True):
    """
    prediction: dict expected to contain keys like "emotion", "label", "score", "confidence".
    show_streamlit: whether to apply streamlit-side UI changes (safe default True).
    """
    if not prediction:
        return

    # normalize fields
    emotion = None
    if isinstance(prediction, dict):
        emotion = prediction.get("emotion") or prediction.get("label") or prediction.get("predicted")
        # some models return top class in ['classes'][0] etc — be defensive:
        if not emotion:
            if "classes" in prediction and isinstance(prediction["classes"], (list,tuple)) and len(prediction["classes"])>0:
                emotion = prediction["classes"][0]
    score = prediction.get("score") or prediction.get("confidence") or prediction.get("prob") or None

    theme = map_emotion_to_theme(emotion)
    if show_streamlit:
        try:
            apply_streamlit_theme(theme["color"])
            show_emotion_overlay(theme["emoji"], theme["message"])
        except Exception as e:
            LOGGER.debug("Streamlit UI update failed: %s", e)

    # attempt to notify user's UI engine (non-destructive)
    try:
        called = call_ui_engine(theme["emotion"], score)
        if called:
            LOGGER.info("UI engine notified of emotion: %s", theme["emotion"])
    except Exception as e:
        LOGGER.debug("Error while calling UI engine: %s", e)
