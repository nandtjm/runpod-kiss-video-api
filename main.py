#!/usr/bin/env python3
"""
RunPod Kiss Video Generation API
Main entry point for the RunPod serverless function
"""

import os
import json
import base64
import tempfile
from typing import Dict, Any, Optional
import torch
import subprocess
import sys
from huggingface_hub import hf_hub_download
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import runpod

def load_kiss_models():
    """Load Wan-AI models and Remade-AI LoRA for kiss generation"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    models = {}
    
    try:
        # Load Wan-AI I2V 14B model (base model for kissing LoRA)
        print("Loading Wan-AI I2V 14B model...")
        wan_model_path = "/app/models/Wan2.1-I2V-14B-720P"
        
        # Check if model exists, if not download it
        if not os.path.exists(wan_model_path):
            print("Downloading Wan-AI I2V model...")
            os.makedirs("/app/models", exist_ok=True)
            subprocess.run([
                "huggingface-cli", "download", 
                "Wan-AI/Wan2.1-I2V-14B-720P",
                "--local-dir", wan_model_path
            ], check=True)
        
        models['wan_ai'] = {
            'model_path': wan_model_path,
            'type': 'wan_i2v',
            'resolution': (1280, 720),
            'loaded': True
        }
        
    except Exception as e:
        print(f"Failed to load Wan-AI model: {e}")
        models['wan_ai'] = None
    
    try:
        # Load Remade-AI kissing LoRA
        print("Loading Remade-AI kissing LoRA...")
        lora_path = "/app/models/kissing-lora"
        
        # Download LoRA if not exists
        if not os.path.exists(lora_path):
            print("Downloading Remade-AI kissing LoRA...")
            os.makedirs(lora_path, exist_ok=True)
            subprocess.run([
                "huggingface-cli", "download", 
                "Remade-AI/kissing",
                "--local-dir", lora_path
            ], check=True)
        
        models['remade_ai'] = {
            'base_model': wan_model_path,
            'lora_path': lora_path,
            'type': 'wan_lora',
            'lora_strength': 1.0,
            'guidance_scale': 6.0,
            'flow_shift': 5.0,
            'loaded': True
        }
        
    except Exception as e:
        print(f"Failed to load Remade-AI LoRA: {e}")
        models['remade_ai'] = None
    
    return models

def preprocess_images(source_image_data: str, target_image_data: str) -> tuple:
    """Preprocess source and target images"""
    # Decode base64 images
    source_image = Image.open(BytesIO(base64.b64decode(source_image_data)))
    target_image = Image.open(BytesIO(base64.b64decode(target_image_data)))
    
    # Convert to RGB if needed
    if source_image.mode != 'RGB':
        source_image = source_image.convert('RGB')
    if target_image.mode != 'RGB':
        target_image = target_image.convert('RGB')
    
    # Resize to appropriate dimensions based on model
    # Wan-AI I2V supports 720P (1280x720) and 480P (832x480)
    source_image = source_image.resize((1280, 720))
    target_image = target_image.resize((1280, 720))
    
    return source_image, target_image

def generate_kiss_video(models: Dict, source_image: Image.Image, target_image: Image.Image, 
                       model_name: str = "remade_ai", **kwargs) -> Optional[str]:
    """Generate kiss video using Wan-AI base model with Remade-AI kissing LoRA"""
    
    if model_name not in models or models[model_name] is None:
        raise ValueError(f"Model {model_name} not available")
    
    model_config = models[model_name]
    
    try:
        # Save source image temporarily
        temp_image_path = tempfile.mktemp(suffix='.jpg')
        source_image.save(temp_image_path, 'JPEG')
        
        # Create output path
        output_path = tempfile.mktemp(suffix='.mp4')
        
        if model_name == "wan_ai":
            # Basic Wan-AI I2V generation (without LoRA)
            prompt = kwargs.get('prompt', "Two people in a romantic scene, cinematic lighting, high quality")
            
            cmd = [
                "python", "/app/generate.py",
                "--task", "i2v-14B",
                "--size", "1280*720",
                "--ckpt_dir", model_config['model_path'],
                "--image", temp_image_path,
                "--prompt", prompt,
                "--output", output_path,
                "--sample_guide_scale", str(kwargs.get('guidance_scale', 6.0)),
                "--sample_shift", str(kwargs.get('sample_shift', 8))
            ]
            
        elif model_name == "remade_ai":
            # Wan-AI with Remade-AI kissing LoRA
            # Use special k144ing trigger word for kissing LoRA
            base_prompt = kwargs.get('prompt', "Two heads, cinematic romantic lighting")
            kissing_prompt = f"{base_prompt}, k144ing kissing softly"
            
            cmd = [
                "python", "/app/generate_with_lora.py",
                "--task", "i2v-14B",
                "--size", "1280*720", 
                "--ckpt_dir", model_config['base_model'],
                "--lora_path", model_config['lora_path'],
                "--lora_strength", str(model_config['lora_strength']),
                "--image", temp_image_path,
                "--prompt", kissing_prompt,
                "--output", output_path,
                "--sample_guide_scale", str(model_config['guidance_scale']),
                "--flow_shift", str(model_config['flow_shift'])
            ]
        
        # Run the generation command
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"Generation failed: {result.stderr}")
            return None
        
        # Clean up temporary image
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        if os.path.exists(output_path):
            return output_path
        else:
            print("Output video file not generated")
            return None
        
    except Exception as e:
        print(f"Error generating video with {model_name}: {e}")
        return None

def save_video_frames(frames, output_path: str = None, fps: int = 24) -> str:
    """Save video frames to MP4 file"""
    if output_path is None:
        output_path = tempfile.mktemp(suffix='.mp4')
    
    # Get frame dimensions
    if isinstance(frames[0], Image.Image):
        height, width = frames[0].size[1], frames[0].size[0]
        frames = [np.array(frame) for frame in frames]
    else:
        height, width = frames[0].shape[:2]
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Write frames
    for frame in frames:
        if len(frame.shape) == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        video_writer.write(frame)
    
    video_writer.release()
    return output_path

def upload_to_storage(video_path: str) -> str:
    """Upload generated video to cloud storage (implement based on your storage solution)"""
    # Placeholder - implement actual upload logic
    # This could be AWS S3, Google Cloud Storage, etc.
    
    # For now, convert to base64 for return
    with open(video_path, 'rb') as f:
        video_data = base64.b64encode(f.read()).decode('utf-8')
    
    return video_data

def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """Main RunPod handler function"""
    try:
        # Extract input from job
        job_input = job.get('input', {})
        
        # Parse input
        source_image_data = job_input.get('source_image')
        target_image_data = job_input.get('target_image')
        model_name = job_input.get('model', 'wan_ai')
        
        if not source_image_data or not target_image_data:
            return {
                'error': 'Missing source_image or target_image in input'
            }
        
        # Load models (cache these in production)
        models = load_kiss_models()
        
        # Preprocess images
        source_image, target_image = preprocess_images(source_image_data, target_image_data)
        
        # Generate video
        video_path = generate_kiss_video(
            models, 
            source_image, 
            target_image, 
            model_name=model_name,
            **job_input.get('parameters', {})
        )
        
        if not video_path:
            return {
                'error': 'Failed to generate video'
            }
        
        # Upload to storage
        video_data = upload_to_storage(video_path)
        
        # Clean up temporary file
        if os.path.exists(video_path):
            os.remove(video_path)
        
        return {
            'status': 'success',
            'video_data': video_data,
            'model_used': model_name,
            'message': 'Kiss video generated successfully'
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed'
        }

# This file is imported by rp_handler.py
# The handler function is defined above and exported for use