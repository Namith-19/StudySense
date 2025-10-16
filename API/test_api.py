# import requests
# import json
# import os

# # ==========================
# # CONFIGURATION
# # ==========================
# API_URL = "http://127.0.0.1:8000/predict"   # FastAPI endpoint
# TEST_IMAGE_PATH = "/mnt/d/CODE/StudySense/test_images/test_angry.jpg"            # Change to your test image path

# # ==========================
# # FUNCTION TO TEST API
# # ==========================
# def test_studysense_api(image_path):
#     if not os.path.exists(image_path):
#         print(f"❌ Error: File '{image_path}' not found.")
#         return

#     try:
#         with open(image_path, "rb") as file:
#             files = {"file": file}
#             response = requests.post(API_URL, files=files)
        
#         # Handle errors
#         if response.status_code != 200:
#             print(f"❌ API Error {response.status_code}: {response.text}")
#             return

#         data = response.json()
#         print("\n✅ API Test Successful!")
#         print("-" * 40)
#         print(f"Predicted Emotion     : {data.get('emotion')}")
#         print(f"Confidence Score      : {data.get('confidence')}")
#         print(f"UI Recommendation     : {data.get('ui_recommendation')}")
#         print("-" * 40)

#     except requests.exceptions.ConnectionError:
#         print("❌ Failed to connect to the API. Make sure it's running with: uvicorn app:app --reload")
#     except Exception as e:
#         print(f"⚠️ Unexpected error: {e}")


# # ==========================
# # MAIN
# # ==========================
# if __name__ == "__main__":
#     print("🔍 Testing StudySense Emotion Detection API...")
#     test_studysense_api(TEST_IMAGE_PATH)


import requests

print("🔍 Testing StudySense Emotion Detection API...")

url = "http://127.0.0.1:8000/predict/"
file_path = "/mnt/d/CODE/StudySense/test_images/image.png"  # path to a test grayscale image

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("✅ Response:", response.json())
else:
    print(f"❌ API Error {response.status_code}: {response.text}")
