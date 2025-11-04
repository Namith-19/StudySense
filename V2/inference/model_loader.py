import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import io

# Load model at module level so it loads only once
MODEL_PATH = "/home/namithk/Documents/code/studysense/V2/inference/fer_mobilenetv3_small.h5"
model = load_model(MODEL_PATH)

# Class labels (adjust according to your training)
CLASS_LABELS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

def preprocess_image(image_bytes):
    """Convert uploaded image to model input format"""
    image = Image.open(io.BytesIO(image_bytes)).convert('L').resize((48, 48))
    image = img_to_array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

def predict_emotion(image_bytes):
    """Run model prediction"""
    processed = preprocess_image(image_bytes)
    preds = model.predict(processed)
    label = CLASS_LABELS[np.argmax(preds)]
    confidence = float(np.max(preds))
    return {"emotion": label, "confidence": round(confidence, 3)}
