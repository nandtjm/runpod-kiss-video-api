#!/usr/bin/env python3
"""
RunPod Serverless Entry Point - Guaranteed Working Version
This is the main entry point that RunPod serverless will call
"""

import runpod
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for RunPod serverless"""
    try:
        print("=" * 50)
        print("🚀 RunPod Serverless Worker Starting")
        print("=" * 50)
        
        # Import handler
        from handler import handler
        print("✅ Handler imported successfully")
        
        # Print environment info
        print(f"📍 Working directory: {os.getcwd()}")
        print(f"🐍 Python version: {sys.version}")
        
        # Check PyTorch
        try:
            import torch
            print(f"🔥 PyTorch: {torch.__version__}")
            print(f"🎮 CUDA available: {torch.cuda.is_available()}")
        except ImportError:
            print("⚠️  PyTorch not available")
        
        # Check volume mount
        volume_mounted = os.path.exists("/runpod-volume")
        workspace_exists = os.path.exists("/workspace")
        print(f"💾 Volume mounted at /runpod-volume: {volume_mounted}")
        print(f"💾 Workspace exists at /workspace: {workspace_exists}")
        
        if volume_mounted:
            try:
                volume_contents = os.listdir("/runpod-volume")
                print(f"📁 Volume contents: {volume_contents}")
            except:
                print("📁 Volume contents: Cannot list")
        
        print("✅ Starting RunPod serverless handler...")
        
        # Start the serverless handler
        runpod.serverless.start({"handler": handler})
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()