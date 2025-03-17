import requests
import json

url = "http://localhost:8000/api/generate/music"
payload = {
    "description": "Create a dark, haunting piano melody with slow, minor key progression and distant echoes."
}

response = requests.post(url, json=payload)
print(f"Status code: {response.status_code}")
print(json.dumps(response.json(), indent=2))