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
from transformers import pipeline
from diffusers import StableDiffusionPipeline
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO

def download_input():
    """Download input data for the RunPod job"""
    job_input = json.loads(os.environ.get('RUNPOD_INPUT', '{}'))
    return job_input

def load_kiss_models():
    """Load Hugging Face kiss generation models"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    models = {}
    
    try:
        # Load Wan-AI kissing model (placeholder - replace with actual model)
        models['wan_ai'] = pipeline(
            "image-to-video",
            model="Wan-AI/kissing-video-generation",
            device=device,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
    except Exception as e:
        print(f"Failed to load Wan-AI model: {e}")
        models['wan_ai'] = None
    
    try:
        # Load Remade-AI kissing model (placeholder - replace with actual model)
        models['remade_ai'] = pipeline(
            "image-to-video", 
            model="Remade-AI/kissing",
            device=device,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
    except Exception as e:
        print(f"Failed to load Remade-AI model: {e}")
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
    
    # Resize to standard dimensions (512x512 for most models)
    source_image = source_image.resize((512, 512))
    target_image = target_image.resize((512, 512))
    
    return source_image, target_image

def generate_kiss_video(models: Dict, source_image: Image.Image, target_image: Image.Image, 
                       model_name: str = "wan_ai", **kwargs) -> Optional[str]:
    """Generate kiss video using specified model"""
    
    if model_name not in models or models[model_name] is None:
        raise ValueError(f"Model {model_name} not available")
    
    model = models[model_name]
    
    try:
        # Create prompt for kiss video generation
        prompt = kwargs.get('prompt', "Two people kissing romantically, smooth motion, high quality")
        
        # Generate video frames
        if model_name == "wan_ai":
            result = model(
                prompt=prompt,
                image=source_image,
                target_image=target_image,
                num_frames=kwargs.get('num_frames', 16),
                guidance_scale=kwargs.get('guidance_scale', 7.5),
                num_inference_steps=kwargs.get('num_inference_steps', 50)
            )
        elif model_name == "remade_ai":
            result = model(
                prompt=prompt,
                image=source_image,
                target_image=target_image,
                num_frames=kwargs.get('num_frames', 24),
                guidance_scale=kwargs.get('guidance_scale', 8.0),
                num_inference_steps=kwargs.get('num_inference_steps', 40)
            )
        
        # Convert result to video file
        video_path = save_video_frames(result.frames if hasattr(result, 'frames') else result)
        
        return video_path
        
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

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """Main RunPod handler function"""
    try:
        # Parse input
        source_image_data = event.get('source_image')
        target_image_data = event.get('target_image')
        model_name = event.get('model', 'wan_ai')
        
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
            **event.get('parameters', {})
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

if __name__ == "__main__":
    # Test locally
    test_input = {
        'source_image': 'base64_encoded_image_data_here',
        'target_image': 'base64_encoded_image_data_here',
        'model': 'wan_ai',
        'parameters': {
            'num_frames': 16,
            'guidance_scale': 7.5,
            'prompt': 'Two people kissing romantically'
        }
    }
    
    result = handler(test_input)
    print(json.dumps(result, indent=2))