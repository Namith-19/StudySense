import cv2
import numpy as np
import requests
from collections import deque
import time
import sys
import os

# ==========================
# CONFIGURATION
# ==========================
API_URL = "http://127.0.0.1:8000/predict_emotion"  # Change if hosted elsewhere
BUFFER_SIZE = 7  # number of frames for smoothing
CONFIDENCE_THRESHOLD = 0.5  # for uncertain predictions
WINDOW_NAME = "StudySense - Real-Time Emotion Detection"

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
    # convert to grayscale, resize and normalize
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (48, 48))
    normalized = resized.astype("float32") / 255.0
    reshaped = np.reshape(normalized, (1, 48, 48, 1))
    return reshaped

# ==========================
# Check if cv2 GUI is available
# ==========================
def gui_available():
    try:
        # Try to create a test window
        cv2.namedWindow("__test__")
        cv2.imshow("__test__", np.zeros((10,10,3), dtype=np.uint8))
        cv2.waitKey(1)
        cv2.destroyWindow("__test__")
        return True
    except Exception:
        return False

# ==========================
# MAIN LOOP
# ==========================
def capture_and_predict():
    # Check GUI support first
    if not gui_available():
        print("\nERROR: OpenCV GUI not available in this environment.")
        print(" - If you're on Linux, install GUI deps: sudo apt install libgtk2.0-dev pkg-config")
        print(" - Ensure opencv-python (not opencv-python-headless) is installed.")
        print(" - If using WSL, run with an X server (VcXsrv) or run on a desktop machine.\n")
        return

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == "nt" else 0)

    if not cap.isOpened():
        print("Error: Could not access camera. Try changing the device index (0 -> 1).")
        return

    print("🎥 Camera started. Press 'q' to quit.")
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Warning: empty frame received.")
                time.sleep(0.1)
                continue

            display_frame = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            # If no faces, show message
            if len(faces) == 0:
                cv2.putText(display_frame, "No face detected", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            for (x, y, w, h) in faces:
                face_roi = frame[y:y+h, x:x+w]

                # Optionally draw box while processing
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), (200, 200, 0), 2)

                # Preprocessing (local use only, but we send jpg to API for inference)
                processed = preprocess_face(face_roi)

                # Encode face region as jpg bytes and send to API
                try:
                    _, img_encoded = cv2.imencode('.jpg', cv2.resize(face_roi, (48, 48)))
                    response = requests.post(API_URL, files={"file": img_encoded.tobytes()}, timeout=2.5)
                    if response.status_code == 200:
                        pred_data = response.json()
                        emotion = pred_data.get("emotion", "Unknown")
                        confidence = float(pred_data.get("confidence", 0.0))
                    else:
                        emotion = "Error"
                        confidence = 0.0
                except requests.exceptions.RequestException as e:
                    emotion = "Error"
                    confidence = 0.0
                    print("API request error:", e)

                # Append to buffer only if confident
                if confidence > CONFIDENCE_THRESHOLD and emotion not in ("Error", None):
                    pred_buffer.append(emotion)

                # Determine stable emotion via np.unique
                if len(pred_buffer) > 0:
                    values, counts = np.unique(np.array(pred_buffer), return_counts=True)
                    stable_emotion = values[np.argmax(counts)]
                else:
                    stable_emotion = "Uncertain"

                # Overlay result on frame
                label = f"{stable_emotion} ({confidence:.2f})" if emotion!="Error" else "API Error"
                color = (0, 255, 0) if stable_emotion != "Error" else (0, 0, 255)
                cv2.putText(display_frame, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

            # Display the frame (this is the missing call in your previous script)
            cv2.imshow(WINDOW_NAME, display_frame)

            # Press q to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # small sleep to reduce CPU usage
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_and_predict()
