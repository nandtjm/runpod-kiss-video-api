#!/usr/bin/env python3
"""
Test script to decode base64 video from RunPod response
Run this on your local machine to preview the generated videos
"""

import base64
import tempfile
import os
import json
from pathlib import Path

def decode_video_from_response(response_data, output_filename="decoded_video.mp4"):
    """
    Decode base64 video from RunPod response and save as MP4
    
    Args:
        response_data: The JSON response from RunPod (dict or JSON string)
        output_filename: Output MP4 filename
    
    Returns:
        str: Path to the saved MP4 file
    """
    try:
        # Parse response if it's a string
        if isinstance(response_data, str):
            response_data = json.loads(response_data)
        
        # Extract video data
        if 'output' in response_data and 'video' in response_data['output']:
            video_b64 = response_data['output']['video']
            print(f"📹 Found video in response (status: {response_data['output']['status']})")
        elif 'video' in response_data:
            video_b64 = response_data['video']
            print("📹 Found video in direct response")
        else:
            raise ValueError("No video found in response data")
        
        # Decode base64
        print(f"🔄 Decoding base64 video ({len(video_b64)} characters)...")
        video_bytes = base64.b64decode(video_b64)
        
        # Save to file
        output_path = Path(output_filename)
        with open(output_path, 'wb') as f:
            f.write(video_bytes)
        
        print(f"✅ Video saved to: {output_path.absolute()}")
        print(f"📊 File size: {len(video_bytes) / 1024:.1f} KB")
        
        return str(output_path.absolute())
        
    except Exception as e:
        print(f"❌ Error decoding video: {e}")
        return None

def decode_video_from_base64_string(video_b64_string, output_filename="decoded_video.mp4"):
    """
    Decode base64 string directly to MP4
    
    Args:
        video_b64_string: Raw base64 video string
        output_filename: Output MP4 filename
    """
    try:
        print(f"🔄 Decoding base64 video ({len(video_b64_string)} characters)...")
        video_bytes = base64.b64decode(video_b64_string)
        
        output_path = Path(output_filename)
        with open(output_path, 'wb') as f:
            f.write(video_bytes)
        
        print(f"✅ Video saved to: {output_path.absolute()}")
        print(f"📊 File size: {len(video_bytes) / 1024:.1f} KB")
        
        return str(output_path.absolute())
        
    except Exception as e:
        print(f"❌ Error decoding video: {e}")
        return None

def preview_video_info(video_path):
    """
    Show video information using ffprobe if available
    """
    try:
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            print("\n📊 Video Information:")
            print(f"Format: {info['format']['format_name']}")
            print(f"Duration: {float(info['format']['duration']):.2f} seconds")
            
            for stream in info['streams']:
                if stream['codec_type'] == 'video':
                    print(f"Resolution: {stream['width']}x{stream['height']}")
                    print(f"Frame rate: {stream['r_frame_rate']}")
                    print(f"Codec: {stream['codec_name']}")
        else:
            print("⚠️ ffprobe not available - install FFmpeg for video info")
            
    except ImportError:
        print("⚠️ Install FFmpeg to see detailed video information")
    except Exception as e:
        print(f"⚠️ Could not get video info: {e}")

# Example usage functions

def test_with_runpod_response():
    """Test with a typical RunPod response"""
    
    # Example response from your RunPod test
    example_response = {
        "output": {
            "model_used": "morphing_fallback",
            "processing_time": "4.7s", 
            "status": "fallback_success",
            "video": "AAAAHGZ0eXBpc29tAAACAGlzb21pc28ybXA0MQAAAAhmcmVlAAljBG1kYXQAAAGzABAHAAABthBgsYL10yS4/emaLb1IfKOse362drV9W9eNWm5afoPYLGlcpGIhhOOeREog9Pw3wFafqYWTjzPWQTYWY925OFjCxu8KD2e7HXuvn8O+cljTnTeN/1ZHVPXj9d/G9tZHDe+N5v483/jbe+Dp6mz5x23uQk3T/2Oav/H99eOZj/G/nOPzn2PfV8OU65zeFR6q9l57fb0Qs2S3J7hZMFmf5UY6IPayI5o814fZ9+8Gz+dObj0w2sb+q8f9VyNvTe9XsBPkQvjnTvZbxnKzVVWbkU8NwkeVQvpbN4V4QyZ0xnaol2oslowOqNfrLXm4tP5NksX4+dP0rkz67488/i1M0/4/7/Y/qfx5xuR/vzQ268PaS5......C1pbHN0AAAAJal0b28AAAAdZGF0YQAAAAEAAAAATGF2ZjU5LjI3LjEwMA=="
        }
    }
    
    video_path = decode_video_from_response(example_response, "fallback_test.mp4")
    if video_path:
        preview_video_info(video_path)
        print(f"\n🎬 Open this file to view the video: {video_path}")

def test_with_base64_string():
    """Test with direct base64 string"""
    
    # Your base64 video string here
    video_b64 = input("📋 Paste your base64 video string here: ").strip()
    
    if video_b64:
        video_path = decode_video_from_base64_string(video_b64, "my_video.mp4")
        if video_path:
            preview_video_info(video_path)
            print(f"\n🎬 Open this file to view the video: {video_path}")

if __name__ == "__main__":
    print("🎬 RunPod Video Decoder")
    print("=" * 40)
    print("1. Test with example fallback response")
    print("2. Decode your own base64 video string") 
    print("3. Decode from JSON response file")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        test_with_runpod_response()
    elif choice == "2":
        test_with_base64_string()
    elif choice == "3":
        json_file = input("Enter path to JSON response file: ").strip()
        if os.path.exists(json_file):
            with open(json_file) as f:
                response_data = json.load(f)
            video_path = decode_video_from_response(response_data, "decoded_from_file.mp4")
            if video_path:
                preview_video_info(video_path)
                print(f"\n🎬 Open this file to view the video: {video_path}")
        else:
            print("❌ File not found")
    else:
        print("❌ Invalid choice")