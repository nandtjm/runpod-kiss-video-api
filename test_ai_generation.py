#!/usr/bin/env python3
"""
Test script for AI kiss video generation
Creates sample base64-encoded images and tests the generation process
"""

import base64
import json
import requests
from PIL import Image, ImageDraw
import io
import tempfile

def create_test_face_image(size=(512, 512), face_color=(255, 200, 180), bg_color=(100, 150, 200)):
    """Create a simple test face image"""
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Face outline
    face_x, face_y = size[0] // 2, size[1] // 2
    face_radius = min(size) // 3
    
    # Draw face
    draw.ellipse([
        face_x - face_radius, face_y - face_radius,
        face_x + face_radius, face_y + face_radius
    ], fill=face_color)
    
    # Eyes
    eye_offset = face_radius // 3
    eye_radius = face_radius // 8
    
    # Left eye
    draw.ellipse([
        face_x - eye_offset - eye_radius, face_y - eye_offset - eye_radius,
        face_x - eye_offset + eye_radius, face_y - eye_offset + eye_radius
    ], fill=(0, 0, 0))
    
    # Right eye
    draw.ellipse([
        face_x + eye_offset - eye_radius, face_y - eye_offset - eye_radius,
        face_x + eye_offset + eye_radius, face_y - eye_offset + eye_radius
    ], fill=(0, 0, 0))
    
    # Mouth
    mouth_width = face_radius // 2
    mouth_height = face_radius // 6
    draw.ellipse([
        face_x - mouth_width // 2, face_y + eye_offset - mouth_height // 2,
        face_x + mouth_width // 2, face_y + eye_offset + mouth_height // 2
    ], fill=(200, 100, 100))
    
    return img

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

def test_local_handler():
    """Test the handler locally"""
    print("🧪 Testing AI handler locally...")
    
    # Import handler
    import sys
    sys.path.append('/Users/nandlal/Local Sites/projects/ai-kiss-video-app/ai-kiss-generator/runpod-kiss-api')
    from handler import handler, generate_ai_kiss_video, create_morphing_video
    
    # Create test images
    print("🎭 Creating test face images...")
    source_face = create_test_face_image(face_color=(255, 200, 180))  # Light skin
    target_face = create_test_face_image(face_color=(200, 150, 120))  # Different skin tone
    
    source_b64 = image_to_base64(source_face)
    target_b64 = image_to_base64(target_face)
    
    print(f"✅ Source image: {len(source_b64)} chars")
    print(f"✅ Target image: {len(target_b64)} chars")
    
    # Test health check first
    print("\n🏥 Testing health check...")
    health_job = {"input": {"health_check": True}}
    health_result = handler(health_job)
    print(f"Health Status: {health_result.get('status')}")
    
    if health_result.get('environment', {}).get('models_dir_exists'):
        print("✅ Models directory found")
    else:
        print("⚠️  Models directory not found - will test fallback")
    
    # Test AI video generation
    print("\n🎬 Testing AI video generation...")
    video_job = {
        "input": {
            "source_image": source_b64,
            "target_image": target_b64
        }
    }
    
    try:
        result = handler(video_job)
        
        print(f"Generation Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        print(f"Model Used: {result.get('model_used', 'unknown')}")
        
        if 'video' in result:
            video_b64 = result['video']
            print(f"✅ Video generated: {len(video_b64)} chars")
            
            # Save test video
            video_data = base64.b64decode(video_b64)
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
                f.write(video_data)
                print(f"💾 Video saved to: {f.name}")
                
        else:
            print("❌ No video in response")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_morphing_fallback():
    """Test the morphing fallback function directly"""
    print("\n🔄 Testing morphing fallback...")
    
    import sys
    sys.path.append('/Users/nandlal/Local Sites/projects/ai-kiss-video-app/ai-kiss-generator/runpod-kiss-api')
    from handler import create_morphing_video
    
    # Create test images
    source_face = create_test_face_image(face_color=(255, 200, 180))
    target_face = create_test_face_image(face_color=(200, 150, 120))
    
    try:
        video_b64 = create_morphing_video(source_face, target_face)
        print(f"✅ Morphing video created: {len(video_b64)} chars")
        
        # Save test video
        video_data = base64.b64decode(video_b64)
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            f.write(video_data)
            print(f"💾 Morphing video saved to: {f.name}")
            
    except Exception as e:
        print(f"❌ Morphing test failed: {e}")
        import traceback
        traceback.print_exc()

def create_api_test_request():
    """Generate a test request for the API"""
    source_face = create_test_face_image(face_color=(255, 200, 180))
    target_face = create_test_face_image(face_color=(200, 150, 120))
    
    source_b64 = image_to_base64(source_face)
    target_b64 = image_to_base64(target_face)
    
    test_request = {
        "input": {
            "source_image": source_b64,
            "target_image": target_b64
        }
    }
    
    print("🔗 RunPod API Test Request:")
    print("```bash")
    print("curl -X POST \"https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run\" \\")
    print("  -H \"Authorization: Bearer YOUR_API_KEY\" \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{")
    print("    \"input\": {")
    print(f"      \"source_image\": \"{source_b64[:50]}...\",")
    print(f"      \"target_image\": \"{target_b64[:50]}...\"")
    print("    }")
    print("  }'")
    print("```")
    
    # Save full request to file
    with open('/tmp/ai_test_request.json', 'w') as f:
        json.dump(test_request, f, indent=2)
    print(f"\n💾 Full test request saved to: /tmp/ai_test_request.json")

if __name__ == "__main__":
    print("🤖 AI Kiss Video Generation - Test Suite")
    print("=" * 50)
    
    # Test locally if possible
    test_local_handler()
    
    # Test morphing fallback
    test_morphing_fallback()
    
    # Create API test request
    create_api_test_request()
    
    print("\n✅ Test suite completed!")
    print("\n📋 Next steps:")
    print("1. Update your RunPod endpoint to use: nandtjm/kiss-video-generator:fast")
    print("2. Test with the generated API request")
    print("3. Check logs for model loading and generation process")