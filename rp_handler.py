#!/usr/bin/env python3
"""
RunPod Handler - Entry point for RunPod serverless worker
"""

import runpod
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for RunPod worker"""
    try:
        print("=== RunPod Worker Starting ===")
        print("Python version:", sys.version)
        print("Working directory:", os.getcwd())
        print("Python path:", sys.path)
        
        # Import our handler function
        from main import handler
        print("✅ Handler imported successfully")
        
        # Test basic imports
        import torch
        print("✅ PyTorch available:", torch.__version__)
        print("✅ CUDA available:", torch.cuda.is_available())
        
        print("✅ Starting RunPod serverless worker...")
        
        # Start the RunPod serverless handler
        runpod.serverless.start({"handler": handler})
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in RunPod handler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()