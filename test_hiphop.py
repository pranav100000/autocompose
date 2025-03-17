import requests
import json

url = "http://localhost:8000/api/generate/music"
payload = {
    "description": "Create a very dark hip hop beat with a haunting piano melody, booming 808 bass, and trap-style hi-hats. The beat should have an ominous atmosphere with a slow tempo around 70 BPM.",
    "tempo": 70
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