import cv2
import numpy as np
import requests
from collections import deque
from scipy import stats
import time

# ==========================
# CONFIGURATION
# ==========================
API_URL = "http://127.0.0.1:8000/predict_emotion"  # Change if hosted elsewhere
BUFFER_SIZE = 7  # number of frames for smoothing
CONFIDENCE_THRESHOLD = 0.5  # for uncertain predictions

# ==========================
# FACE DETECTION SETUP
# ==========================
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Rolling buffer for predictions
pred_buffer = deque(maxlen=BUFFER_SIZE)

# Emotion labels (must match your model training order)
EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# ==========================
# HELPER: Process face for model input
# ==========================
def preprocess_face(face):
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized / 255.0
    reshaped = np.reshape(normalized, (1, 48, 48, 1))
    return reshaped

# ==========================
# MAIN LOOP
# ==========================
def capture_and_predict():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access camera.")
        return

    print("🎥 Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            processed = preprocess_face(face_roi)

            # Send to API
            try:
                _, img_encoded = cv2.imencode('.jpg', cv2.resize(face_roi, (48, 48)))
                response = requests.post(API_URL, files={"file": img_encoded.tobytes()})
                if response.status_code == 200:
                    pred_data = response.json()
                    emotion = pred_data.get("emotion")
                    confidence = pred_data.get("confidence", 0)
                else:
                    emotion = "Error"
                    confidence = 0.0
            except Exception as e:
                emotion = "Error"
                confidence = 0.0
                print(f"API error: {e}")

            # Apply smoothing
            # Apply smoothing
            if confidence > CONFIDENCE_THRESHOLD:
                pred_buffer.append(emotion)

            if len(pred_buffer) > 0:
                # Find the most frequent emotion in buffer (mode equivalent)
                values, counts = np.unique(pred_buffer, return_counts=True)
                stable_emotion = values[np.argmax(counts)]
            else:
                stable_emotion = "Uncertain"

            # Display results
            color = (0, 255, 0) if stable_emotion != "Error" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{stable_emotion}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_and_predict()
