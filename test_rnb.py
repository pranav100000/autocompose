import requests
import json

url = "http://localhost:8000/api/generate/music"
payload = {
    "description": "Make a melodic RnB Beat that tells a story with its melody. The tempo should be around 120 BPM. The beat should have drums, a saxophone, a choir, a piano, and a triangle.",
    "tempo": 120
}

response = requests.post(url, json=payload)
print(f"Status code: {response.status_code}")
# Get the data but don't print the base64 encoded MIDI data
if response.status_code == 200:
    data = response.json()
    for track in data.get("tracks", []):
        track["midi_data"] = "[base64 data removed for clarity]"
    print(json.dumps(data, indent=2))
else:
    print(response.text)