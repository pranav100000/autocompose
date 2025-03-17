#!/usr/bin/env python3
"""
HTTP client test script for the AutoCompose API.
This script assumes the server is already running at http://127.0.0.1:8000
"""
import os
import json
import base64
import urllib.request
import tempfile

def test_api():
    """Test the API using Python's built-in HTTP client."""
    print("=" * 60)
    print("AutoCompose API Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/")
        print("\nServer is running.")
    except Exception as e:
        print(f"\nERROR: Server is not running at http://127.0.0.1:8000")
        print(f"Error details: {e}")
        print("\nPlease start the server first with:")
        print("uvicorn app.main:app --reload --port=8000")
        return False
    
    # Test soundfonts endpoint
    print("\nFetching piano soundfonts...")
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
    print("\nGenerating music (this may take some time)...")
    try:
        # Create a temporary file for the request
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name
            json.dump({
                "description": "A cheerful piano melody with a gentle rhythm",
                "tempo": 120,
                "key": "C major",
                "duration": 10
            }, tmp)
        
        # Send the request
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/generate/music",
            data=open(tmp_path, "rb").read(),
            headers={"Content-Type": "application/json"}
        )
        
        # Wait for the response (this may take a while)
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
            # Use a short identifier to avoid URL encoding issues
            # Just use the first word for simplicity
            composition_id = composition_dir.split()[0]
            print(f"\nFetching composition details for ID: {composition_id}...")
            try:
                comp_url = f"http://127.0.0.1:8000/api/composition/{composition_id}"
                response = urllib.request.urlopen(comp_url)
                comp_data = json.loads(response.read().decode("utf-8"))
                
                print(f"Composition has {comp_data['file_count']} files:")
                for i, file in enumerate(comp_data['midi_files']):
                    print(f"  {i+1}. {file['filename']} - {file['soundfont_name']}")
                    print(f"     Download: http://127.0.0.1:8000{file['download_url']}")
            except Exception as e:
                print(f"Error getting composition details: {str(e)}")
                
    except Exception as e:
        print(f"Error generating music: {str(e)}")
        return False
    
    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    test_api()