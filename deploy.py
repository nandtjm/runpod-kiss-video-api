#!/usr/bin/env python3
"""
RunPod Deployment Script for Kiss Video Generator
"""

import os
import json
import subprocess
import requests
from typing import Dict, Any
from runpod_config import RUNPOD_CONFIG, get_runpod_endpoint_config

def build_docker_image():
    """Build Docker image for RunPod deployment"""
    image_name = RUNPOD_CONFIG["image"]
    
    print(f"Building Docker image: {image_name}")
    
    try:
        # Build Docker image
        subprocess.run([
            "docker", "build", 
            "-t", image_name,
            "."
        ], check=True)
        
        print(f"✅ Docker image built successfully: {image_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Docker image: {e}")
        return False

def push_docker_image():
    """Push Docker image to registry"""
    image_name = RUNPOD_CONFIG["image"]
    
    print(f"Pushing Docker image: {image_name}")
    
    try:
        # Push to Docker Hub (or your preferred registry)
        subprocess.run([
            "docker", "push", image_name
        ], check=True)
        
        print(f"✅ Docker image pushed successfully: {image_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push Docker image: {e}")
        return False

def create_runpod_endpoint():
    """Create RunPod serverless endpoint"""
    
    # You'll need to set your RunPod API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ RUNPOD_API_KEY environment variable not set")
        return False
    
    endpoint_config = get_runpod_endpoint_config()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # RunPod API endpoint for creating serverless endpoints
    url = "https://api.runpod.ai/v2/endpoints"
    
    payload = {
        "name": RUNPOD_CONFIG["name"],
        "image": RUNPOD_CONFIG["image"],
        "gpu_ids": RUNPOD_CONFIG["gpu_type"],
        "locations": "US,EU",  # Available locations
        "idle_timeout": 5,     # Seconds before scaling to 0
        "execution_timeout": 600,  # Max execution time
        "env": RUNPOD_CONFIG["env"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        endpoint_id = result.get("id")
        endpoint_url = result.get("url")
        
        print(f"✅ RunPod endpoint created successfully!")
        print(f"Endpoint ID: {endpoint_id}")
        print(f"Endpoint URL: {endpoint_url}")
        
        # Save endpoint info
        with open("endpoint_info.json", "w") as f:
            json.dump({
                "endpoint_id": endpoint_id,
                "endpoint_url": endpoint_url,
                "created_at": result.get("created_at")
            }, f, indent=2)
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Failed to create RunPod endpoint: {e}")
        return False

def test_endpoint():
    """Test the deployed endpoint"""
    
    # Load endpoint info
    try:
        with open("endpoint_info.json", "r") as f:
            endpoint_info = json.load(f)
            endpoint_url = endpoint_info["endpoint_url"]
    except FileNotFoundError:
        print("❌ endpoint_info.json not found. Deploy endpoint first.")
        return False
    
    # Test payload (you'll need actual base64 encoded images)
    test_payload = {
        "input": {
            "source_image": "base64_encoded_source_image_here",
            "target_image": "base64_encoded_target_image_here", 
            "model": "wan_ai",
            "parameters": {
                "num_frames": 16,
                "guidance_scale": 7.5,
                "prompt": "Two people kissing romantically"
            }
        }
    }
    
    api_key = os.getenv("RUNPOD_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing endpoint...")
    
    try:
        response = requests.post(f"{endpoint_url}/run", headers=headers, json=test_payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Endpoint test successful!")
        print(f"Status: {result.get('status')}")
        
        return True
        
    except requests.RequestException as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

def main():
    """Main deployment process"""
    print("🚀 Starting RunPod Kiss Video Generator deployment...")
    
    steps = [
        ("Building Docker image", build_docker_image),
        ("Pushing Docker image", push_docker_image), 
        ("Creating RunPod endpoint", create_runpod_endpoint),
        ("Testing endpoint", test_endpoint)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Deployment failed at: {step_name}")
            return False
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your main app's API endpoint URL")
    print("2. Test with real image data")
    print("3. Monitor performance and costs in RunPod dashboard")
    
    return True

if __name__ == "__main__":
    main()