#!/usr/bin/env python3
"""
Test API handler without model downloads
"""

import runpod
import sys
import os
import json
from PIL import Image
import requests
from io import BytesIO
import base64

def test_handler(job):
    """Test handler that validates inputs without downloading models"""
    try:
        job_input = job.get('input', {})
        
        source_image_data = job_input.get('source_image')
        target_image_data = job_input.get('target_image')
        model_name = job_input.get('model', 'wan_ai')
        
        if not source_image_data or not target_image_data:
            return {
                'error': 'Missing source_image or target_image in input',
                'status': 'failed'
            }
        
        print(f"Testing with model: {model_name}")
        print(f"Source image type: {'URL' if source_image_data.startswith('http') else 'base64'}")
        print(f"Target image type: {'URL' if target_image_data.startswith('http') else 'base64'}")
        
        # Test image loading without processing
        def test_image_load(image_data, name):
            try:
                if image_data.startswith(('http://', 'https://')):
                    print(f"Testing {name} URL: {image_data}")
                    
                    # Add proper headers to avoid blocking
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    response = requests.get(image_data, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    print(f"Response status: {response.status_code}")
                    print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
                    print(f"Content-Length: {len(response.content)} bytes")
                    
                    # Debug first few bytes
                    content_preview = response.content[:100]
                    print(f"Content preview: {content_preview}")
                    
                    # Check if it's actually HTML instead of image
                    if response.content.startswith(b'<!DOCTYPE') or response.content.startswith(b'<html'):
                        raise ValueError(f"URL returned HTML page instead of image")
                    
                    img = Image.open(BytesIO(response.content))
                    print(f"✅ {name} loaded: {img.size} {img.mode}")
                    return True
                else:
                    if image_data.startswith('data:image/'):
                        image_data = image_data.split(',')[1]
                    image_data = image_data + '=' * (4 - len(image_data) % 4) % 4
                    img = Image.open(BytesIO(base64.b64decode(image_data)))
                    print(f"✅ {name} loaded: {img.size} {img.mode}")
                    return True
            except Exception as e:
                print(f"❌ {name} failed: {e}")
                return False
        
        source_ok = test_image_load(source_image_data, "Source image")
        target_ok = test_image_load(target_image_data, "Target image")
        
        if not source_ok or not target_ok:
            return {
                'error': 'Failed to load one or both images',
                'status': 'failed'
            }
        
        # Simulate successful processing
        return {
            'status': 'success',
            'message': 'Image validation successful! Models would process here.',
            'model': model_name,
            'debug': {
                'source_image_loaded': source_ok,
                'target_image_loaded': target_ok,
                'model_requested': model_name
            }
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed'
        }

if __name__ == "__main__":
    print("=== TEST API HANDLER STARTING ===")
    print("This version tests input validation without downloading models")
    runpod.serverless.start({"handler": test_handler})