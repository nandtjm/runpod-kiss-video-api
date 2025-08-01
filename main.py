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
from huggingface_hub import hf_hub_download, snapshot_download
import cv2
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import runpod

def download_model_from_hf(repo_id: str, local_dir: str, timeout: int = 300) -> bool:
    """Download model from Hugging Face Hub with timeout and progress tracking"""
    try:
        import time
        from threading import Thread
        import queue
        
        print(f"Downloading {repo_id} to {local_dir}...")
        os.makedirs(local_dir, exist_ok=True)
        
        # Use a queue to communicate between threads
        result_queue = queue.Queue()
        
        def download_worker():
            try:
                snapshot_download(
                    repo_id=repo_id,
                    local_dir=local_dir,
                    resume_download=True,
                    allow_patterns=["*.json", "*.bin", "*.safetensors", "*.txt", "*.py"],
                    ignore_patterns=["*.git*", "*.md", "*.lock"]
                )
                result_queue.put(("success", None))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # Start download in separate thread with timeout
        download_thread = Thread(target=download_worker)
        download_thread.daemon = True
        download_thread.start()
        
        # Wait for completion or timeout
        download_thread.join(timeout=timeout)
        
        if download_thread.is_alive():
            print(f"Download timeout ({timeout}s) for {repo_id}")
            return False
        
        # Check result
        try:
            status, error = result_queue.get_nowait()
            if status == "success":
                print(f"✅ Successfully downloaded {repo_id}")
                return True
            else:
                print(f"❌ Download failed for {repo_id}: {error}")
                return False
        except queue.Empty:
            print(f"❌ Download failed for {repo_id}: No result returned")
            return False
            
    except Exception as e:
        print(f"❌ Download error for {repo_id}: {e}")
        return False

