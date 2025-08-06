#!/bin/bash

# Fast Production Build on RunPod Pod
# Takes advantage of superior bandwidth and GPU acceleration

set -e

echo "⚡ Fast Production Docker Build"
echo "=============================="
echo ""

# Configuration
IMAGE_NAME="nandtjm/kiss-video-generator"
TAG="${BUILD_TAG:-production}"
FULL_IMAGE="${IMAGE_NAME}:${TAG}"

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Build optimizations
echo "🏗️ Build Optimizations:"
echo "  ✅ Docker BuildKit enabled"
echo "  ✅ Multi-stage caching"
echo "  ✅ Parallel layer builds"
echo "  ✅ Superior RunPod bandwidth"
echo "  ✅ NVMe storage I/O"
echo ""

# Build with optimizations
echo "🚀 Building production image..."
echo "Image: ${FULL_IMAGE}"
echo ""

time docker build \
    --platform=linux/amd64 \
    -f Dockerfile.production \
    -t "${FULL_IMAGE}" \
    --progress=plain \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --cache-from="${FULL_IMAGE}" \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build completed successfully!"
    
    # Show image info
    echo ""
    echo "📊 Image Information:"
    docker images "${FULL_IMAGE}" --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}\\t{{.CreatedAt}}"
    
    # Push to Docker Hub
    echo ""
    read -p "🚀 Push to Docker Hub now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to Docker Hub..."
        time docker push "${FULL_IMAGE}"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 Build and push completed!"
            echo ""
            echo "✅ Image ready: ${FULL_IMAGE}"
            echo "✅ Total time: Fast (RunPod bandwidth advantage)"
            echo "✅ Ready for serverless deployment"
            echo ""
            echo "💡 Update your endpoint to use: ${FULL_IMAGE}"
        fi
    fi
else
    echo "❌ Build failed!"
    exit 1
fi

