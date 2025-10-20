from fastapi import FastAPI
from pydantic import BaseModel
from model_loader import model

app = FastAPI()

class FrameInput(BaseModel):
    image_base64: str

@app.post("/predict")
def predict_emotion(data: FrameInput):
    emotion = model.predict(data.image_base64)
    return {"emotion": emotion}
