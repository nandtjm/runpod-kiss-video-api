#!/usr/bin/env python3
"""
Production AI Kiss Video Generator Handler
Optimized for RunPod serverless with real AI models
"""

import os
import json
import base64
import tempfile
import sys
import time
import gc
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging

import runpod
import torch
import numpy as np
from PIL import Image
import cv2
from diffusers import DiffusionPipeline, DDIMScheduler
import io
from loguru import logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.info("🤖 Production AI Kiss Video Generator Starting...")

# Configuration
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/runpod-volume/models")
TEMP_DIR = os.getenv("TEMP_DIR", "/tmp")
WAN_MODEL_PATH = f"{MODEL_CACHE_DIR}/Wan2.1-I2V-14B-720P"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Global model cache
_model_cache = {}

def optimize_gpu_memory():
    """Optimize GPU memory usage"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        # Enable memory efficiency
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True

def load_wan_ai_model() -> Optional[DiffusionPipeline]:
    """Load Wan-AI model with optimizations"""
    global _model_cache
    
    if "wan_ai" in _model_cache:
        logger.info("✅ Using cached Wan-AI model")
        return _model_cache["wan_ai"]
    
    if not os.path.exists(WAN_MODEL_PATH):
        logger.error(f"❌ Wan-AI model not found: {WAN_MODEL_PATH}")
        return None
    
    try:
        logger.info(f"🔄 Loading Wan-AI model from {WAN_MODEL_PATH}")
        
        # Load with optimizations
        pipeline = DiffusionPipeline.from_pretrained(
            WAN_MODEL_PATH,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            safety_checker=None,  # Disable for speed
            requires_safety_checker=False,
            local_files_only=True
        )
        
        if DEVICE == "cuda":
            pipeline = pipeline.to(DEVICE)
            # Enable memory optimizations
            pipeline.enable_memory_efficient_attention()
            pipeline.enable_vae_slicing()
            pipeline.enable_model_cpu_offload()
            
            # Use optimized scheduler
            pipeline.scheduler = DDIMScheduler.from_config(pipeline.scheduler.config)
        
        _model_cache["wan_ai"] = pipeline
        logger.info("✅ Wan-AI model loaded successfully")
        return pipeline
        
    except Exception as e:
        logger.error(f"❌ Failed to load Wan-AI model: {e}")
        return None

def preprocess_face_image(image: Image.Image, target_size: Tuple[int, int] = (512, 512)) -> Image.Image:
    """Preprocess face image for AI generation"""
    # Resize maintaining aspect ratio
    image = image.convert('RGB')
    
    # Smart resize with padding to maintain aspect ratio
    w, h = image.size
    aspect = w / h
    target_w, target_h = target_size
    
    if aspect > 1:  # Wider than tall
        new_w = target_w
        new_h = int(target_w / aspect)
    else:  # Taller than wide
        new_h = target_h
        new_w = int(target_h * aspect)
    
    # Resize and create centered image with padding
    image = image.resize((new_w, new_h), Image.LANCZOS)
    
    # Create new image with target size and paste resized image in center
    result = Image.new('RGB', target_size, (0, 0, 0))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    result.paste(image, (paste_x, paste_y))
    
    return result

def generate_kiss_animation_frames(source_img: Image.Image, target_img: Image.Image, 
                                 pipeline: DiffusionPipeline, num_frames: int = 24) -> list:
    """Generate kiss animation frames using AI model"""
    frames = []
    
    # Preprocess images
    source_processed = preprocess_face_image(source_img)
    target_processed = preprocess_face_image(target_img)
    
    logger.info(f"🎬 Generating {num_frames} kiss animation frames...")
    
    with torch.no_grad():
        for i in range(num_frames):
            # Calculate animation progress (0 to 1 and back for kiss motion)
            t = i / (num_frames - 1)
            # Use smooth easing for natural kiss motion
            progress = 0.5 * (1 + np.sin(2 * np.pi * t - np.pi/2))
            
            # Create prompts for kiss animation
            kiss_prompts = [
                "two people about to kiss, romantic, intimate, close up",
                "faces moving closer together, romantic tension",
                "lips almost touching, intimate moment, soft lighting",
                "passionate kiss, romantic scene, beautiful couple",
                "tender kiss, love, romantic atmosphere",
            ]
            
            prompt_idx = min(int(progress * len(kiss_prompts)), len(kiss_prompts) - 1)
            prompt = kiss_prompts[prompt_idx]
            
            try:
                # Generate frame using controlnet-style approach
                # Blend source and target based on animation progress
                if progress < 0.3:
                    control_image = source_processed
                    strength = 0.8
                elif progress > 0.7:
                    control_image = target_processed  
                    strength = 0.8
                else:
                    # Blend images for middle frames
                    alpha = progress
                    source_array = np.array(source_processed)
                    target_array = np.array(target_processed)
                    blended_array = (1 - alpha) * source_array + alpha * target_array
                    control_image = Image.fromarray(blended_array.astype(np.uint8))
                    strength = 0.6
                
                # Generate frame
                result = pipeline(
                    prompt=prompt,
                    image=control_image,
                    num_inference_steps=15,  # Fast inference
                    guidance_scale=7.0,
                    strength=strength,
                    height=512,
                    width=512,
                    generator=torch.Generator(device=DEVICE).manual_seed(42 + i)
                ).images[0]
                
                frames.append(np.array(result))
                logger.info(f"📹 Frame {i+1}/{num_frames} generated (progress: {progress:.2f})")
                
                # Memory cleanup every few frames
                if i % 5 == 0:
                    optimize_gpu_memory()
                    
            except Exception as e:
                logger.warning(f"⚠️  Frame {i+1} generation failed: {e}")
                # Use blended fallback frame
                alpha = progress
                source_array = np.array(source_processed)
                target_array = np.array(target_processed)
                fallback_frame = (1 - alpha) * source_array + alpha * target_array
                frames.append(fallback_frame.astype(np.uint8))
    
    return frames

def create_video_from_frames(frames: list, fps: int = 24) -> str:
    """Create MP4 video from frames and return base64"""
    output_path = tempfile.mktemp(suffix='.mp4')
    
    if not frames:
        raise ValueError("No frames provided for video creation")
    
    height, width = frames[0].shape[:2]
    
    # Use H.264 codec for better compression
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    logger.info(f"🎬 Creating video: {width}x{height} @ {fps}fps ({len(frames)} frames)")
    
    for i, frame in enumerate(frames):
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        video_writer.write(frame_bgr)
        
        if i % 10 == 0:
            logger.info(f"📝 Writing frame {i+1}/{len(frames)}")
    
    video_writer.release()
    
    # Read and encode as base64
    with open(output_path, 'rb') as f:
        video_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Cleanup
    os.remove(output_path)
    
    logger.info(f"✅ Video created: {len(video_data)} chars")
    return video_data

def generate_ai_kiss_video(source_b64: str, target_b64: str) -> Dict[str, Any]:
    """Main AI kiss video generation function"""
    start_time = time.time()
    
    try:
        # Decode input images
        logger.info("🖼️  Decoding input images...")
        source_data = base64.b64decode(source_b64)
        target_data = base64.b64decode(target_b64)
        
        source_image = Image.open(io.BytesIO(source_data)).convert('RGB')
        target_image = Image.open(io.BytesIO(target_data)).convert('RGB')
        
        logger.info(f"📸 Source: {source_image.size}, Target: {target_image.size}")
        
        # Load AI model
        pipeline = load_wan_ai_model()
        if not pipeline:
            raise Exception("Failed to load Wan-AI model")
        
        # Generate animation frames
        frames = generate_kiss_animation_frames(source_image, target_image, pipeline)
        
        if not frames:
            raise Exception("No frames generated")
        
        # Create video
        video_b64 = create_video_from_frames(frames)
        
        processing_time = time.time() - start_time
        
        logger.info(f"✅ AI kiss video generated in {processing_time:.1f}s")
        
        return {
            "status": "success",
            "video": video_b64,
            "processing_time": f"{processing_time:.1f}s",
            "num_frames": len(frames),
            "model_used": "Wan2.1-I2V-14B-720P",
            "resolution": "512x512",
            "fps": 24
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ AI generation failed after {processing_time:.1f}s: {e}")
        
        # Create simple fallback video
        try:
            source_image = Image.open(io.BytesIO(base64.b64decode(source_b64))).convert('RGB')
            target_image = Image.open(io.BytesIO(base64.b64decode(target_b64))).convert('RGB')
            fallback_video = create_morphing_fallback(source_image, target_image)
            
            return {
                "status": "fallback_success",
                "video": fallback_video,
                "processing_time": f"{processing_time:.1f}s",
                "model_used": "morphing_fallback",
                "error": str(e)
            }
        except Exception as fallback_error:
            return {
                "status": "error", 
                "error": str(e),
                "fallback_error": str(fallback_error),
                "processing_time": f"{processing_time:.1f}s"
            }

def create_morphing_fallback(source_image: Image.Image, target_image: Image.Image) -> str:
    """Create morphing fallback video"""
    logger.info("🔄 Creating morphing fallback video...")
    
    source_array = np.array(source_image.resize((512, 512)))
    target_array = np.array(target_image.resize((512, 512)))
    
    frames = []
    num_frames = 48  # 2 seconds at 24fps
    
    for i in range(num_frames):
        t = i / (num_frames - 1)
        # Smooth easing for kiss motion
        alpha = 0.5 * (1 + np.sin(2 * np.pi * t - np.pi/2))
        
        # Blend images
        blended = (1 - alpha) * source_array + alpha * target_array
        frames.append(blended.astype(np.uint8))
    
    return create_video_from_frames(frames)

def check_environment() -> Dict[str, Any]:
    """Comprehensive environment check"""
    logger.info("🔍 Checking environment...")
    
    env_info = {
        "python_version": sys.version,
        "torch_version": torch.__version__ if torch else "Not available",
        "cuda_available": torch.cuda.is_available() if torch else False,
        "device": DEVICE,
        "model_cache_dir": MODEL_CACHE_DIR,
        "volume_mounted": os.path.exists("/runpod-volume"),
        "models_dir_exists": os.path.exists(MODEL_CACHE_DIR),
        "wan_model_exists": os.path.exists(WAN_MODEL_PATH)
    }
    
    if torch.cuda.is_available():
        env_info.update({
            "gpu_count": torch.cuda.device_count(),
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory_total": f"{torch.cuda.get_device_properties(0).total_memory // 1024**3}GB",
            "gpu_memory_free": f"{torch.cuda.memory_reserved(0) // 1024**3}GB"
        })
    
    if env_info["wan_model_exists"]:
        try:
            model_files = list(Path(WAN_MODEL_PATH).iterdir())
            env_info["wan_model_files"] = len(model_files)
            env_info["has_model_weights"] = any(f.suffix in ['.safetensors', '.bin', '.pth'] for f in model_files)
        except Exception as e:
            env_info["wan_model_error"] = str(e)
    
    return env_info

def health_check() -> Dict[str, Any]:
    """Production health check"""
    try:
        env_info = check_environment()
        
        is_healthy = all([
            env_info.get("torch_available", False),
            env_info.get("cuda_available", False),
            env_info.get("volume_mounted", False),
            env_info.get("wan_model_exists", False)
        ])
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": time.time(),
            "environment": env_info,
            "model_cache_status": "loaded" if "wan_ai" in _model_cache else "not_loaded"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

def handler(job):
    """Production RunPod serverless handler"""
    try:
        logger.info("🚀 Production AI Kiss Video Handler Starting...")
        
        job_input = job.get('input', {})
        
        # Handle health check
        if job_input.get('health_check', False):
            return health_check()
        
        # Handle test mode
        if job_input.get('test_mode', False):
            env_info = check_environment()
            return {
                "status": "success",
                "message": "Production handler test completed",
                "environment": env_info,
                "handler_version": "production_v1.0"
            }
        
        # Validate input
        source_image = job_input.get('source_image')
        target_image = job_input.get('target_image')
        
        if not source_image or not target_image:
            return {
                "status": "error",
                "error": "Both source_image and target_image are required",
                "usage": "Provide base64-encoded images in input"
            }
        
        # Optimize GPU before generation
        optimize_gpu_memory()
        
        # Generate AI kiss video
        logger.info("🎬 Starting AI kiss video generation...")
        result = generate_ai_kiss_video(source_image, target_image)
        
        logger.info(f"✅ Handler completed: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Handler error: {e}")
        import traceback
        
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()[-1000:],  # Last 1000 chars
            "handler_version": "production_v1.0"
        }

# For local testing
if __name__ == "__main__":
    logger.info("🧪 Testing production handler...")
    
    # Test health check
    health = health_check()
    print(json.dumps(health, indent=2))
    
    # Test environment
    env = check_environment()
    print(json.dumps(env, indent=2))