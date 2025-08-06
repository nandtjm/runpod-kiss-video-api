#!/bin/bash

# Build Serverless-Optimized Docker Image
# Uses network volume models - No model downloads!

set -e

echo "🚀 Building Serverless-Optimized AI Kiss Generator"
echo "================================================="
echo ""

echo "💡 Serverless Optimization Strategy:"
echo "  ✅ Uses pre-existing network volume models"
echo "  ✅ No model downloads during build"
echo "  ✅ Lightweight image (2GB vs 8GB+)"
echo "  ✅ Fast serverless cold starts"
echo "  ✅ Superior RunPod bandwidth for dependencies only"
echo ""

# Configuration
IMAGE_NAME="nandtjm/kiss-video-generator"
TAG="serverless"
FULL_IMAGE="${IMAGE_NAME}:${TAG}"

# Enable Docker BuildKit
export DOCKER_BUILDKIT=1

echo "📋 Build Configuration:"
echo "  Image: ${FULL_IMAGE}"
echo "  Dockerfile: Dockerfile.serverless"
echo "  Strategy: Network volume optimized"
echo "  Expected size: ~2GB (vs 8GB+ with embedded models)"
echo ""

# Check required files
echo "🔍 Verifying serverless build files..."
REQUIRED_FILES=(
    "Dockerfile.serverless"
    "handler.serverless.py"
    "requirements.serverless.txt"
    "runpod_serverless.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        exit 1
    fi
    echo "  ✅ $file"
done

echo ""
echo "🏗️ Building serverless-optimized image..."
echo ""

time docker build \
    --platform=linux/amd64 \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --cache-from="${FULL_IMAGE}" \
    -f Dockerfile.serverless \
    -t "${FULL_IMAGE}" \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Serverless build completed!"
    
    # Show image comparison
    echo ""
    echo "📊 Image Size Comparison:"
    echo "========================="
    echo "Previous production image (with embedded models):"
    docker images "${IMAGE_NAME}:production" --format "  {{.Repository}}:{{.Tag}}  {{.Size}}" 2>/dev/null || echo "  Not available"
    echo ""
    echo "New serverless image (network volume optimized):"
    docker images "${FULL_IMAGE}" --format "  {{.Repository}}:{{.Tag}}  {{.Size}}"
    
    # Push to Docker Hub
    echo ""
    read -p "🚀 Push serverless image to Docker Hub? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing serverless image..."
        time docker push "${FULL_IMAGE}"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 Serverless Image Deployed Successfully!"
            echo "========================================"
            echo ""
            echo "✅ Image: ${FULL_IMAGE}"
            echo "✅ Optimized for network volume models"
            echo "✅ Fast serverless deployment"
            echo "✅ No model downloads required"
            echo ""
            echo "🚀 Deployment Instructions:"
            echo "=========================="
            echo ""
            echo "1. Create RunPod Serverless Endpoint:"
            echo "   - Docker Image: ${FULL_IMAGE}"
            echo "   - Network Volume: ai-models-kiss-video (100GB)"
            echo "   - Mount Path: /runpod-volume"
            echo "   - GPU: RTX 4090/5090"
            echo ""
            echo "2. Environment Variables:"
            echo "   MODEL_CACHE_DIR=/runpod-volume/models"
            echo "   CUDA_LAUNCH_BLOCKING=0"
            echo ""
            echo "3. Test Health Check:"
            echo '   curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \'
            echo '     -H "Authorization: Bearer YOUR_API_KEY" \'
            echo '     -d '"'"'{"input": {"health_check": true}}'"'"''
            echo ""
            echo "4. Expected Response:"
            echo '   {"status": "healthy", "models_ready": true}'
            echo ""
            echo "5. Generate Kiss Video:"
            echo '   curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \'
            echo '     -H "Authorization: Bearer YOUR_API_KEY" \'
            echo '     -d '"'"'{"input": {"source_image": "BASE64_IMG1", "target_image": "BASE64_IMG2"}}'"'"''
            echo ""
            echo "🎯 Key Benefits:"
            echo "==============="
            echo "  ⚡ 70% smaller image size"
            echo "  🚀 Faster cold starts"
            echo "  💰 Lower compute costs"
            echo "  📦 Uses your existing network volume models"
            echo "  🔥 Same AI video quality"
            echo ""
            echo "🎬 Ready to generate AI kiss videos with your network volume models! ✨"
        fi
    else
        echo ""
        echo "ℹ️  Image built but not pushed. You can push later with:"
        echo "   docker push ${FULL_IMAGE}"
    fi
else
    echo "❌ Build failed!"
    echo ""
    echo "🔍 Common Issues:"
    echo "  - Docker daemon not running"
    echo "  - Missing build files"
    echo "  - Network connectivity issues"
    echo "  - Insufficient disk space"
    echo ""
    exit 1
fi

echo ""
echo "💡 Why This Approach Is Superior:"
echo "================================="
echo ""
echo "❌ Old approach (Dockerfile.production):"
echo "  - Downloaded models during build (slow)"
echo "  - 8GB+ image size"
echo "  - Duplicated models (network volume + image)"
echo "  - Expensive bandwidth during build"
echo ""
echo "✅ New approach (Dockerfile.serverless):"
echo "  - Uses existing network volume models"
echo "  - ~2GB image size"
echo "  - Single source of truth for models"
echo "  - Fast builds and deployments"
echo ""
echo "🎯 Result: Same AI generation, optimized infrastructure!"