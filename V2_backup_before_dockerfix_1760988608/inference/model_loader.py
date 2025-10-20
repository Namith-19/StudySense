# # inference/model_loader.py
# import os
# import numpy as np
# from PIL import Image
# import threading

# _MODEL = None
# _LOCK = threading.Lock()

# def get_model():
#     global _MODEL
#     if _MODEL is None:
#         with _LOCK:
#             if _MODEL is None:
#                 # Replace with real loader (tflite/onnx/keras) as needed
#                 # Example placeholder: simple dummy model object with predict(arr)->probs
#                 class DummyModel:
#                     labels = ['Neutral', 'Fatigued', 'Energized', 'Frustrated']
#                     def predict(self, img_arr):
#                         m = float(np.mean(img_arr))
#                         probs = np.array([0.4,0.2,0.2,0.2])
#                         if m < 80: probs = np.array([0.1,0.6,0.2,0.1])
#                         elif m > 180: probs = np.array([0.2,0.1,0.6,0.1])
#                         return probs
#                 _MODEL = DummyModel()
#     return _MODEL

# def preprocess_image_b64(b64str):
#     from io import BytesIO
#     import base64
#     try:
#         raw = base64.b64decode(b64str)
#         img = Image.open(BytesIO(raw)).convert('RGB')
#         img = img.resize((64,64))
#         arr = np.asarray(img).astype(np.float32)
#         return arr
#     except Exception as e:
#         raise ValueError("Invalid image data") from e







# Dummy:

# model_loader.py
import random
import time

# List of sample emotions for dummy inference
EMOTIONS = ["Happy", "Sad", "Neutral", "Angry", "Surprised", "Fatigued", "Frustrated"]

# Internal variable to simulate a 1-minute window of inference
_start_time = None

def load_dummy_model():
    """
    Initialize dummy model (simulate model load latency)
    """
    print("[INFO] Dummy model loaded successfully (simulated CNN).")
    global _start_time
    _start_time = time.time()

def predict_emotion(_frame=None):
    """
    Returns a random emotion for 1 minute after loading.
    If called after 1 minute, returns None to simulate model cooldown.
    """
    global _start_time
    if _start_time is None:
        raise RuntimeError("Dummy model not loaded. Call load_dummy_model() first.")
    
    # Check time window
    if time.time() - _start_time > 60:
        return None  # After 1 minute, stop giving predictions

    # Randomly pick an emotion
    emotion = random.choice(EMOTIONS)
    # Simulate inference latency (100–300 ms)
    time.sleep(random.uniform(0.1, 0.3))
    return emotion

# Optional standalone test
if __name__ == "__main__":
    load_dummy_model()
    print("Testing dummy inference for 1 minute...\n")
    while True:
        emotion = predict_emotion()
        if emotion is None:
            print("\n[INFO] Dummy inference ended (1 minute complete).")
            break
        print(f"Predicted Emotion: {emotion}")