def load_kiss_models():
    """Load Wan-AI models and Remade-AI LoRA for kiss generation with runtime download"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    models = {}
    
    # Use volume storage for models with fallback to local cache
    model_cache_dir = os.getenv("MODEL_CACHE_DIR", "/workspace/models")
    os.makedirs(model_cache_dir, exist_ok=True)
    
    # Model configurations
    model_configs = {
        'wan_ai': {
            'repo_id': 'Wan-AI/Wan2.1-I2V-14B-720P',
            'local_dir': f"{model_cache_dir}/Wan2.1-I2V-14B-720P",
            'timeout': 180  # 3 minutes for base model
        },
        'remade_ai': {
            'repo_id': 'Remade-AI/kissing',
            'local_dir': f"{model_cache_dir}/kissing-lora", 
            'timeout': 120  # 2 minutes for LoRA
        }
    }
    
    # Load Wan-AI I2V 14B model (base model)
    try:
        print("Loading Wan-AI I2V 14B model...")
        config = model_configs['wan_ai']
        wan_model_path = config['local_dir']
        
        # Check if model exists, if not try to download
        if not os.path.exists(wan_model_path) or not os.listdir(wan_model_path):
            print(f"Wan-AI model not found at {wan_model_path}, attempting download...")
            
            if not download_model_from_hf(config['repo_id'], wan_model_path, config['timeout']):
                print("Failed to download Wan-AI model")
                models['wan_ai'] = None
            else:
                models['wan_ai'] = {
                    'model_path': wan_model_path,
                    'type': 'wan_i2v',
                    'resolution': (1280, 720),
                    'loaded': True
                }
        else:
            print(f"✅ Wan-AI model found at {wan_model_path}")
            models['wan_ai'] = {
                'model_path': wan_model_path,
                'type': 'wan_i2v', 
                'resolution': (1280, 720),
                'loaded': True
            }
        
    except Exception as e:
        print(f"Failed to load Wan-AI model: {e}")
        models['wan_ai'] = None
    
    # Load Remade-AI kissing LoRA
    try:
        print("Loading Remade-AI kissing LoRA...")
        config = model_configs['remade_ai']
        lora_path = config['local_dir']
        
        # Check if LoRA exists, if not try to download
        if not os.path.exists(lora_path) or not os.listdir(lora_path):
            print(f"Remade-AI LoRA not found at {lora_path}, attempting download...")
            
            if not download_model_from_hf(config['repo_id'], lora_path, config['timeout']):
                print("Failed to download Remade-AI LoRA")
                models['remade_ai'] = None
            else:
                # Only create remade_ai model if base model is available
                if models.get('wan_ai') is not None:
                    models['remade_ai'] = {
                        'base_model': wan_model_path,
                        'lora_path': lora_path,
                        'type': 'wan_lora',
                        'lora_strength': 1.0,
                        'guidance_scale': 6.0,
                        'flow_shift': 5.0,
                        'loaded': True
                    }
                else:
                    print("Cannot create remade_ai model: base wan_ai model not available")
                    models['remade_ai'] = None
        else:
            print(f"✅ Remade-AI LoRA found at {lora_path}")
            # Only create remade_ai model if base model is available
            if models.get('wan_ai') is not None:
                models['remade_ai'] = {
                    'base_model': wan_model_path,
                    'lora_path': lora_path,
                    'type': 'wan_lora',
                    'lora_strength': 1.0,
                    'guidance_scale': 6.0,
                    'flow_shift': 5.0,
                    'loaded': True
                }
            else:
                print("Cannot create remade_ai model: base wan_ai model not available")
                models['remade_ai'] = None
        
    except Exception as e:
        print(f"Failed to load Remade-AI LoRA: {e}")
        models['remade_ai'] = None
    
    # Summary
    available_models = [k for k, v in models.items() if v is not None]
    unavailable_models = [k for k, v in models.items() if v is None]
    
    if available_models:
        print(f"✅ Available models: {', '.join(available_models)}")
    if unavailable_models:
        print(f"❌ Unavailable models: {', '.join(unavailable_models)}")
    
    return models

def preprocess_images(source_image_data: str, target_image_data: str) -> tuple:
    """Preprocess source and target images - supports both URLs and base64"""
    def load_image_from_input(image_data: str) -> Image.Image:
        """Load image from either URL or base64 data"""
        try:
            # Check if it's a URL
            if image_data.startswith(('http://', 'https://')):
                print(f"Loading image from URL: {image_data[:50]}...")
                
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
                
                # Check if it's actually HTML instead of image
                if response.content.startswith(b'<!DOCTYPE') or response.content.startswith(b'<html'):
                    raise ValueError(f"URL returned HTML page instead of image")
                
                return Image.open(BytesIO(response.content))
            
            # Handle base64 data
            else:
                # Remove data URL prefix if present
                if image_data.startswith('data:image/'):
                    image_data = image_data.split(',')[1]
                
                # Add padding if needed
                image_data = image_data + '=' * (4 - len(image_data) % 4) % 4
                
                # Decode base64
                return Image.open(BytesIO(base64.b64decode(image_data, validate=True)))
                
        except requests.RequestException as e:
            raise ValueError(f"Failed to download image from URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process image data: {str(e)}")
    
    try:
        source_image = load_image_from_input(source_image_data)
        target_image = load_image_from_input(target_image_data)
        
    except Exception as e:
        raise ValueError(f"Image processing error: {str(e)}. Please provide valid image URLs or base64 encoded data.")
    
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
        model_name = job_input.get('model', 'remade_ai')
        
        if not source_image_data or not target_image_data:
            return {
                'error': 'Missing source_image or target_image in input',
                'status': 'failed'
            }
        
        # Validate input data types
        if not isinstance(source_image_data, str) or not isinstance(target_image_data, str):
            return {
                'error': 'source_image and target_image must be base64 encoded strings',
                'status': 'failed'
            }
        
        # Load models (cache these in production)
        models = load_kiss_models()
        
        # Preprocess images with error handling
        try:
            source_image, target_image = preprocess_images(source_image_data, target_image_data)
        except ValueError as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
        
        # Check if requested model is available
        if model_name not in models or models[model_name] is None:
            available_models = [k for k, v in models.items() if v is not None]
            return {
                'error': f'Model {model_name} not available. Available models: {", ".join(available_models) if available_models else "None"}',
                'status': 'failed',
                'available_models': available_models
            }

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
                'error': 'Failed to generate video - check logs for details',
                'status': 'failed'
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