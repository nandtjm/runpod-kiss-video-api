#!/bin/bash

# Optimized Build Script - Uses Pre-downloaded Models
# Run this AFTER models are downloaded locally

echo "🚀 Building Optimized Docker Image with Pre-downloaded Models"
echo "=================================================="

# Build configuration
IMAGE_NAME="kiss-video-generator"
TAG="production-optimized"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Build Configuration:"
echo "  Image Name: $IMAGE_NAME"
echo "  Tag: $TAG"
echo "  Registry: $REGISTRY"
echo "  Full Image: $FULL_IMAGE"
echo ""

# Check if models exist locally
echo "🔍 Checking for pre-downloaded models..."
if [ ! -d "./models/Wan2.1-I2V-14B-720P" ]; then
    echo "❌ Wan-AI model not found in ./models/"
    echo "   Please run: python3 download_models_direct.py"
    exit 1
fi

MODEL_SIZE=$(du -sh ./models/Wan2.1-I2V-14B-720P | cut -f1)
echo "✅ Found Wan-AI model: $MODEL_SIZE"

if [ ! -d "./models/kissing-lora" ]; then
    echo "⚠️  Kissing LoRA model not found (optional)"
fi

echo ""

# Enable BuildKit for better performance
export DOCKER_BUILDKIT=1

echo "🔨 Building Docker image (this should be much faster!)..."
echo "📦 Using COPY strategy instead of downloading models"
echo ""

# Build the image
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.optimized \
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
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi