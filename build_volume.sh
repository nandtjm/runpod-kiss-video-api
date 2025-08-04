#!/bin/bash

# Volume-based Build Script
# Professional model management strategy used by real AI services

echo "🚀 Building Volume-Based Docker Image"
echo "====================================="

# Build configuration
IMAGE_NAME="kiss-video-generator"
TAG="volume-ready"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Build Configuration:"
echo "  Image Name: $IMAGE_NAME"
echo "  Tag: $TAG"
echo "  Registry: $REGISTRY"
echo "  Full Image: $FULL_IMAGE"
echo "  Strategy: Pre-loaded Volume (Professional)"
echo ""

echo "💡 Volume Strategy Benefits:"
echo "  ✅ Small Docker image (~2-3GB vs 30GB+)"
echo "  ✅ Instant container startup (no downloads)"
echo "  ✅ Models shared across all containers"
echo "  ✅ Cost-effective ($2-5/month vs API fees)"
echo "  ✅ Full control and customization"
echo "  ✅ Used by: ComfyUI Cloud, Automatic1111, etc."
echo ""

# Enable BuildKit
export DOCKER_BUILDKIT=1

echo "🔨 Building Docker image (lightweight - no models included)..."
echo "📁 Models will be loaded from pre-configured volume"
echo ""

# Build the image
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.volume \
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
    echo "🚀 Deployment Steps:"
    echo ""
    echo "1. Push to Docker Hub:"
    echo "   docker push $FULL_IMAGE"
    echo ""
    echo "2. Setup RunPod Network Volume (if not done):"
    echo "   - Create 100GB+ Network Volume in RunPod"
    echo "   - Run setup_volume.sh on RunPod instance"
    echo ""
    echo "3. Create RunPod Serverless Endpoint:"
    echo "   - Docker Image: $FULL_IMAGE"
    echo "   - Network Volume: Attach your pre-loaded volume to /workspace"
    echo "   - GPU: RTX 4090 or A100"
    echo "   - Memory: 32GB+"
    echo ""
    echo "4. Test Deployment:"
    echo "   - First request: Instant startup (models already loaded)"
    echo "   - No downloads, no timeouts, no auth issues"
    echo ""
    echo "📝 How It Works:"
    echo "   Container starts → Mounts volume → Models ready instantly"
    echo "   No 28GB downloads, no network issues, just works!"
    echo ""
    echo "💰 Cost Comparison:"
    echo "   Volume Strategy: $2-5/month + compute"
    echo "   API Services: $0.20+ per video"
    echo "   Break-even: ~25 videos/month"
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi