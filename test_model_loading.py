#!/usr/bin/env python3
"""
Test script to verify model loading mechanism
"""

import os
import sys
import tempfile
import shutil

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_model_loading():
    """Test the model loading mechanism with a temporary directory"""
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix="kiss_model_test_")
    print(f"Testing with temporary directory: {temp_dir}")
    
    try:
        # Set environment variable to use temp directory
        os.environ["MODEL_CACHE_DIR"] = temp_dir
        
        # Import the function after setting the environment variable
        from main import load_kiss_models
        
        print("Starting model loading test...")
        print("=" * 60)
        
        # Test model loading (this should attempt downloads)
        models = load_kiss_models()
        
        print("=" * 60)
        print("Test Results:")
        
        # Check results
        for model_name, model_config in models.items():
            if model_config is not None:
                print(f"✅ {model_name}: Successfully loaded")
                print(f"   Type: {model_config.get('type', 'unknown')}")
                if 'model_path' in model_config:
                    print(f"   Path: {model_config['model_path']}")
                if 'lora_path' in model_config:
                    print(f"   LoRA Path: {model_config['lora_path']}")
            else:
                print(f"❌ {model_name}: Failed to load")
        
        # Count available models
        available_count = sum(1 for v in models.values() if v is not None)
        total_count = len(models)
        
        print(f"\nSummary: {available_count}/{total_count} models available")
        
        if available_count > 0:
            print("✅ Model loading mechanism is working!")
            return True
        else:
            print("❌ No models could be loaded")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Warning: Could not clean up {temp_dir}: {e}")

def test_handler_with_missing_models():
    """Test the handler function when models are not available"""
    
    print("\n" + "=" * 60)
    print("Testing handler with missing models...")
    
    try:
        # Import handler
        from main import handler
        
        # Create test job input
        test_job = {
            'input': {
                'source_image': 'https://example.com/source.jpg',
                'target_image': 'https://example.com/target.jpg',
                'model': 'remade_ai'
            }
        }
        
        # Set environment to a non-existent directory
        temp_dir = tempfile.mkdtemp(prefix="kiss_empty_test_")
        os.environ["MODEL_CACHE_DIR"] = temp_dir
        
        try:
            # Call handler
            result = handler(test_job)
            
            print("Handler result:")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Error: {result.get('error', 'none')}")
            
            if 'available_models' in result:
                print(f"  Available models: {result['available_models']}")
            
            if result.get('status') == 'failed' and 'not available' in result.get('error', ''):
                print("✅ Handler correctly reports model unavailability")
                return True
            else:
                print("❌ Handler did not handle missing models correctly")
                return False
                
        finally:
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        print(f"❌ Handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("RunPod Kiss API - Model Loading Test")
    print("=" * 60)
    
    success = True
    
    # Test 1: Model loading mechanism
    success &= test_model_loading()
    
    # Test 2: Handler with missing models
    success &= test_handler_with_missing_models()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(0 if success else 1)