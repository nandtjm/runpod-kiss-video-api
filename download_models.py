#!/usr/bin/env python3
"""
Model Download Script for RunPod Kiss Video Generator
Run this script to pre-download all required models before deployment
"""

import os
import subprocess
import sys
from pathlib import Path

def download_models():
    """Download all required models for production deployment"""
    
    # Model cache directory
    model_cache_dir = os.getenv("MODEL_CACHE_DIR", "/workspace/models")
    print(f"Downloading models to: {model_cache_dir}")
    
    # Create cache directory
    os.makedirs(model_cache_dir, exist_ok=True)
    
    models_to_download = [
        {
            "name": "Wan-AI I2V 14B Model",
            "repo": "Wan-AI/Wan2.1-I2V-14B-720P",
            "local_dir": f"{model_cache_dir}/Wan2.1-I2V-14B-720P",
            "size": "~28GB"
        },
        {
            "name": "Remade-AI Kissing LoRA",
            "repo": "Remade-AI/kissing",
            "local_dir": f"{model_cache_dir}/kissing-lora",
            "size": "~1GB"
        }
    ]
    
    for model in models_to_download:
        print(f"\n{'='*60}")
        print(f"Downloading: {model['name']}")
        print(f"Repository: {model['repo']}")
        print(f"Size: {model['size']}")
        print(f"Local path: {model['local_dir']}")
        print(f"{'='*60}")
        
        if os.path.exists(model['local_dir']) and os.listdir(model['local_dir']):
            print(f"✅ Model already exists at {model['local_dir']}")
            continue
        
        try:
            # Create local directory
            os.makedirs(model['local_dir'], exist_ok=True)
            
            # Download with huggingface-cli
            cmd = [
                "huggingface-cli", "download",
                model['repo'],
                "--local-dir", model['local_dir'],
                "--resume-download"
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print(f"✅ Successfully downloaded {model['name']}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download {model['name']}")
            print(f"Error: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error downloading {model['name']}: {e}")
            return False
    
    print(f"\n{'='*60}")
    print("🎉 All models downloaded successfully!")
    print("You can now deploy your RunPod endpoint.")
    print(f"{'='*60}")
    
    return True

def verify_models():
    """Verify that all required models are present"""
    
    model_cache_dir = os.getenv("MODEL_CACHE_DIR", "/workspace/models")
    
    required_paths = [
        f"{model_cache_dir}/Wan2.1-I2V-14B-720P",
        f"{model_cache_dir}/kissing-lora"
    ]
    
    print("Verifying model installation...")
    
    all_present = True
    for path in required_paths:
        if os.path.exists(path) and os.listdir(path):
            print(f"✅ Found: {path}")
        else:
            print(f"❌ Missing: {path}")
            all_present = False
    
    if all_present:
        print("🎉 All required models are present!")
    else:
        print("❌ Some models are missing. Run download_models() first.")
    
    return all_present

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_models()
    else:
        print("Starting model download process...")
        print("This may take a long time depending on your internet connection.")
        print("The models are large (>25GB total).")
        
        if download_models():
            verify_models()
        else:
            print("❌ Model download failed. Please check the errors above.")
            sys.exit(1)

if __name__ == "__main__":
    main()