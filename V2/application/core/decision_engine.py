import requests

class DecisionEngine:
    def __init__(self, api_url="http://localhost:8000/predict"):
        self.api_url = api_url

    def get_mood(self):
        """Fetch mood from inference API"""
        try:
            response = requests.post(self.api_url, json={}, timeout=5)
            response.raise_for_status()
            return response.json().get("mood", "neutral")
        except Exception:
            return "neutral"

    def get_theme(self, mood):
        """Map mood to dark pastel themes"""
        themes = {
            "angry": {"bg": "#1e2a1f", "sidebar": "#253a25", "text": "#a9d6a9"},
            "relaxed": {"bg": "#1b2b38", "sidebar": "#243b4a", "text": "#a3cbe3"},
            "fear": {"bg": "#2e2a1e", "sidebar": "#3b3526", "text": "#d1b897"},
            "suprise": {"bg": "#2b1e1e", "sidebar": "#3a2626", "text": "#e6a5a5"},
            "sad": {"bg": "#1e1e1e", "sidebar": "#2b2b2b", "text": "#cccccc"}
        }
        return themes.get(mood, themes["neutral"])
