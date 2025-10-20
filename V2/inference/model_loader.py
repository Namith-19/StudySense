import numpy as np

class EmotionModel:
    def __init__(self):
        print("Model loaded (dummy)")

    def predict(self, frame):
        # Dummy inference - returns fake emotion
        emotions = ["happy", "sad", "angry", "neutral"]
        return np.random.choice(emotions)

model = EmotionModel()
