from fastapi import FastAPI, File, UploadFile
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import cv2
import io

app = FastAPI()

# Load model
MODEL_PATH = "/home/namithk/Documents/code/studysense/V2/inference/fer_mobilenetv3_small.h5"
model = load_model(MODEL_PATH)
EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

@app.post("/predict_emotion")
async def predict_emotion(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized / 255.0
    reshaped = normalized.reshape(1, 48, 48, 1)

    preds = model.predict(reshaped)
    class_idx = np.argmax(preds)
    emotion = EMOTIONS[class_idx]
    confidence = float(np.max(preds))

    return {"emotion": emotion, "confidence": confidence}
