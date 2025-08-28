import requests, os
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
def tts(text:str):
    return requests.post(f"{BASE_URL}/api/v1/tts", json={"text": text}).json()
