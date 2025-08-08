#!/usr/bin/env python3
"""
Check RunPod job results and download videos
"""

import requests
import base64
import json
import time
from datetime import datetime

# Configuration - same as test_local.py
API_KEY = "YOUR_RUNPOD_API_KEY"
ENDPOINT_ID = "63wukybus821bc"

def check_job_status(job_id):
    """Check status of a RunPod job"""
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error checking job {job_id}: {response.status_code}")
        return None

def decode_and_save_video(base64_data, filename):
    """Decode base64 video and save as MP4"""
    try:
        video_bytes = base64.b64decode(base64_data)
        with open(filename, 'wb') as f:
            f.write(video_bytes)
        
        file_size = len(video_bytes)
        print(f"✅ Video saved: {filename}")
        print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        return filename
    except Exception as e:
        print(f"❌ Failed to decode video: {e}")
        return None

def main():
    # These are the job IDs from the test run - replace with your actual job IDs
    job_ids = [
        "7bc095f3-1f25-4a59-ae2c-ef7b47cac0e1-e2",  # Base64 test  
        "59f6aa86-1e78-4e31-be65-211c96098560-e1"   # URL test
    ]
    
    print("🔍 Checking RunPod job results...")
    print("=" * 40)
    
    for i, job_id in enumerate(job_ids, 1):
        print(f"\n📋 Checking Job {i}: {job_id}")
        print("-" * 50)
        
        result = check_job_status(job_id)
        if result:
            status = result.get('status', 'UNKNOWN')
            print(f"📊 Status: {status}")
            
            if status == 'COMPLETED':
                output = result.get('output', {})
                
                # Check for video URL
                if 'video_url' in output:
                    print(f"🔗 Video URL: {output['video_url']}")
                    
                # Check for base64 video
                elif 'video' in output:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"kiss_video_job{i}_{timestamp}.mp4"
                    decode_and_save_video(output['video'], filename)
                    
                # Print other details
                if 'processing_time' in output:
                    print(f"⏱️ Processing time: {output['processing_time']}")
                if 'model_used' in output:
                    print(f"🤖 Model: {output['model_used']}")
                    
            elif status == 'IN_PROGRESS':
                print("🔄 Job still processing...")
            elif status == 'FAILED':
                print(f"❌ Job failed: {result.get('error', 'Unknown error')}")
        else:
            print("❌ Failed to get job status")
    
    print("\n🎉 Results check complete!")

if __name__ == "__main__":
    main()