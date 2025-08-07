#!/usr/bin/env python3
"""
Serverless AI Kiss Video Generator Handler - Network Volume Optimized
Uses pre-existing models from RunPod network volume - No downloads!

This is the main handler file that will be called by RunPod serverless.
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
import io
import requests
from loguru import logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.info("🚀 Serverless AI Kiss Video Generator - Network Volume Mode")

# Configuration - Uses network volume models
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/runpod-volume/models")
WAN_MODEL_PATH = f"{MODEL_CACHE_DIR}/Wan2.1-I2V-14B-720P"
LORA_MODEL_PATH = f"{MODEL_CACHE_DIR}/kissing-lora"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

logger.info(f"📁 Model cache directory: {MODEL_CACHE_DIR}")
logger.info(f"🤖 Wan-AI model path: {WAN_MODEL_PATH}")
logger.info(f"🎭 LoRA model path: {LORA_MODEL_PATH}")

# Global model cache for serverless efficiency
_model_cache = {}

def check_network_volume() -> Dict[str, Any]:
    """Check network volume and model availability"""
    volume_info = {
        "volume_mounted": os.path.exists("/runpod-volume"),
        "models_dir_exists": os.path.exists(MODEL_CACHE_DIR),
        "wan_model_exists": os.path.exists(WAN_MODEL_PATH),
        "lora_model_exists": os.path.exists(LORA_MODEL_PATH),
        "model_files": []
    }
    
    # List available models
    if volume_info["models_dir_exists"]:
        try:
            model_dirs = [d for d in os.listdir(MODEL_CACHE_DIR) if os.path.isdir(os.path.join(MODEL_CACHE_DIR, d))]
            volume_info["model_files"] = model_dirs
            volume_info["total_models"] = len(model_dirs)
        except Exception as e:
            volume_info["error"] = str(e)
    
    # Check Wan-AI model details
    if volume_info["wan_model_exists"]:
        try:
            wan_files = list(Path(WAN_MODEL_PATH).iterdir())
            volume_info["wan_model_files"] = len(wan_files)
            volume_info["has_safetensors"] = any(f.suffix == '.safetensors' for f in wan_files)
            volume_info["has_config"] = any(f.name.startswith('config') for f in wan_files)
        except Exception as e:
            volume_info["wan_error"] = str(e)
    
    return volume_info

def load_ai_models():
    """Load AI models from network volume"""
    global _model_cache
    
    # Check if models already loaded
    if "pipeline" in _model_cache:
        logger.info("✅ Using cached AI models")
        return _model_cache["pipeline"]
    
    # Verify network volume
    volume_info = check_network_volume()
    if not volume_info["wan_model_exists"]:
        raise Exception(f"Wan-AI model not found on network volume: {WAN_MODEL_PATH}")
    
    logger.info("🔄 Loading AI models from network volume...")
    
    try:
        from diffusers import DiffusionPipeline
        
        # Load Wan-AI model from network volume
        pipeline = DiffusionPipeline.from_pretrained(
            WAN_MODEL_PATH,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            safety_checker=None,
            requires_safety_checker=False,
            local_files_only=True,  # Only use network volume files
            cache_dir=None  # Don't cache - use direct from volume
        )
        
        if DEVICE == "cuda":
            pipeline = pipeline.to(DEVICE)
            pipeline.enable_memory_efficient_attention()
            pipeline.enable_vae_slicing()
            pipeline.enable_model_cpu_offload()
        
        # Cache for serverless efficiency
        _model_cache["pipeline"] = pipeline
        
        logger.info("✅ AI models loaded from network volume")
        return pipeline
        
    except Exception as e:
        logger.error(f"❌ Failed to load AI models from network volume: {e}")
        raise

def optimize_gpu_memory():
    """Optimize GPU memory for serverless"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        
        # Log GPU memory status
        memory_allocated = torch.cuda.memory_allocated(0) // 1024**2
        memory_reserved = torch.cuda.memory_reserved(0) // 1024**2
        logger.info(f"🎮 GPU Memory: {memory_allocated}MB allocated, {memory_reserved}MB reserved")

def preprocess_image(image: Image.Image, size: Tuple[int, int] = (512, 512)) -> Image.Image:
    """Preprocess image for AI generation"""
    # Convert and resize
    image = image.convert('RGB')
    
    # Smart resize with padding
    w, h = image.size
    aspect = w / h
    target_w, target_h = size
    
    if aspect > 1:
        new_w = target_w
        new_h = int(target_w / aspect)
    else:
        new_h = target_h
        new_w = int(target_h * aspect)
    
    image = image.resize((new_w, new_h), Image.LANCZOS)
    
    # Center on black background
    result = Image.new('RGB', size, (0, 0, 0))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    result.paste(image, (paste_x, paste_y))
    
    return result

