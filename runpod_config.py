"""
RunPod Configuration and Deployment Settings
"""

import os
from typing import Dict, Any

# RunPod Configuration
RUNPOD_CONFIG = {
    "name": "kiss-video-generator",
    "image": "your-dockerhub-username/kiss-video-generator:latest",
    "gpu_count": 1,
    "gpu_type": "NVIDIA GeForce RTX 4090",
    "memory": 32,  # GB
    "disk": 50,    # GB
    "ports": "8000/http",
    "env": {
        "MODEL_CACHE_DIR": "/runpod-volume/models",
        "TEMP_DIR": "/runpod-volume/temp",
        "HUGGINGFACE_HUB_CACHE": "/runpod-volume/hf_cache",
        "TORCH_HOME": "/runpod-volume/torch",
    }
}

# Model Configuration
MODEL_CONFIG = {
    "wan_ai": {
        "model_id": "Wan-AI/kissing-video-generation",
        "model_type": "image-to-video",
        "precision": "fp16",
        "max_frames": 24,
        "resolution": (512, 512),
        "memory_usage": "8GB"
    },
    "remade_ai": {
        "model_id": "Remade-AI/kissing", 
        "model_type": "image-to-video",
        "precision": "fp16",
        "max_frames": 32,
        "resolution": (768, 768),
        "memory_usage": "12GB"
    }
}

# Generation Parameters
DEFAULT_PARAMS = {
    "num_frames": 16,
    "fps": 24,
    "guidance_scale": 7.5,
    "num_inference_steps": 50,
    "strength": 0.8,
    "seed": -1,  # Random seed if -1
    "prompt": "Two people kissing romantically, smooth motion, cinematic quality",
    "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy"
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "use_xformers": True,
    "use_attention_slicing": True,
    "use_cpu_offload": False,  # Set to True if GPU memory is limited
    "batch_size": 1,
    "max_concurrent_requests": 3,
    "timeout_seconds": 300
}

def get_runpod_endpoint_config() -> Dict[str, Any]:
    """Get RunPod endpoint configuration"""
    return {
        "handler": "main.handler",
        "runtime": {
            "python_version": "3.10",
            "cuda_version": "11.8"
        },
        "build": {
            "python_packages": "requirements.txt",
            "system_packages": [
                "git",
                "wget", 
                "curl",
                "unzip",
                "libgl1-mesa-glx",
                "libglib2.0-0"
            ]
        },
        "resources": {
            "gpu": {
                "type": "NVIDIA GeForce RTX 4090",
                "count": 1,
                "memory": "24GB"
            },
            "cpu": {
                "cores": 8,
                "memory": "32GB"
            },
            "storage": "50GB"
        }
    }