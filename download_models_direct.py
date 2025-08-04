#!/usr/bin/env python3
"""
Direct Model Download Script using huggingface_hub Python API
"""

import os
from huggingface_hub import snapshot_download
from pathlib import Path

def download_models():
    """Download models using Python API"""
    
    models_dir = "./models"
    os.makedirs(models_dir, exist_ok=True)
    
    models = [
        {
            "name": "Wan-AI I2V 14B Model",
            "repo": "Wan-AI/Wan2.1-I2V-14B-720P", 
            "local_dir": f"{models_dir}/Wan2.1-I2V-14B-720P"
        },
        {
            "name": "Kissing LoRA",
            "repo": "Remade-AI/kissing-lora",
            "local_dir": f"{models_dir}/kissing-lora"
        }
    ]
    
    for model in models:
        print(f"Downloading {model['name']} (~28GB)...")
        print(f"From: {model['repo']}")
        print(f"To: {model['local_dir']}")
        
        try:
            snapshot_download(
                repo_id=model['repo'],
                local_dir=model['local_dir'],
                resume_download=True
            )
            print(f"✅ Downloaded {model['name']}")
        except Exception as e:
            print(f"❌ Failed to download {model['name']}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Starting direct model download...")
    success = download_models()
    if success:
        print("✅ All models downloaded successfully!")
    else:
        print("❌ Model download failed")