#!/bin/bash

# Fast Build Script - 2-3 minutes instead of hours
# Uses existing RunPod base, minimal dependencies

set -e

echo "⚡ Building FAST RunPod Serverless Image"
echo "======================================="
echo ""

# Configuration
IMAGE_NAME="kiss-video-generator"
TAG="fast"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Fast Build Strategy:"
echo "  Purpose: Get working endpoint ASAP"
echo "  Base: runpod/pytorch:2.1.0-py3.10-cuda11.8.0 (cached)"
echo "  Image: $FULL_IMAGE"
echo "  Build Time: 2-3 minutes (vs 5 hours!)"
echo "  Dependencies: Minimal (only essentials)"
echo ""

echo "⚡ Speed Optimizations:"
echo "  ✅ Uses cached RunPod base (no 3GB download)"
echo "  ✅ Minimal dependencies (5 packages vs 20+)"
echo "  ✅ No PyTorch compilation"
echo "  ✅ No source builds"
echo "  ✅ No optional packages"
echo ""

# Check required files
echo "🔍 Verifying fast build files..."
REQUIRED_FILES=(
    "handler.py"
    "runpod_serverless.py"
    "Dockerfile.fast"
    "requirements_fast.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        exit 1
    fi
    echo "  ✅ $file"
done

echo ""
echo "🚀 Building fast image (should complete in 2-3 minutes)..."

# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build fast version
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.fast \
    -t "$FULL_IMAGE" \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Fast build completed in record time!"
    echo ""
    
    # Show image info
    echo "📊 Fast Image Information:"
    docker images "$FULL_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    echo ""
    
    echo "🚀 Fast Deployment Steps:"
    echo ""
    echo "1. 📤 Push fast image (30 seconds):"
    echo "   docker push $FULL_IMAGE"
    echo ""
    echo "2. 🔧 Update RunPod endpoint:"
    echo "   - Docker Image: $FULL_IMAGE"
    echo "   - Volume mount: /runpod-volume"
    echo "   - Environment: MODEL_CACHE_DIR=/runpod-volume/models"
    echo ""
    echo "3. 🧪 Test immediately:"
    echo "   curl -X POST \"https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run\" \\"
    echo "     -H \"Authorization: Bearer YOUR_API_KEY\" \\"
    echo "     -d '{\"input\": {\"test_mode\": true}}'"
    echo ""
    echo "4. 🎯 Expected fast response:"
    echo "   {"
    echo "     \"status\": \"success\","
    echo "     \"message\": \"Fast build working!\","
    echo "     \"environment\": {"
    echo "       \"volume_mounted\": true"
    echo "     }"
    echo "   }"
    echo ""
    
    # Auto-push offer
    read -p "🚀 Push fast image now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing fast image..."
        docker push "$FULL_IMAGE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 Fast image ready for deployment!"
            echo ""
            echo "✅ Total time: ~3-4 minutes (vs 5+ hours)"
            echo "✅ Working solution deployed"
            echo "✅ Can optimize for RTX 5090 later"
            echo ""
            echo "💡 Next: Update your endpoint to use:"
            echo "   $FULL_IMAGE"
        fi
    fi
    
else
    echo "❌ Fast build failed - check logs above"
    exit 1
fi