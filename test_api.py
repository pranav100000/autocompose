#!/usr/bin/env python3
"""
Test script for the AutoCompose API.
"""
import os
import sys
import asyncio
import json
import base64
import subprocess
import tempfile

def run_server():
    """Start the FastAPI server."""
    print("Starting FastAPI server...")
    
    # Start the server process
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Start a thread to read the server output
    import threading
    
    def read_output(stream, name):
        for line in stream:
            line = line.strip()
            if line:
                if "ERROR" in line:
                    print(f"SERVER {name.upper()}: {line}", flush=True)
                elif "INFO" in line and ("Started server" in line or "Application startup complete" in line):
                    print(f"SERVER {name.upper()}: {line}", flush=True)

    threading.Thread(target=read_output, args=(process.stdout, "out"), daemon=True).start()
    threading.Thread(target=read_output, args=(process.stderr, "err"), daemon=True).start()
    
    return process

def test_api():
    """Test the API using command line tools."""
    print("=" * 60)
    print("AutoCompose API Test")
    print("=" * 60)
    
    # Test root endpoint
    print("\nTesting API root...")
    try:
        # We'll use Python itself instead of curl
        import urllib.request
        response = urllib.request.urlopen("http://127.0.0.1:8000/")
        data = response.read().decode("utf-8")
        print(f"Response: {response.getcode()} {data}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    # Test soundfonts endpoint
    print("\nTesting soundfonts endpoint...")
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/api/soundfonts?query=piano")
        data = json.loads(response.read().decode("utf-8"))
        print(f"Found {data['total']} piano soundfonts")
        if data['total'] > 0:
            sample = data['soundfonts'][0]
            print(f"Sample soundfont: {sample['name']} ({sample['inferred_type']['type']})")
    except Exception as e:
        print(f"Error getting soundfonts: {str(e)}")
        print("Continuing with tests...")
    
    # Test music generation
    print("\nGenerating music...")
    try:
        # Create a temporary file for the request
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name
            json.dump({
                "description": "A dark and moody piano melody with a slow tempo",
                "tempo": 60,
                "key": "E flat minor",
                "duration": 10
            }, tmp)
        
        # Use Python's urllib.request to make a POST request
        import urllib.request
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/generate/music",
            data=open(tmp_path, "rb").read(),
            headers={"Content-Type": "application/json"}
        )
        
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode("utf-8"))
        
        print(f"Generated music: {data['title']}")
        print(f"Composition directory: {data['directory']}")
        print(f"Total tracks: {len(data['tracks'])}")
        
        # Create output directory
        test_dir = "test_output"
        os.makedirs(test_dir, exist_ok=True)
        
        # Save each MIDI file
        for i, track in enumerate(data['tracks']):
            midi_data = base64.b64decode(track['midi_data'])
            output_file = os.path.join(test_dir, f"{track['soundfont_name']}.mid")
            with open(output_file, "wb") as f:
                f.write(midi_data)
            print(f"Saved track {i+1}: {track['instrument_name']} ({track['soundfont_name']}) to {output_file}")
            print(f"Download URL: http://127.0.0.1:8000{track['download_url']}")
        
        # Clean up
        os.unlink(tmp_path)
        
        # Test getting composition details
        if data['directory']:
            composition_dir = os.path.basename(data['directory'])
            print(f"\nTesting composition endpoint for {composition_dir}...")
            try:
                comp_url = f"http://127.0.0.1:8000/api/composition/{composition_dir}"
                response = urllib.request.urlopen(comp_url)
                comp_data = json.loads(response.read().decode("utf-8"))
                
                print(f"Composition has {comp_data['file_count']} files:")
                for i, file in enumerate(comp_data['midi_files']):
                    print(f"  {i+1}. {file['filename']} - {file['soundfont_name']}")
                    print(f"     Download: http://127.0.0.1:8000{file['download_url']}")
            except Exception as e:
                print(f"Error getting composition details: {str(e)}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

def main():
    """Run the test."""
    # Start the server
    server_process = run_server()
    
    try:
        # Give the server time to start (MCP initialization takes time)
        print("Waiting for server to start...")
        import time
        wait_time = 10  # Longer wait for MCP initialization
        for i in range(wait_time):
            print(f"Starting in {wait_time - i} seconds...", end="\r")
            time.sleep(1)
        print("\nServer should be ready now.")
        
        # Run the tests
        success = test_api()
        
        if success:
            print("\nTests completed successfully!")
        else:
            print("\nTests failed.")
            
    finally:
        # Stop the server
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()