#!/bin/bash

# Production Docker Build Script for RunPod Kiss Video API
# This script builds a Docker image with pre-loaded AI models

set -e  # Exit on any error

echo "🚀 Building Production Docker Image with Pre-loaded Models"
echo "=================================================="

# Configuration
IMAGE_NAME="kiss-video-generator"
TAG="production-preloaded"
REGISTRY=${DOCKER_REGISTRY:-"nandtjm"}
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

echo "📋 Build Configuration:"
echo "  Image Name: ${IMAGE_NAME}"
echo "  Tag: ${TAG}"
echo "  Registry: ${REGISTRY}"
echo "  Full Image: ${FULL_IMAGE_NAME}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image (this may take 20-30 minutes due to model downloads)..."
echo "⚠️  Large models (28GB+ Wan-AI) will be downloaded during build"
echo ""

# Use BuildKit for better build performance
export DOCKER_BUILDKIT=1

# Build with production Dockerfile
docker build \
    -f Dockerfile.production \
    -t "${FULL_IMAGE_NAME}" \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker image built successfully!"
    echo "📊 Image details:"
    docker images "${FULL_IMAGE_NAME}"
    
    echo ""
    echo "🏷️  Tagged as: ${FULL_IMAGE_NAME}"
    
    # Verify models are in the image
    echo ""
    echo "🔍 Verifying models are included in image..."
    docker run --rm "${FULL_IMAGE_NAME}" \
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
        echo "🚀 Next steps:"
        echo "  1. Push to registry: docker push ${FULL_IMAGE_NAME}"
        echo "  2. Deploy on RunPod using image: ${FULL_IMAGE_NAME}"
        echo "  3. Models will load instantly (no runtime downloads!)"
        
        # Ask if user wants to push
        read -p "📤 Push image to registry now? (y/N): " -n 1 -r
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
echo "🎉 Production build complete!"
echo "   Image: ${FULL_IMAGE_NAME}"
echo "   Size: $(docker images --format 'table {{.Size}}' ${FULL_IMAGE_NAME} | tail -1)"
echo "   Models: Pre-loaded (Wan-AI + Remade-AI LoRA)"
echo "   Ready for RunPod deployment!"