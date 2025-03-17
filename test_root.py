import requests

# Test the root endpoint
url = "http://localhost:8000/"
try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")