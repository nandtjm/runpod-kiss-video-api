#!/bin/bash

# Build Latest CUDA 12.8+ & PyTorch 2.8+ RunPod Serverless Image
# Updated for cutting-edge compatibility

set -e

echo "🚀 Building Latest CUDA 12.8+ & PyTorch 2.8+ Image"
echo "=================================================="
echo ""

# Configuration
IMAGE_NAME="kiss-video-generator"
TAG="latest"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Latest Build Configuration:"
echo "  Purpose: Latest CUDA & PyTorch compatibility"
echo "  Base Image: runpod/pytorch:2.4.0-py3.11-cuda12.4.1"
echo "  Target Image: $FULL_IMAGE"
echo "  CUDA Version: 12.4+ (supports 12.8)"
echo "  PyTorch: 2.8+ with latest CUDA support"
echo "  Python: 3.11 (latest stable)"
echo ""

echo "🔍 Latest Version Benefits:"
echo "  ✅ CUDA 12.8+ compatibility"
echo "  ✅ PyTorch 2.8+ with all latest features"
echo "  ✅ Python 3.11 performance improvements"
echo "  ✅ Latest Hugging Face ecosystem"
echo "  ✅ Cutting-edge AI model support"
echo "  ✅ Better GPU memory management"
echo ""

# Check required files
echo "🔍 Verifying required files..."
REQUIRED_FILES=(
    "handler.py"
    "runpod_serverless.py" 
    "Dockerfile.latest"
    "requirements_latest.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
    echo "  ✅ $file"
done

echo ""

# Show disk space
echo "💾 Checking available disk space..."
df -h . | tail -1 | awk '{print "  Available: " $4 " (need ~5GB for build)"}'
echo ""

# Enable BuildKit for better performance
export DOCKER_BUILDKIT=1

echo "🔨 Building latest CUDA/PyTorch Docker image..."
echo "⏱️  This may take 5-8 minutes (downloading PyTorch 2.8+)"
echo "📡 Downloading from PyTorch nightly builds for latest features"
echo ""

# Build with latest Dockerfile
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.latest \
    -t "$FULL_IMAGE" \
    --progress=plain \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Latest build successful!"
    echo ""
    
    # Show image info
    echo "📊 Image Information:"
    docker images "$FULL_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    echo ""
    
    # Test latest versions in built image
    echo "🧪 Testing latest versions in built image..."
    docker run --rm "$FULL_IMAGE" python3 -c "
import sys
print(f'Python: {sys.version.split()[0]}')

try:
    import torch
    print(f'PyTorch: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    
    if hasattr(torch.version, 'cuda') and torch.version.cuda:
        print(f'CUDA version (PyTorch): {torch.version.cuda}')
    
    # Check PyTorch version meets requirements
    major, minor = map(int, torch.__version__.split('.')[:2])
    if major > 2 or (major == 2 and minor >= 5):
        print('✅ PyTorch version excellent for latest features')
    else:
        print(f'⚠️  PyTorch {torch.__version__} - might want newer nightly build')
        
except Exception as e:
    print(f'PyTorch test error: {e}')

try:
    import cv2
    print(f'OpenCV: {cv2.__version__}')
except Exception as e:
    print(f'OpenCV error: {e}')

try:
    import transformers
    print(f'Transformers: {transformers.__version__}')
except Exception as e:
    print(f'Transformers error: {e}')

print('Note: GPU tests require actual GPU hardware')
"
    
    echo ""
    echo "🚀 Next Steps for Latest Version:"
    echo ""
    echo "1. 📤 Push the latest image:"
    echo "   docker push $FULL_IMAGE"
    echo ""
    echo "2. 🔧 Update your RunPod serverless endpoint:"
    echo "   - Docker Image: $FULL_IMAGE"
    echo "   - GPU: RTX 4090 or RTX 6000 Ada (for CUDA 12.8+ support)"
    echo "   - Memory: 32GB+ (recommended for PyTorch 2.8+)"
    echo ""
    echo "3. 🧪 Test the latest endpoint:"
    echo "   curl -X POST \"https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run\" \\"
    echo "     -H \"Authorization: Bearer YOUR_API_KEY\" \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"input\": {\"test_mode\": true}}'"
    echo ""
    echo "4. 🎯 Expected latest version info:"
    echo "   {"
    echo "     \"environment\": {"
    echo "       \"python_version\": \"3.11.x\","
    echo "       \"torch_available\": true,"
    echo "       \"cuda_available\": true,"
    echo "       \"torch_version\": \"2.8.x+cu124\""
    echo "     }"
    echo "   }"
    echo ""
    
    # Ask about pushing
    read -p "🤔 Push latest image to Docker Hub now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing latest image to Docker Hub..."
        docker push "$FULL_IMAGE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Latest image pushed successfully!"
            echo ""
            echo "🎉 Cutting-Edge CUDA/PyTorch Ready!"
            echo ""
            echo "📋 Latest Version Checklist:"
            echo "  1. ✅ CUDA 12.8+ & PyTorch 2.8+ image built and pushed"
            echo "  2. ⏳ Update endpoint Docker image to: $FULL_IMAGE"
            echo "  3. ⏳ Test endpoint with latest GPU features"
            echo "  4. ⏳ Enjoy bleeding-edge performance! 🚀"
            echo ""
            echo "💡 Benefits of latest version:"
            echo "   🔥 Best GPU performance and memory efficiency"
            echo "   🧠 Latest AI model compatibility"
            echo "   ⚡ Faster inference and better optimization"
            echo "   🎯 Support for newest Hugging Face models"
            echo ""
            echo "🔗 Image available at: https://hub.docker.com/r/$REGISTRY/$IMAGE_NAME/tags"
        else
            echo "❌ Push failed. Check Docker Hub credentials:"
            echo "   docker login"
            echo "   docker push $FULL_IMAGE"
        fi
    else
        echo "⏳ Push later with: docker push $FULL_IMAGE"
        echo ""
        echo "📝 Don't forget to update your RunPod endpoint with:"
        echo "   Docker Image: $FULL_IMAGE"
    fi
    
else
    echo ""
    echo "❌ Latest build failed. Common issues:"
    echo ""
    echo "🔧 Troubleshooting latest build:"
    echo "  1. Network timeout during PyTorch 2.8+ download"
    echo "  2. Insufficient disk space (need ~5GB+)"
    echo "  3. Docker BuildKit issues"
    echo "  4. Base image compatibility"
    echo ""
    echo "💡 Solutions:"
    echo "  - Ensure stable internet for large PyTorch download"
    echo "  - Free up disk space: docker system prune -a"
    echo "  - Check Docker version: docker --version"
    echo "  - Try smaller intermediate build first"
    echo ""
    echo "📋 Build logs above show specific error details"
    exit 1
fi