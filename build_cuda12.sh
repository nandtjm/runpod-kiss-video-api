#!/bin/bash

# Build CUDA 12.x Compatible RunPod Serverless Image
# Fixes CUDA version mismatch issues

set -e

echo "🚀 Building CUDA 12.x Compatible RunPod Serverless Image"
echo "========================================================"
echo ""

# Configuration
IMAGE_NAME="kiss-video-generator"
TAG="cuda12"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Build Configuration:"
echo "  Purpose: Fix CUDA version compatibility"
echo "  Base Image: runpod/pytorch:2.1.0-py3.10-cuda12.1.0-devel-ubuntu22.04"
echo "  Image: $FULL_IMAGE"
echo "  CUDA Version: 12.1 (RunPod compatible)"
echo "  PyTorch: 2.1.0+ with CUDA 12.1 support"
echo ""

echo "🔍 CUDA Compatibility Fix:"
echo "  ❌ Previous: CUDA 11.8 (incompatible)"
echo "  ✅ New: CUDA 12.1 (RunPod requirement)"
echo "  ✅ PyTorch from cu121 index"
echo "  ✅ All GPU operations should work"
echo ""

# Check required files
echo "🔍 Verifying required files..."
REQUIRED_FILES=(
    "handler.py"
    "runpod_serverless.py" 
    "Dockerfile.cuda12"
    "requirements_cuda12.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
    echo "  ✅ $file"
done

echo ""

# Enable BuildKit
export DOCKER_BUILDKIT=1

echo "🔨 Building CUDA 12.x compatible Docker image..."
echo "⏱️  This may take 3-5 minutes (installing PyTorch with CUDA 12.1)"
echo ""

# Build with CUDA 12.x Dockerfile
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.cuda12 \
    -t "$FULL_IMAGE" \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ CUDA 12.x build successful!"
    echo ""
    
    # Show image info
    echo "📊 Image Information:"
    docker images "$FULL_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    echo ""
    
    # Test CUDA in built image
    echo "🧪 Testing CUDA compatibility in built image..."
    docker run --rm "$FULL_IMAGE" python3 -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
else:
    print('Note: CUDA test requires GPU, but build is compatible')
"
    
    echo ""
    echo "🚀 Next Steps to Fix CUDA Issue:"
    echo ""
    echo "1. 📤 Push the CUDA 12.x compatible image:"
    echo "   docker push $FULL_IMAGE"
    echo ""
    echo "2. 🔧 Update your RunPod serverless endpoint:"
    echo "   - Docker Image: $FULL_IMAGE"
    echo "   - This should resolve the CUDA version mismatch"
    echo ""
    echo "3. 🧪 Test the endpoint:"
    echo "   curl -X POST \"https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run\" \\"
    echo "     -H \"Authorization: Bearer YOUR_API_KEY\" \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"input\": {\"test_mode\": true}}'"
    echo ""
    echo "4. 🎯 Expected CUDA info in response:"
    echo "   {"
    echo "     \"environment\": {"
    echo "       \"torch_available\": true,"
    echo "       \"cuda_available\": true,"
    echo "       \"torch_version\": \"2.1.0+cu121\""
    echo "     }"
    echo "   }"
    echo ""
    
    # Ask about pushing
    read -p "🤔 Push CUDA 12.x image to Docker Hub now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing CUDA 12.x image to Docker Hub..."
        docker push "$FULL_IMAGE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ CUDA 12.x image pushed successfully!"
            echo ""
            echo "🎉 Ready to Fix CUDA Compatibility!"
            echo ""
            echo "📋 Updated Checklist:"
            echo "  1. ✅ CUDA 12.x compatible image built and pushed"
            echo "  2. ⏳ Update endpoint Docker image to: $FULL_IMAGE"
            echo "  3. ⏳ Test endpoint (should now work with GPU)"
            echo "  4. ⏳ Celebrate working CUDA! 🎊"
            echo ""
            echo "💡 The CUDA mismatch should now be resolved."
            echo "   Your endpoint will have proper GPU acceleration."
        else
            echo "❌ Push failed. Please check Docker Hub credentials."
        fi
    else
        echo "⏳ Push later with: docker push $FULL_IMAGE"
    fi
    
else
    echo ""
    echo "❌ Build failed. Check output above for errors."
    echo ""
    echo "🔧 Common CUDA build issues:"
    echo "  - Network timeout during PyTorch download"
    echo "  - Insufficient disk space"
    echo "  - Docker BuildKit not enabled"
    echo ""
    echo "Try running again or check Docker daemon status."
    exit 1
fi