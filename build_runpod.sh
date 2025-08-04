#!/bin/bash

# RunPod Serverless Build Script
# Strategy: Small image, models stored on RunPod Network Storage

echo "🚀 Building RunPod Serverless Image"
echo "===================================="

# Build configuration
IMAGE_NAME="kiss-video-generator"
TAG="runpod-serverless"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Build Configuration:"
echo "  Image Name: $IMAGE_NAME"
echo "  Tag: $TAG"
echo "  Registry: $REGISTRY"
echo "  Full Image: $FULL_IMAGE"
echo "  Strategy: RunPod Network Storage + Serverless"
echo ""

echo "💡 RunPod Strategy Benefits:"
echo "  ✅ Small Docker image (~2-3GB instead of 30GB+)"
echo "  ✅ Models downloaded once to Network Storage"
echo "  ✅ All containers share the same models"
echo "  ✅ Fast cold starts (no 28GB download per container)"
echo "  ✅ Cost effective (pay only for compute, not storage transfer)"
echo ""

# Enable BuildKit
export DOCKER_BUILDKIT=1

echo "🔨 Building RunPod serverless image..."
echo "📦 Models will be stored on RunPod Network Storage"
echo ""

# Build the image
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.runpod \
    -t "$FULL_IMAGE" \
    --progress=plain \
    --no-cache \
    .

# Check build status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build completed successfully!"
    echo ""
    echo "📊 Image Information:"
    docker images "$FULL_IMAGE"
    echo ""
    echo "🚀 Next Steps for RunPod Deployment:"
    echo ""
    echo "1. Push to Docker Hub:"
    echo "   docker push $FULL_IMAGE"
    echo ""
    echo "2. Create RunPod Serverless Endpoint:"
    echo "   - Go to RunPod Dashboard → Serverless"
    echo "   - Create New Endpoint"
    echo "   - Docker Image: $FULL_IMAGE"
    echo "   - GPU: RTX 4090 or A100 (for best performance)"
    echo "   - Network Storage: Enable 100GB+ (for models)"
    echo ""
    echo "3. Environment Variables:"
    echo "   RUNPOD_VOLUME_PATH=/runpod-volume"
    echo "   MODEL_CACHE_DIR=/runpod-volume/models"
    echo ""
    echo "📝 How it Works:"
    echo "   - First request: Downloads models to Network Storage (~5-10 min)"
    echo "   - Subsequent requests: Uses cached models (instant startup)"
    echo "   - All containers share the same model files"
    echo "   - No repeated downloads = Lower costs & faster performance"
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi