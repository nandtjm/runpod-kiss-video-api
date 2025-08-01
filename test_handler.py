#!/usr/bin/env python3
"""
Minimal test handler to isolate container startup issues
"""

import sys
import os
import time

def main():
    """Minimal test main function"""
    try:
        print("=== TEST HANDLER STARTING ===", flush=True)
        print(f"Python version: {sys.version}", flush=True)
        print(f"Working directory: {os.getcwd()}", flush=True)
        print(f"Python executable: {sys.executable}", flush=True)
        
        # Test basic imports
        print("Testing basic imports...", flush=True)
        
        try:
            import torch
            print(f"✅ PyTorch: {torch.__version__}", flush=True)
            print(f"✅ CUDA available: {torch.cuda.is_available()}", flush=True)
        except ImportError as e:
            print(f"❌ PyTorch import failed: {e}", flush=True)
            
        try:
            import runpod
            print("✅ RunPod imported successfully", flush=True)
        except ImportError as e:
            print(f"❌ RunPod import failed: {e}", flush=True)
            
        # Test handler import
        print("Testing handler import...", flush=True)
        try:
            from main import handler
            print("✅ Handler imported successfully", flush=True)
            print(f"✅ Handler callable: {callable(handler)}", flush=True)
        except ImportError as e:
            print(f"❌ Handler import failed: {e}", flush=True)
        except Exception as e:
            print(f"❌ Handler error: {e}", flush=True)
            
        print("=== TEST COMPLETED - KEEPING ALIVE ===", flush=True)
        
        # Keep the container alive for 60 seconds to see logs
        for i in range(60):
            print(f"Alive for {i+1} seconds...", flush=True)
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()