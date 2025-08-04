#!/bin/bash

# Minimal Build Script - Fast build without pre-loading models
# Models download at runtime on first request

echo "🚀 Building Minimal Docker Image (No Pre-loaded Models)"
echo "=============================================="

# Build configuration
IMAGE_NAME="kiss-video-generator"
TAG="minimal"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Build Configuration:"
echo "  Image Name: $IMAGE_NAME"
echo "  Tag: $TAG"
echo "  Registry: $REGISTRY"
echo "  Full Image: $FULL_IMAGE"
echo "  Strategy: Runtime model download"
echo ""

# Enable BuildKit for better performance
export DOCKER_BUILDKIT=1

echo "🔨 Building Docker image (fast build without models)..."
echo "📦 Models will be downloaded on first API request"
echo ""

# Build the image
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.minimal \
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
    echo "🚀 Next Steps:"
    echo "  1. Test locally: docker run --platform=linux/amd64 --rm -p 8000:8000 $FULL_IMAGE"
    echo "  2. Push to registry: docker push $FULL_IMAGE"
    echo "  3. Deploy on RunPod with image: $FULL_IMAGE"
    echo ""
    echo "📝 Notes:"
    echo "  - Models (~28GB) will download on first API request"
    echo "  - First video generation will take longer due to model download"
    echo "  - Ensure RunPod instance has sufficient disk space (50GB+)"
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi