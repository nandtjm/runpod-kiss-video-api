#!/usr/bin/env python3
"""
ModelScope Download Script - Alternative to Hugging Face
"""

import os
import sys

# Add modelscope to path
sys.path.append('/Users/nandlal/Library/Python/3.9/lib/python/site-packages')

try:
    from modelscope import snapshot_download
except ImportError:
    print("Installing modelscope...")
    os.system("pip3 install modelscope")
    from modelscope import snapshot_download

def download_models():
    """Download models using ModelScope"""
    
    models_dir = "./models"
    os.makedirs(models_dir, exist_ok=True)
    
    models = [
        {
            "name": "Wan-AI I2V 14B Model",
            "repo": "Wan-AI/Wan2.1-I2V-14B-720P", 
            "local_dir": f"{models_dir}/Wan2.1-I2V-14B-720P"
        }
    ]
    
    for model in models:
        print(f"Downloading {model['name']} via ModelScope...")
        print(f"From: {model['repo']}")
        print(f"To: {model['local_dir']}")
        
        try:
            snapshot_download(
                model_id=model['repo'],
                local_dir=model['local_dir'],
                resume_download=True
            )
            print(f"✅ Downloaded {model['name']}")
            return True
        except Exception as e:
            print(f"❌ Failed to download {model['name']}: {e}")
            
            # Try alternative method - using CLI
            print("Trying ModelScope CLI...")
            cmd = f"python3 -m modelscope.cli download Wan-AI/Wan2.1-I2V-14B-720P --local_dir {model['local_dir']}"
            result = os.system(cmd)
            if result == 0:
                print(f"✅ Downloaded {model['name']} via CLI")
                return True
            else:
                return False
    
    return True

if __name__ == "__main__":
    print("Starting ModelScope model download...")
    success = download_models()
    if success:
        print("✅ All models downloaded successfully!")
    else:
        print("❌ Model download failed")