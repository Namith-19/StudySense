# from fastapi import FastAPI, File, UploadFile
# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.models import load_model
# import cv2
# import io

# app = FastAPI()

# # Load model
# MODEL_PATH = "/home/namithk/Documents/code/studysense/V2/inference/fer_mobilenetv3_small.h5"
# model = load_model(MODEL_PATH)
# EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# @app.post("/predict_emotion")
# async def predict_emotion(file: UploadFile = File(...)):
#     contents = await file.read()
#     nparr = np.frombuffer(contents, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     resized = cv2.resize(gray, (48, 48))
#     normalized = resized / 255.0
#     reshaped = normalized.reshape(1, 48, 48, 1)

#     preds = model.predict(reshaped)
#     class_idx = np.argmax(preds)
#     emotion = EMOTIONS[class_idx]
#     confidence = float(np.max(preds))

#     return {"emotion": emotion, "confidence": confidence}


# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import cv2
import os
import io

app = FastAPI()

# Model path via env var (default to mounted path inside container)
MODEL_PATH = os.environ.get("MODEL_PATH", "/app/model/fer_mobilenetv3_small.h5")
model = None
EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

def load_model_safe(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Model file not found at: {path}")
    return load_model(path)

@app.on_event("startup")
def startup_event():
    global model
    try:
        model = load_model_safe(MODEL_PATH)
        print(f"Loaded model from {MODEL_PATH}")
    except Exception as e:
        # Ensure container still runs but endpoints return 500 with helpful message
        print(f"ERROR loading model: {e}")
        model = None

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None, "model_path": MODEL_PATH}

@app.post("/predict_emotion")
async def predict_emotion(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not loaded. Expected at {MODEL_PATH}")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image uploaded")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized / 255.0
    reshaped = normalized.reshape(1, 48, 48, 1).astype(np.float32)

    preds = model.predict(reshaped)
    class_idx = int(np.argmax(preds))
    emotion = EMOTIONS[class_idx]
    confidence = float(np.max(preds))

    return {"emotion": emotion, "confidence": confidence}

