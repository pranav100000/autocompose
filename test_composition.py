import requests
import json

# Test the composition endpoint
url = "http://localhost:8000/api/composition/Haunting%20Echoes"
try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    # Get the data but don't print the base64 encoded MIDI data
    data = response.json()
    for midi_file in data.get("midi_files", []):
        midi_file["midi_data"] = "[base64 data removed for clarity]"
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")