from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import random

# Fake emotion classes for demo
class_labels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

app = FastAPI(title="Emotion Detection API (Demo)", version="1.0")

@app.get("/")
def root():
    return {"message": "Welcome to the Demo Emotion Detection API 🚀"}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # Pretend we processed the image
    # Randomly choose an emotion for demo
    pred_label = random.choice(class_labels)
    confidence = round(random.uniform(0.5, 1.0), 4)

    return JSONResponse(content={
        "predicted_class": pred_label,
        "confidence": confidence,
        "all_probabilities": {label: round(random.uniform(0, 1), 4) for label in class_labels}
    })
    