import requests

url = "http://127.0.0.1:8000/predict"
file_path = "/home/namithk/Documents/code/studysense/Data/FER/test/fear/PrivateTest_2159049.jpg"

with open(file_path, "rb") as f:
    files = {"file": f}
    res = requests.post(url, files=files)

print(res.json())
