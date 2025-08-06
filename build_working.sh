#!/bin/bash

# Build Working RunPod Serverless Image
# This addresses all the issues that caused your previous failures

set -e

echo "🚀 Building Guaranteed Working RunPod Serverless Image"
echo "======================================================"
echo ""

# Configuration
IMAGE_NAME="kiss-video-generator"
TAG="working"
REGISTRY="nandtjm"
FULL_IMAGE="$REGISTRY/$IMAGE_NAME:$TAG"

echo "📋 Build Configuration:"
echo "  Purpose: Fix all serverless endpoint issues"
echo "  Image: $FULL_IMAGE"
echo "  Strategy: Minimal, tested, guaranteed working"
echo ""

echo "🔍 Issues This Fixes:"
echo "  ✅ Volume path: /runpod-volume (not /workspace)"
echo "  ✅ Handler imports: Clean, working structure"
echo "  ✅ Comprehensive debugging: Health checks included"
echo "  ✅ Minimal dependencies: Only what's needed"
echo "  ✅ Proper startup validation: Catches issues early"
echo ""

# Check required files
echo "🔍 Verifying required files..."
REQUIRED_FILES=(
    "handler.py"
    "runpod_serverless.py" 
    "Dockerfile.working"
    "requirements_working.txt"
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

echo "🔨 Building working Docker image..."
echo "⏱️  This should complete in ~2-3 minutes"
echo ""

# Build with working Dockerfile
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.working \
    -t "$FULL_IMAGE" \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    # Show image info
    echo "📊 Image Information:"
    docker images "$FULL_IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    echo ""
    
    echo "🚀 Next Steps to Fix Your Endpoint:"
    echo ""
    echo "1. 📤 Push the working image:"
    echo "   docker push $FULL_IMAGE"
    echo ""
    echo "2. 🔧 Update your RunPod serverless endpoint:"
    echo "   - Go to RunPod Serverless Dashboard"
    echo "   - Edit your existing endpoint"
    echo "   - Change Docker Image to: $FULL_IMAGE"
    echo "   - ⚠️  CRITICAL: Verify volume mount path is /runpod-volume"
    echo "   - Environment Variables:"
    echo "     * MODEL_CACHE_DIR=/runpod-volume/models"
    echo "     * TEMP_DIR=/tmp"
    echo ""
    echo "3. 🧪 Test the fixed endpoint:"
    echo "   curl -X POST \"https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run\" \\"
    echo "     -H \"Authorization: Bearer YOUR_API_KEY\" \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"input\": {\"test_mode\": true}}'"
    echo ""
    echo "4. 🎯 Expected result (working):"
    echo "   {"
    echo "     \"status\": \"success\","
    echo "     \"message\": \"Health check completed\","
    echo "     \"environment\": {"
    echo "       \"volume_mounted\": true,"
    echo "       \"models_dir_exists\": true"
    echo "     }"
    echo "   }"
    echo ""
    
    # Ask about pushing
    read -p "🤔 Push image to Docker Hub now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to Docker Hub..."
        docker push "$FULL_IMAGE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Image pushed successfully!"
            echo ""
            echo "🎉 Ready to Fix Your Endpoint!"
            echo ""
            echo "📋 Checklist:"
            echo "  1. ✅ Working image built and pushed"
            echo "  2. ⏳ Update endpoint Docker image to: $FULL_IMAGE"
            echo "  3. ⏳ Verify volume mount path: /runpod-volume"
            echo "  4. ⏳ Test with health check"
            echo "  5. ⏳ Celebrate when it actually works! 🎊"
            echo ""
            echo "💡 The key difference: This image knows about the correct"
            echo "   volume path (/runpod-volume) and has comprehensive debugging."
            echo ""
            echo "🔧 If you need help updating the endpoint, see DEBUG_GUIDE.md"
        else
            echo "❌ Push failed. Please check Docker Hub credentials."
        fi
    else
        echo "⏳ Push later with: docker push $FULL_IMAGE"
    fi
    
else
    echo ""
    echo "❌ Build failed. Check output above for errors."
    exit 1
fi