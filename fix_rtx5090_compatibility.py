#!/usr/bin/env python3
"""
Fix RTX 5090 Compatibility and Model Path Issues
"""

import os
import torch

def check_gpu_compatibility():
    """Check RTX 5090 compatibility and suggest fixes"""
    print("🎮 GPU Compatibility Check")
    print("=" * 40)
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU: {gpu_name}")
        
        # Get GPU compute capability
        major, minor = torch.cuda.get_device_capability(0)
        compute_cap = f"sm_{major}{minor}"
        print(f"Compute Capability: {compute_cap}")
        
        # RTX 5090 uses sm_120 (CUDA Compute 12.0)
        if "RTX 5090" in gpu_name:
            print("⚠️  RTX 5090 detected - PyTorch compatibility issue")
            print(f"   Current PyTorch: {torch.__version__}")
            print(f"   CUDA Version: {torch.version.cuda}")
            print("   RTX 5090 needs PyTorch 2.8+ with CUDA 12.8+")
            print("")
            print("🔧 Recommendations:")
            print("1. Use RTX 4090 GPU (fully compatible)")
            print("2. Use A100 40GB GPU (enterprise grade)")  
            print("3. Update to newer PyTorch base image:")
            print("   runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04")
            return False
        else:
            print("✅ GPU is compatible with current PyTorch")
            return True
    else:
        print("❌ CUDA not available")
        return False

def check_network_volume():
    """Check network volume and find models"""
    print("\n💾 Network Volume Check")
    print("=" * 40)
    
    volume_mounted = os.path.exists("/runpod-volume")
    print(f"Volume mounted: {volume_mounted}")
    
    if volume_mounted:
        print("📁 Volume contents:")
        try:
            contents = os.listdir("/runpod-volume")
            for item in contents:
                item_path = f"/runpod-volume/{item}"
                if os.path.isdir(item_path):
                    print(f"  📂 {item}/")
                    # Check subdirectories
                    try:
                        subitems = os.listdir(item_path)[:5]  # First 5 items
                        for subitem in subitems:
                            print(f"     📄 {subitem}")
                        if len(os.listdir(item_path)) > 5:
                            print(f"     ... and {len(os.listdir(item_path)) - 5} more")
                    except PermissionError:
                        print(f"     (access denied)")
                else:
                    print(f"  📄 {item}")
        except Exception as e:
            print(f"  Error listing contents: {e}")
        
        # Look for models in common locations
        model_locations = [
            "/runpod-volume/models",
            "/runpod-volume/Models", 
            "/runpod-volume/AI-Models",
            "/runpod-volume/huggingface",
            "/runpod-volume/cache",
            "/runpod-volume"
        ]
        
        print(f"\n🔍 Searching for Wan-AI model in common locations:")
        for location in model_locations:
            if os.path.exists(location):
                print(f"✅ {location} exists")
                try:
                    items = os.listdir(location)
                    wan_models = [item for item in items if 'wan' in item.lower() or 'i2v' in item.lower()]
                    if wan_models:
                        print(f"   🎯 Found potential models: {wan_models}")
                    else:
                        print(f"   📋 Contents: {items[:3]}..." if len(items) > 3 else f"   📋 Contents: {items}")
                except Exception as e:
                    print(f"   ❌ Cannot list: {e}")
            else:
                print(f"❌ {location} not found")
    
    return volume_mounted

def suggest_model_path_fix():
    """Suggest how to fix model path issues"""
    print("\n🔧 Model Path Fix Suggestions")
    print("=" * 40)
    
    print("If models are in your network volume but not found:")
    print("")
    print("1. 📂 Check actual model location in your volume")
    print("2. 🔧 Update MODEL_CACHE_DIR environment variable")
    print("3. 📝 Common model paths:")
    print("   - /runpod-volume/models/")
    print("   - /runpod-volume/Models/")  
    print("   - /runpod-volume/huggingface/")
    print("   - /runpod-volume/AI-Models/")
    print("")
    print("4. 🚀 Update RunPod endpoint environment:")
    print("   MODEL_CACHE_DIR=/runpod-volume/ACTUAL_PATH")

if __name__ == "__main__":
    print("🔧 RTX 5090 & Model Path Diagnostic")
    print("=" * 50)
    
    # Check GPU compatibility
    gpu_compatible = check_gpu_compatibility()
    
    # Check network volume
    volume_ok = check_network_volume()
    
    # Provide suggestions
    if not gpu_compatible:
        print("\n💡 GPU Recommendation: Switch to RTX 4090 for guaranteed compatibility")
    
    if not volume_ok:
        print("\n💡 Volume Recommendation: Ensure network volume is properly mounted")
    else:
        suggest_model_path_fix()
    
    print(f"\n📋 Summary:")
    print(f"  GPU Compatible: {'✅' if gpu_compatible else '❌'}")
    print(f"  Volume Mounted: {'✅' if volume_ok else '❌'}")
    print(f"  Ready for AI Generation: {'✅' if gpu_compatible and volume_ok else '❌'}")