def generate_kiss_video_frames(source_img: Image.Image, target_img: Image.Image, 
                             pipeline, num_frames: int = 24) -> list:
    """Generate kiss animation frames using network volume models"""
    frames = []
    
    # Preprocess images
    source_processed = preprocess_image(source_img)
    target_processed = preprocess_image(target_img)
    
    logger.info(f"🎬 Generating {num_frames} frames using network volume models...")
    
    with torch.no_grad():
        for i in range(num_frames):
            # Animation progress
            t = i / (num_frames - 1)
            progress = 0.5 * (1 + np.sin(2 * np.pi * t - np.pi/2))
            
            # Kiss prompts
            kiss_prompts = [
                "two faces approaching for a kiss, romantic lighting, soft focus",
                "faces getting closer, intimate moment, warm atmosphere",
                "lips about to touch, romantic tension, beautiful lighting",
                "passionate kiss between two people, love scene, cinematic",
                "tender kiss, romantic scene, soft lighting, emotional"
            ]
            
            prompt_idx = min(int(progress * len(kiss_prompts)), len(kiss_prompts) - 1)
            prompt = kiss_prompts[prompt_idx]
            
            try:
                # Control image based on progress
                if progress < 0.3:
                    control_image = source_processed
                elif progress > 0.7:
                    control_image = target_processed
                else:
                    # Blend images
                    alpha = progress
                    source_array = np.array(source_processed)
                    target_array = np.array(target_processed)
                    blended_array = (1 - alpha) * source_array + alpha * target_array
                    control_image = Image.fromarray(blended_array.astype(np.uint8))
                
                # Generate frame using network volume models
                result = pipeline(
                    prompt=prompt,
                    image=control_image,
                    num_inference_steps=12,  # Fast for serverless
                    guidance_scale=6.5,
                    height=512,
                    width=512,
                    generator=torch.Generator(device=DEVICE).manual_seed(42 + i)
                ).images[0]
                
                frames.append(np.array(result))
                
                # Optimize memory every few frames
                if i % 6 == 0:
                    optimize_gpu_memory()
                
            except Exception as e:
                logger.warning(f"⚠️ Frame {i+1} failed: {e}, using fallback")
                # Fallback frame
                alpha = progress
                source_array = np.array(source_processed)
                target_array = np.array(target_processed)
                fallback = (1 - alpha) * source_array + alpha * target_array
                frames.append(fallback.astype(np.uint8))
    
    logger.info(f"✅ Generated {len(frames)} frames")
    return frames

def create_video_from_frames(frames: list, fps: int = 24) -> str:
    """Create MP4 video and return base64"""
    if not frames:
        raise ValueError("No frames to create video")
    
    output_path = tempfile.mktemp(suffix='.mp4')
    height, width = frames[0].shape[:2]
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        video_writer.write(frame_bgr)
    
    video_writer.release()
    
    # Convert to base64
    with open(output_path, 'rb') as f:
        video_data = base64.b64encode(f.read()).decode('utf-8')
    
    os.remove(output_path)
    return video_data

