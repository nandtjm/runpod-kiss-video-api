#!/bin/bash

# Alternative Build Without Docker - Direct Push Method
# For when Docker daemon won't start in containers

set -e

echo "🔄 Alternative Build Method - No Docker Required"
echo "==============================================="
echo ""

echo "💡 This method builds the image WITHOUT Docker daemon:"
echo "  ✅ Uses container registry API directly"
echo "  ✅ Leverages RunPod's superior bandwidth"
echo "  ✅ Creates the same production-ready image"
echo "  ✅ No Docker daemon issues"
echo ""

# Check if we're in a container with restricted Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Detected: Running inside a container"
    echo "  This explains the Docker daemon ulimit issues"
    echo "  Using container-friendly build method..."
else
    echo "🖥️  Detected: Running on host system"
fi

echo ""
echo "📦 Building production image using BuildKit..."

# Method 1: Use buildx if available (works in many containers)
if command -v docker >/dev/null 2>&1; then
    echo "🔧 Attempting Docker buildx (container-friendly)..."
    
    # Try to use Docker without daemon
    docker buildx version 2>/dev/null && {
        echo "✅ Docker buildx available"
        
        # Create builder instance
        docker buildx create --name container-builder --driver docker-container 2>/dev/null || true
        docker buildx use container-builder 2>/dev/null || true
        
        # Build using buildx
        docker buildx build \
            --platform linux/amd64 \
            --output type=registry \
            --tag nandtjm/kiss-video-generator:production \
            -f Dockerfile.production \
            . && echo "✅ Buildx build successful!" || echo "❌ Buildx build failed"
    } || echo "⚠️  Buildx not available or failed"
fi

echo ""
echo "🔄 Method 2: Using Buildah (Docker-free building)"

# Install Buildah if not available
if ! command -v buildah >/dev/null 2>&1; then
    echo "📦 Installing Buildah..."
    apt-get update
    apt-get install -y buildah podman
fi

if command -v buildah >/dev/null 2>&1; then
    echo "✅ Buildah available - building without Docker daemon"
    
    # Build with Buildah
    buildah build \
        --format docker \
        --platform linux/amd64 \
        --tag nandtjm/kiss-video-generator:production \
        -f Dockerfile.production \
        . && {
        
        echo "✅ Buildah build successful!"
        
        # Push to registry
        echo "📤 Pushing to Docker Hub with Buildah..."
        buildah push \
            --creds YOUR_USERNAME:YOUR_TOKEN \
            nandtjm/kiss-video-generator:production \
            docker://docker.io/nandtjm/kiss-video-generator:production
            
    } || echo "❌ Buildah build failed"
else
    echo "⚠️  Buildah not available"
fi

echo ""
echo "🔄 Method 3: Remote Build Service"

# Create a build script for remote execution
cat > remote_build.sh << 'EOF'
#!/bin/bash
# This script runs on a system with working Docker

set -e

echo "🏗️ Remote Docker Build"
echo "====================="

# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-kiss-generator.git || {
    echo "📦 Repository not available, using uploaded files"
}

cd ai-kiss-generator/runpod-kiss-api 2>/dev/null || cd /workspace/build

# Build production image
docker build \
    --platform=linux/amd64 \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -f Dockerfile.production \
    -t nandtjm/kiss-video-generator:production \
    .

# Push to registry
docker push nandtjm/kiss-video-generator:production

echo "✅ Remote build completed!"
EOF

chmod +x remote_build.sh

echo "📋 Created remote build script: remote_build.sh"

echo ""
echo "🔄 Method 4: Use RunPod Serverless Builder"

echo "💡 Alternative: Deploy as serverless endpoint directly"
echo ""
echo "Since Docker daemon won't start, consider:"
echo "1. 🚀 Build on your local machine (slower but works):"
echo "   docker build -f Dockerfile.production -t nandtjm/kiss-video-generator:production ."
echo "   docker push nandtjm/kiss-video-generator:production"
echo ""
echo "2. 🐳 Use different RunPod Pod template:"
echo "   - Try 'Development Environment' template"
echo "   - Try 'PyTorch 2.4 + CUDA 12.4' (newer)"
echo "   - Try 'Ubuntu 22.04 + Docker' template"
echo ""
echo "3. ⚡ Use RunPod Serverless directly:"
echo "   - Upload handler.production.py directly to serverless"
echo "   - Use existing base image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
echo "   - Install dependencies at runtime"
echo ""

echo "🎯 Recommended Quick Solution:"
echo "============================="
echo ""
echo "Since you're hitting Docker daemon issues in the container:"
echo ""
echo "Option A: Different Pod Template"
echo "  1. Terminate current Pod"
echo "  2. Create new Pod with 'Development Environment' template"  
echo "  3. Upload files again"
echo "  4. Run build_production_ultra_fast.sh"
echo ""
echo "Option B: Local Build (Guaranteed to work)"
echo "  1. Build locally: docker build -f Dockerfile.production -t nandtjm/kiss-video-generator:production ."
echo "  2. Push: docker push nandtjm/kiss-video-generator:production"
echo "  3. Deploy to serverless endpoint"
echo ""
echo "Option C: Serverless Direct Deploy"
echo "  1. Create serverless endpoint"
echo "  2. Use base image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
echo "  3. Upload handler.production.py directly"
echo "  4. Install deps at runtime with pip"
echo ""

echo "💰 Cost Comparison:"
echo "  Pod with Docker issues: Still billing while troubleshooting"
echo "  Local build: Free (uses your machine)"
echo "  Serverless direct: Only pay for actual AI generation"
echo ""

echo "🚀 My recommendation: Try Option B (local build) for guaranteed success!"