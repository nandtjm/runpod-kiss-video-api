#!/usr/bin/env python3
"""
Simple entry point for RunPod serverless
This ensures the handler can be found regardless of the exact command used
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, '.')
sys.path.insert(0, '/workspace')

def main():
    """Main entry point that imports and starts the handler"""
    try:
        print("=" * 60)
        print("🚀 AI Kiss Video Generator - Serverless Entry Point")
        print("=" * 60)
        print(f"📍 Working directory: {os.getcwd()}")
        print(f"📂 Available files: {[f for f in os.listdir('.') if f.endswith('.py')]}")
        print("")
        
        # Try different ways to import the handler
        handler = None
        
        # Method 1: Try handler.serverless
        try:
            print("📦 Attempting to import handler.serverless...")
            from handler.serverless import handler
            print("✅ Successfully imported handler.serverless")
        except (ImportError, ModuleNotFoundError):
            print("⚠️  handler.serverless not found, trying alternatives...")
            
            # Method 2: Try handler_serverless
            try:
                print("📦 Attempting to import handler_serverless...")
                import handler_serverless
                handler = handler_serverless.handler
                print("✅ Successfully imported handler_serverless")
            except (ImportError, ModuleNotFoundError):
                print("⚠️  handler_serverless not found, trying alternatives...")
                
                # Method 3: Try regular handler
                try:
                    print("📦 Attempting to import handler...")
                    from handler import handler
                    print("✅ Successfully imported handler")
                except (ImportError, ModuleNotFoundError):
                    print("❌ No handler found!")
                    print("Available Python files:")
                    for f in os.listdir('.'):
                        if f.endswith('.py'):
                            print(f"  {f}")
                    raise ImportError("No valid handler found")
        
        if handler is None:
            raise RuntimeError("Handler is None after import")
            
        print("")
        print("🔥 Checking PyTorch and GPU...")
        try:
            import torch
            print(f"✅ PyTorch: {torch.__version__}")
            print(f"✅ CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        except ImportError:
            print("⚠️  PyTorch not available")
        
        print("")
        print("💾 Checking network volume...")
        volume_mounted = os.path.exists("/runpod-volume")
        models_exist = os.path.exists("/runpod-volume/models")
        wan_model = os.path.exists("/runpod-volume/models/Wan2.1-I2V-14B-720P")
        
        print(f"✅ Volume mounted: {volume_mounted}")
        print(f"✅ Models directory: {models_exist}")
        print(f"✅ Wan-AI model: {wan_model}")
        
        print("")
        print("🚀 Starting RunPod serverless handler...")
        
        import runpod
        runpod.serverless.start({"handler": handler})
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()