def download_image_from_url(url: str) -> Image.Image:
    """Download and validate image from URL or data URL"""
    try:
        logger.info(f"📥 Processing image from: {url[:100]}...")
        
        # Handle data URLs (base64 embedded)
        if url.startswith('data:'):
            logger.info("🔄 Processing data URL...")
            header, encoded = url.split(',', 1)
            image_data = base64.b64decode(encoded)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        else:
            # Download from HTTP/HTTPS URL
            headers = {
                'User-Agent': 'RunPod AI Kiss Video Generator/1.0',
                'Accept': 'image/*'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                raise ValueError(f"Invalid content type: {content_type}")
            
            # Load image
            image = Image.open(io.BytesIO(response.content)).convert('RGB')
        
        # Validate image size
        if image.size[0] < 64 or image.size[1] < 64:
            raise ValueError(f"Image too small: {image.size}")
        
        if image.size[0] > 4096 or image.size[1] > 4096:
            logger.info(f"⚠️ Large image {image.size}, resizing...")
            image = image.resize((min(2048, image.size[0]), min(2048, image.size[1])), Image.LANCZOS)
        
        logger.info(f"✅ Image loaded: {image.size}")
        return image
        
    except Exception as e:
        raise Exception(f"Failed to download image from {url}: {str(e)}")

def create_morphing_fallback(source_image: Image.Image, target_image: Image.Image) -> str:
    """Create morphing fallback if AI generation fails"""
    logger.info("🔄 Creating morphing fallback...")
    
    source_array = np.array(source_image.resize((512, 512)))
    target_array = np.array(target_image.resize((512, 512)))
    
    frames = []
    for i in range(48):
        t = i / 47
        alpha = 0.5 * (1 + np.sin(2 * np.pi * t - np.pi/2))
        blended = (1 - alpha) * source_array + alpha * target_array
        frames.append(blended.astype(np.uint8))
    
    return create_video_from_frames(frames)

def generate_ai_kiss_video(source_url: str, target_url: str) -> Dict[str, Any]:
    """Main AI video generation using network volume models"""
    start_time = time.time()
    
    try:
        # Download images from URLs
        source_image = download_image_from_url(source_url)
        target_image = download_image_from_url(target_url)
        
        logger.info(f"📸 Processing: {source_image.size} + {target_image.size}")
        
        # Load models from network volume
        pipeline = load_ai_models()
        
        # Generate frames
        frames = generate_kiss_video_frames(source_image, target_image, pipeline)
        
        # Create video
        video_b64 = create_video_from_frames(frames)
        
        processing_time = time.time() - start_time
        
        return {
            "status": "success",
            "message": "AI kiss video generated using network volume models",
            "video": video_b64,
            "processing_time": f"{processing_time:.1f}s",
            "num_frames": len(frames),
            "model_used": "Wan2.1-I2V-14B-720P",
            "model_source": "network_volume",
            "resolution": "512x512"
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ AI generation failed: {e}")
        
        # Fallback to morphing
        try:
            source_image = download_image_from_url(source_url)
            target_image = download_image_from_url(target_url)
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

def check_environment() -> Dict[str, Any]:
    """Check serverless environment"""
    env_info = {
        "python_version": sys.version,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device": DEVICE,
        "deployment_mode": "serverless_network_volume"
    }
    
    # GPU info
    if torch.cuda.is_available():
        env_info.update({
            "gpu_count": torch.cuda.device_count(),
            "gpu_name": torch.cuda.get_device_name(0),
            "gpu_memory": f"{torch.cuda.get_device_properties(0).total_memory // 1024**3}GB"
        })
    
    # Network volume info
    volume_info = check_network_volume()
    env_info["network_volume"] = volume_info
    
    return env_info

def explore_volume_structure() -> Dict[str, Any]:
    """Debug function to explore network volume structure and find models"""
    try:
        volume_info = {
            "volume_mounted": os.path.exists("/runpod-volume"),
            "volume_contents": {},
            "model_search_results": {},
            "recommendations": []
        }
        
        if volume_info["volume_mounted"]:
            # Explore volume contents
            try:
                contents = os.listdir("/runpod-volume")
                for item in contents[:10]:  # First 10 items
                    item_path = f"/runpod-volume/{item}"
                    if os.path.isdir(item_path):
                        try:
                            subitems = os.listdir(item_path)[:5]
                            volume_info["volume_contents"][f"{item}/"] = subitems
                        except:
                            volume_info["volume_contents"][f"{item}/"] = "access_denied"
                    else:
                        size = os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                        volume_info["volume_contents"][item] = f"{size} bytes"
            except Exception as e:
                volume_info["volume_contents"] = f"Error: {e}"
            
            # Search for AI models
            search_patterns = ["wan", "i2v", "kiss", "video", "model", "safetensors", "bin", "pth"]
            search_locations = [
                "/runpod-volume",
                "/runpod-volume/models",
                "/runpod-volume/Models", 
                "/runpod-volume/huggingface",
                "/runpod-volume/AI-Models",
                "/runpod-volume/cache"
            ]
            
            for location in search_locations:
                if os.path.exists(location):
                    try:
                        items = os.listdir(location)
                        matches = []
                        for item in items:
                            for pattern in search_patterns:
                                if pattern.lower() in item.lower():
                                    item_path = os.path.join(location, item)
                                    if os.path.isdir(item_path):
                                        # Count files in model directory
                                        try:
                                            file_count = len(os.listdir(item_path))
                                            matches.append(f"{item}/ ({file_count} files)")
                                        except:
                                            matches.append(f"{item}/ (access denied)")
                                    else:
                                        matches.append(item)
                                    break
                        
                        volume_info["model_search_results"][location] = matches[:5]
                        
                        # Generate recommendations
                        if matches:
                            volume_info["recommendations"].append(
                                f"Found models in {location}: {matches[:3]}"
                            )
                            if "wan" in str(matches).lower() or "i2v" in str(matches).lower():
                                volume_info["recommendations"].append(
                                    f"🎯 Recommended MODEL_CACHE_DIR: {location}"
                                )
                    except Exception as e:
                        volume_info["model_search_results"][location] = f"Error: {e}"
        
        return {
            "status": "debug_complete",
            "message": "Volume structure explored",
            "volume_info": volume_info
        }
        
    except Exception as e:
        return {
            "status": "debug_error",
            "error": str(e)
        }

def check_gpu_compatibility() -> Dict[str, Any]:
    """Debug function to check GPU compatibility with PyTorch"""
    try:
        gpu_info = {
            "cuda_available": torch.cuda.is_available(),
            "pytorch_version": torch.__version__,
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
        }
        
        if torch.cuda.is_available():
            gpu_info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_count": torch.cuda.device_count(),
                "compute_capability": torch.cuda.get_device_capability(0),
                "memory_total": f"{torch.cuda.get_device_properties(0).total_memory // 1024**3}GB"
            })
            
            # Check RTX 5090 compatibility
            if "RTX 5090" in gpu_info["gpu_name"]:
                major, minor = torch.cuda.get_device_capability(0)
                compute_cap = f"sm_{major}{minor}"
                gpu_info["compatibility_issue"] = True
                gpu_info["issue_description"] = f"RTX 5090 uses {compute_cap} but PyTorch {gpu_info['pytorch_version']} only supports up to sm_90"
                gpu_info["recommendations"] = [
                    "Switch to RTX 4090 GPU (fully compatible)",
                    "Use A100 40GB GPU (enterprise grade)",
                    "Update base image to: runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
                ]
            else:
                gpu_info["compatibility_issue"] = False
                gpu_info["status"] = "GPU fully compatible with current PyTorch"
        
        return {
            "status": "gpu_debug_complete",
            "gpu_info": gpu_info
        }
        
    except Exception as e:
        return {
            "status": "gpu_debug_error",
            "error": str(e)
        }

