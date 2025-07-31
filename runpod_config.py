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
    "disk": 100,   # GB (increased for model storage)
    "ports": "8000/http",
    "env": {
        "MODEL_CACHE_DIR": "/runpod-volume/models",
        "TEMP_DIR": "/runpod-volume/temp",
        "HUGGINGFACE_HUB_CACHE": "/runpod-volume/hf_cache",
        "TORCH_HOME": "/runpod-volume/torch",
        "HF_HOME": "/runpod-volume/hf_cache",
        "TRANSFORMERS_CACHE": "/runpod-volume/transformers_cache",
    }
}

# Model Configuration
MODEL_CONFIG = {
    "wan_ai": {
        "model_id": "Wan-AI/Wan2.1-I2V-14B-720P",
        "model_type": "image-to-video",
        "precision": "fp16",
        "resolution": (1280, 720),
        "memory_usage": "16GB",
        "recommended_settings": {
            "guidance_scale": 6.0,
            "sample_shift": 8,
            "fps": 24
        }
    },
    "remade_ai": {
        "model_id": "Remade-AI/kissing", 
        "base_model": "Wan-AI/Wan2.1-I2V-14B-720P",
        "model_type": "lora",
        "precision": "fp16",
        "resolution": (1280, 720),
        "memory_usage": "16GB",
        "lora_settings": {
            "lora_strength": 1.0,
            "guidance_scale": 6.0,
            "flow_shift": 5.0
        },
        "trigger_word": "k144ing kissing",
        "training_info": {
            "epochs": 30,
            "training_data": "50 seconds of video with 11 kissing clips"
        }
    }
}

# Generation Parameters
DEFAULT_PARAMS = {
    "wan_ai": {
        "fps": 24,
        "guidance_scale": 6.0,
        "sample_shift": 8,
        "seed": -1,
        "prompt": "Two people in a romantic scene, cinematic lighting, high quality",
        "resolution": "1280*720"
    },
    "remade_ai": {
        "fps": 24,
        "lora_strength": 1.0,
        "guidance_scale": 6.0,
        "flow_shift": 5.0,
        "seed": -1,
        "prompt": "Two heads, cinematic romantic lighting, k144ing kissing softly",
        "resolution": "1280*720"
    }
}

# Example prompts for Remade-AI kissing LoRA
EXAMPLE_PROMPTS = {
    "mountain_scene": "A man and a woman wearing jackets and hats are standing close together in the snowy mountains. The man is standing facing the woman, then they engage in k144ing kissing.",
    "passionate_scene": "A man with a beard is shown smiling. A woman comes into the scene and starts passionately k144ing kissing the man.",
    "lake_scene": "A man and a woman are embracing near a lake with mountains in the background. They are k144ing kissing, while still embracing each other.",
    "cinematic": "Two heads, cinematic romantic lighting, k144ing kissing softly"
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