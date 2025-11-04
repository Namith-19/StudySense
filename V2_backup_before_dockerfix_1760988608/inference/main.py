from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(title="Mood Detection API", version="1.0")

# CORS setup for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOODS = ["focused", "relaxed", "distracted", "stressed", "neutral"]

@app.get("/")
def home():
    return {"status": "ok", "message": "Mood API running successfully"}

@app.post("/predict")
def predict_mood():
    """Return a random mood (temporary inference simulation)"""
    mood = random.choice(MOODS)
    return {"mood": mood}