def health_check() -> Dict[str, Any]:
    """Serverless health check"""
    try:
        env_info = check_environment()
        volume_info = env_info["network_volume"]
        
        is_healthy = all([
            env_info.get("cuda_available", False),
            volume_info.get("volume_mounted", False),
            volume_info.get("wan_model_exists", False)
        ])
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": time.time(),
            "environment": env_info,
            "models_ready": volume_info.get("wan_model_exists", False)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

def handler(job):
    """Serverless handler using network volume models"""
    try:
        logger.info("🚀 Serverless Handler - Network Volume Mode")
        
        job_input = job.get('input', {})
        
        # Health check
        if job_input.get('health_check', False):
            return health_check()
        
        # Test mode
        if job_input.get('test_mode', False):
            env_info = check_environment()
            return {
                "status": "success",
                "message": "Serverless handler ready",
                "environment": env_info,
                "deployment_mode": "serverless_network_volume"
            }
        
        # Debug mode - explore volume structure
        if job_input.get('debug') == 'check_volume':
            return explore_volume_structure()
        
        # GPU compatibility check
        if job_input.get('debug') == 'check_gpu':
            return check_gpu_compatibility()
        
        # Video generation
        source_image_url = job_input.get('source_image_url')
        target_image_url = job_input.get('target_image_url')
        
        # Support both URL and base64 inputs
        source_image = job_input.get('source_image')
        target_image = job_input.get('target_image')
        
        if source_image_url and target_image_url:
            # Use URLs (preferred)
            pass
        elif source_image and target_image:
            # Check if it's actually base64 data or a URL mistakenly passed as source_image
            if source_image.startswith(('http://', 'https://', 'data:')):
                # It's actually a URL, use directly
                logger.info("🔄 Detected URL in legacy source_image field")
                source_image_url = source_image
                target_image_url = target_image
            else:
                # Legacy base64 support
                logger.info("⚠️ Using legacy base64 input (deprecated)")
                source_image_url = f"data:image/jpeg;base64,{source_image}"
                target_image_url = f"data:image/jpeg;base64,{target_image}"
        else:
            return {
                "status": "error",
                "error": "Both source_image_url and target_image_url required",
                "usage": "Provide image URLs: {'source_image_url': 'https://...', 'target_image_url': 'https://...'}"
            }
        
        # Optimize GPU before generation
        optimize_gpu_memory()
        
        # Generate video using network volume models
        result = generate_ai_kiss_video(source_image_url, target_image_url)
        
        # Cleanup after generation
        optimize_gpu_memory()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Handler error: {e}")
        import traceback
        
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()[-1000:],
            "deployment_mode": "serverless_network_volume"
        }

# RunPod serverless integration
if __name__ == "__main__":
    print("🚀 Starting AI Kiss Video Generator - Network Volume Mode")
    runpod.serverless.start({"handler": handler})