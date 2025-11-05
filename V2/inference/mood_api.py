# mood_api.py (enhanced for live dynamic theme)
# Adds a persistent /last_mood endpoint so that frontend live mode can change theme dynamically

import os
import io
import traceback
from typing import Optional, Tuple, Dict
import time

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2

try:
    from tensorflow.keras.models import load_model
except Exception:
    load_model = None

MODEL_PATH = os.environ.get("MODEL_PATH", "/app/model/CNN.h5")
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501")
MODEL_INPUT_SIZE = (48, 48)
HAAR_CASCADE_PATH = os.environ.get("HAAR_CASCADE_PATH", "")
SAVE_PREPROCESSED = os.environ.get("SAVE_PREPROCESSED", "0") == "1"
LAST_MOOD_TTL = int(os.environ.get("LAST_MOOD_TTL", "15"))  # 15 seconds TTL for freshness

app = FastAPI(title="StudySense Inference (CORS + preprocessing + /last_mood)")

origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
EMOTIONS = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]
last_prediction: Dict = {"emotion": None, "confidence": 0.0, "meta": {}, "timestamp": 0}


def load_model_safe(path: str):
    if load_model is None:
        raise RuntimeError("TensorFlow/Keras not available.")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Model file not found at: {path}")
    return load_model(path)


@app.on_event("startup")
def startup_event():
    global model
    try:
        model = load_model_safe(MODEL_PATH)
        print(f"[startup] Loaded model from {MODEL_PATH}")
    except Exception as e:
        model = None
        print(f"[startup] ERROR loading model: {e}")
        traceback.print_exc()


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None, "model_path": MODEL_PATH, "cors_origins": origins}


def read_image_from_bytes(data: bytes) -> Optional[np.ndarray]:
    nparr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def center_crop(img: np.ndarray, crop_size: Tuple[int, int]) -> np.ndarray:
    h, w = img.shape[:2]
    ch, cw = crop_size
    startx = max(0, w // 2 - cw // 2)
    starty = max(0, h // 2 - ch // 2)
    return img[starty:starty + ch, startx:startx + cw]


def preprocess_image_for_model(img_bgr: np.ndarray) -> Tuple[np.ndarray, Dict]:
    meta: Dict = {"face_detected": False, "used_haar": False, "used_clahe": False}
    h0, w0 = img_bgr.shape[:2]

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    cascade_file = HAAR_CASCADE_PATH or (cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    face_cascade = cv2.CascadeClassifier(cascade_file) if os.path.exists(cascade_file) else None

    face_box = None
    if face_cascade is not None:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        if len(faces) > 0:
            faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
            x, y, w, h = faces[0]
            face_box = (x, y, w, h)
            meta["face_detected"] = True
            meta["used_haar"] = True

    if face_box is not None:
        x, y, w, h = face_box
        pad = int(max(w, h) * 0.25)
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(w0, x + w + pad)
        y2 = min(h0, y + h + pad)
        crop = gray[y1:y2, x1:x2]
    else:
        size = min(h0, w0)
        crop = center_crop(gray, (size, size))

    try:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        crop = clahe.apply(crop)
        meta["used_clahe"] = True
    except Exception:
        pass

    resized = cv2.resize(crop, (MODEL_INPUT_SIZE[1], MODEL_INPUT_SIZE[0]), interpolation=cv2.INTER_AREA)
    normalized = resized.astype(np.float32) / 255.0
    input_tensor = normalized.reshape(1, MODEL_INPUT_SIZE[0], MODEL_INPUT_SIZE[1], 1)

    meta["orig_shape"] = (h0, w0)
    meta["crop_shape"] = crop.shape
    meta["final_shape"] = input_tensor.shape
    return input_tensor, meta


@app.post("/predict_emotion")
async def predict_emotion(file: UploadFile = File(...)):
    global last_prediction

    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    img = read_image_from_bytes(contents)
    if img is None:
        raise HTTPException(status_code=400, detail="Unable to decode image")

    try:
        input_tensor, meta = preprocess_image_for_model(img)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {e}")

    try:
        preds = model.predict(input_tensor)
        class_idx = int(np.argmax(preds))
        emotion = EMOTIONS[class_idx] if 0 <= class_idx < len(EMOTIONS) else "Unknown"
        confidence = float(np.max(preds))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    ts = int(time.time())
    last_prediction = {"emotion": emotion, "confidence": confidence, "meta": meta, "timestamp": ts}

    if SAVE_PREPROCESSED:
        try:
            dbg_dir = "/tmp/studysense_debug"
            os.makedirs(dbg_dir, exist_ok=True)
            arr = (input_tensor[0, :, :, 0] * 255.0).astype(np.uint8)
            cv2.imwrite(os.path.join(dbg_dir, f"preproc_{ts}.jpg"), arr)
        except Exception:
            pass

    return {"emotion": emotion, "confidence": confidence, "meta": meta}


@app.get("/last_mood")
def get_last_mood():
    if not last_prediction or last_prediction.get("emotion") is None:
        return {"emotion": None, "confidence": 0.0, "meta": {}, "fresh": False}

    now = int(time.time())
    age = now - last_prediction.get("timestamp", 0)
    fresh = age <= LAST_MOOD_TTL

    return {
        "emotion": last_prediction.get("emotion"),
        "confidence": last_prediction.get("confidence"),
        "meta": last_prediction.get("meta"),
        "age": age,
        "fresh": fresh,
    }
