#!/usr/bin/env python3
"""
Local Test Script for RunPod Kiss Video API
Run this on your local machine to test video generation
"""

import requests
import base64
import json
import os
import time
from datetime import datetime

# Configuration
API_KEY = "YOUR_RUNPOD_API_KEY"  # Replace with your actual RunPod API key
ENDPOINT_ID = "63wukybus821bc"  # Your endpoint ID
API_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"

def test_video_generation(source_image_url, target_image_url, output_format="base64"):
    """Test video generation with two image URLs"""
    
    print("🚀 Testing RunPod Kiss Video Generation")
    print("=" * 50)
    print(f"📸 Source: {source_image_url}")
    print(f"📸 Target: {target_image_url}")
    print(f"📤 Output: {output_format}")
    print()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    data = {
        'input': {
            'source_image_url': source_image_url,
            'target_image_url': target_image_url,
            'output_format': output_format
        }
    }
    
    try:
        print("🔄 Sending request to RunPod...")
        start_time = time.time()
        
        response = requests.post(API_URL, headers=headers, json=data, timeout=300)
        
        request_time = time.time() - start_time
        print(f"⏱️ Request completed in {request_time:.1f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response Status: {response.status_code}")
            print(f"📊 Response: {json.dumps(result, indent=2)[:500]}...")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def decode_base64_video(base64_data, output_filename=None):
    """Decode base64 video and save as MP4"""
    try:
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"kiss_video_{timestamp}.mp4"
        
        print(f"🎬 Decoding base64 video to {output_filename}...")
        
        # Decode base64
        video_bytes = base64.b64decode(base64_data)
        
        # Save to file
        with open(output_filename, 'wb') as f:
            f.write(video_bytes)
        
        file_size = len(video_bytes)
        print(f"✅ Video saved: {output_filename}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"🎬 You can now play: {output_filename}")
        
        return output_filename
        
    except Exception as e:
        print(f"❌ Failed to decode video: {e}")
        return None

def main():
    """Main test function"""
    print("🎬 RunPod Kiss Video API - Local Test")
    print("=" * 40)
    
    # Check API key
    if API_KEY == "YOUR_API_KEY":
        print("❌ Please update API_KEY with your actual RunPod API key")
        return
    
    # Test URLs (you can change these)
    source_url = "https://wfl-app.com/images/french-girl.jpg"
    target_url = "https://wfl-app.com/images/pakistani-man.jpg"
    
    print(f"🔑 Using API Key: {API_KEY[:10]}...")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print()
    
    # Test 1: Base64 output (guaranteed to work)
    print("📋 TEST 1: Base64 Output")
    print("-" * 25)
    result = test_video_generation(source_url, target_url, "base64")
    
    if result and result.get('status') == 'COMPLETED':
        output_data = result.get('output', {})
        
        if 'video' in output_data:
            print("✅ Base64 video received!")
            video_file = decode_base64_video(output_data['video'])
            if video_file:
                print(f"🎉 SUCCESS! Your video is ready: {video_file}")
        elif 'video_url' in output_data:
            print(f"✅ Video URL received: {output_data['video_url']}")
        else:
            print("⚠️ No video data found in response")
    
    print("\n" + "=" * 50)
    
    # Test 2: URL output (may fallback to base64)
    print("📋 TEST 2: URL Output (may fallback)")
    print("-" * 35)
    result = test_video_generation(source_url, target_url, "url")
    
    if result and result.get('status') == 'COMPLETED':
        output_data = result.get('output', {})
        
        if 'video_url' in output_data:
            print(f"✅ Video URL: {output_data['video_url']}")
        elif 'video' in output_data:
            print("⚠️ Upload failed, received base64 fallback")
            video_file = decode_base64_video(output_data['video'], "fallback_video.mp4")
            if video_file:
                print(f"🎉 Fallback video saved: {video_file}")
    
    print("\n🎉 Testing Complete!")
    print("Check the generated MP4 files in this directory!")

if __name__ == "__main__":
    main()