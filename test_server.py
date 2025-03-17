#!/usr/bin/env python
"""
Test script to verify the AutoCompose server is working.
"""
import asyncio
import json
import urllib.request
import urllib.parse

async def test_api():
    """Test the music generation API."""
    print("Testing music generation API...")
    
    # API endpoint
    url = "http://127.0.0.1:8000/api/generate/music"
    
    # Request data
    data = {
        "description": "An upbeat jazz tune with piano, bass and drums",
        "tempo": 130,
        "key": "F major"
    }
    
    # Convert to JSON
    json_data = json.dumps(data).encode("utf-8")
    
    # Create request
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        # Send request
        with urllib.request.urlopen(req) as response:
            # Parse response
            result = json.loads(response.read().decode("utf-8"))
            
            # Print result
            print(f"Generated music: {result['title']}")
            print(f"Instruments: {', '.join(result['instruments'])}")
            print(f"Download URL: http://127.0.0.1:8000{result['download_url']}")
            
            # Download MIDI file
            download_url = f"http://127.0.0.1:8000{result['download_url']}"
            output_file = "test_output.mid"
            
            urllib.request.urlretrieve(download_url, output_file)
            print(f"Downloaded MIDI file to {output_file}")
            
            return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def main():
    """Run the test."""
    await test_api()

if __name__ == "__main__":
    asyncio.run(main())