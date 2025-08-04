#!/bin/bash

# Alternative Docker Build Script with Reliable Base Image
# Uses standard PyTorch image instead of potentially corrupted RunPod image

set -e  # Exit on any error

echo "🚀 Building with Alternative Reliable Base Image"
echo "=================================================="

# Configuration
IMAGE_NAME="kiss-video-generator"
TAG="production-preloaded"
REGISTRY="nandtjm"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

echo "📋 Build Configuration:"
echo "  Image Name: ${IMAGE_NAME}"
echo "  Tag: ${TAG}"
echo "  Registry: ${REGISTRY}"
echo "  Full Image: ${FULL_IMAGE_NAME}"
echo "  Base Image: pytorch/pytorch:2.1.0-cuda11.8-devel-ubuntu22.04 (alternative)"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Try to pull the alternative base image first
echo "📥 Testing alternative base image download..."
if docker pull --platform=linux/amd64 pytorch/pytorch:2.1.0-cuda11.8-devel-ubuntu22.04; then
    echo "✅ Alternative base image downloaded successfully"
else
    echo "❌ Failed to download alternative base image"
    exit 1
fi

# Use BuildKit for better build performance
export DOCKER_BUILDKIT=1

# Build with alternative Dockerfile
echo "🔨 Building with alternative Dockerfile..."
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.alternative \
    -t "${FULL_IMAGE_NAME}" \
    --progress=plain \
    --no-cache \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker image built successfully with alternative base!"
    echo "📊 Image details:"
    docker images "${FULL_IMAGE_NAME}"
    
    echo ""
    echo "🏷️  Tagged as: ${FULL_IMAGE_NAME}"
    
    # Verify models are in the image
    echo ""
    echo "🔍 Verifying models are included in image..."
    docker run --platform=linux/amd64 --rm "${FULL_IMAGE_NAME}" \
        python3 -c "
import os
models_dir = '/app/models'
wan_path = f'{models_dir}/Wan2.1-I2V-14B-720P'
lora_path = f'{models_dir}/kissing-lora'

print(f'Checking {wan_path}...')
if os.path.exists(wan_path) and os.listdir(wan_path):
    print(f'✅ Wan-AI model found ({len(os.listdir(wan_path))} files)')
else:
    print(f'❌ Wan-AI model NOT found')
    exit(1)

print(f'Checking {lora_path}...')
if os.path.exists(lora_path) and os.listdir(lora_path):
    print(f'✅ Remade-AI LoRA found ({len(os.listdir(lora_path))} files)')
else:
    print(f'❌ Remade-AI LoRA NOT found')
    exit(1)

print('🎉 All models verified in Docker image!')
"
    
    if [ $? -eq 0 ]; then
        echo "✅ Model verification passed!"
        
        echo ""
        echo "🚀 Ready to push:"
        echo "  docker push ${FULL_IMAGE_NAME}"
        
        # Ask if user wants to push
        read -p "📤 Push image to Docker Hub now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "📤 Pushing image to registry..."
            docker push "${FULL_IMAGE_NAME}"
            
            if [ $? -eq 0 ]; then
                echo "✅ Image pushed successfully!"
                echo "🔗 Image URL: ${FULL_IMAGE_NAME}"
            else
                echo "❌ Failed to push image"
                exit 1
            fi
        fi
        
    else
        echo "❌ Model verification failed!"
        exit 1
    fi
    
else
    echo "❌ Docker build failed!"
    exit 1
fi

echo ""
echo "🎉 Alternative build complete!"
echo "   Image: ${FULL_IMAGE_NAME}"
echo "   Base: Standard PyTorch (more reliable)"
echo "   Ready for RunPod deployment!"