# from fastapi import FastAPI, File, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# import numpy as np
# import tensorflow as tf
# from PIL import Image
# import io

# app = FastAPI(title="StudySense Emotion Detection API")

# # Allow frontend (Tkinter/Streamlit) to access API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load your trained CNN model
# MODEL_PATH = "../src_model/fer_cnn_model.h5"  # change path if different
# model = tf.keras.models.load_model(MODEL_PATH)

# # Emotion class labels
# CLASS_NAMES = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# def preprocess_image(image_bytes):
#     """Convert image bytes to model-ready numpy array."""
#     img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     img = img.resize((48, 48))  # match model input size
#     img_array = np.array(img) / 255.0
#     img_array = np.expand_dims(img_array, axis=0)
#     return img_array

# @app.get("/")
# def root():
#     return {"message": "StudySense Emotion API is running 🚀"}

# @app.post("/predict")
# async def predict(file: UploadFile = File(...)):
#     contents = await file.read()
#     image = preprocess_image(contents)
#     preds = model.predict(image)
#     pred_class = np.argmax(preds[0])
#     confidence = float(np.max(preds[0]))

#     emotion = CLASS_NAMES[pred_class]

#     # Emotion-to-UI mapping logic (you can fine-tune this)
#     ui_recommendations = {
#         "angry": "Switch to calm blue theme, reduce distractions",
#         "disgust": "Neutral UI, possibly prompt for short break",
#         "fear": "Warm colors, encouraging popup",
#         "happy": "Bright theme, maintain current environment",
#         "neutral": "Keep default UI",
#         "sad": "Enable motivational messages, slightly brighter theme",
#         "surprise": "No change, momentary state"
#     }

#     return {
#         "emotion": emotion,
#         "confidence": round(confidence, 3),
#         "ui_recommendation": ui_recommendations.get(emotion, "Default UI"),
#     }


from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image
import io

app = FastAPI(title="StudySense Emotion Detection API")

# Load your trained CNN model
model = tf.keras.models.load_model("/mnt/d/CODE/StudySense/src_model/fer_cnn_model.h5")

# Class indices
class_indices = {
    'angry': 0,
    'disgust': 1,
    'fear': 2,
    'happy': 3,
    'neutral': 4,
    'sad': 5,
    'surprise': 6
}
idx_to_class = {v: k for k, v in class_indices.items()}

@app.get("/")
def root():
    return {"message": "StudySense Emotion Detection API is running!"}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Read and preprocess the image
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("L")  # Convert to grayscale
        img = img.resize((48, 48))  # FER image size
        img_array = np.array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=(0, -1))  # Shape: (1, 48, 48, 1)

        # Prediction
        preds = model.predict(img_array)
        predicted_idx = np.argmax(preds, axis=1)[0]
        predicted_label = idx_to_class[predicted_idx]

        return {"emotion": predicted_label, "confidence": float(np.max(preds))}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
