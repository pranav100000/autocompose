import requests
import json

url = "http://localhost:8000/api/generate/music"
payload = {
    "description": "Create an upbeat electronic dance track with a catchy synth lead melody, pulsing bassline, and energetic drums. The track should have a bright, euphoric feeling with a tempo around 128 BPM.",
    "tempo": 128
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