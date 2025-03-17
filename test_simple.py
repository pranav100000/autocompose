#!/usr/bin/env python
"""
Test script for simple MIDI generation API.
"""
import asyncio
import subprocess
import time
import json
import urllib.request
import urllib.parse

async def start_server():
    """Start the server in the background."""
    server_process = subprocess.Popen(
        ["python", "simple.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("Starting server...")
    time.sleep(2)  # Wait for server to start
    
    return server_process

def make_request():
    """Make a request to the MIDI generation endpoint."""
    print("Making API request...")
    
    # Prepare request
    url = "http://127.0.0.1:8000/generate"
    data = {
        "description": "A simple piano melody",
        "tempo": 120,
        "key": "C Major"
    }
    
    # Convert to JSON
    json_data = json.dumps(data).encode("utf-8")
    
    # Make request
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(f"Generated MIDI file: {result['title']}")
            print(f"Download URL: http://127.0.0.1:8000{result['download_url']}")
            print(f"Instruments: {', '.join(result['instruments'])}")
            return result
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

async def main():
    """Run the test."""
    server = await start_server()
    
    try:
        # Test the endpoint
        result = make_request()
        
        if result:
            print("Test successful!")
        else:
            print("Test failed.")
            
    finally:
        # Kill the server
        print("Shutting down server...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    asyncio.run(main())