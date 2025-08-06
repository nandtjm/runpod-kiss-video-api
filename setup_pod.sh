#!/bin/bash

echo "🚀 Setting up RunPod Pod as Docker Build Machine"
echo "=============================================="
echo ""

# Update system
echo "📦 Updating system packages..."
apt update && apt install -y sudo git curl wget unzip htop nvtop

# Install Docker with BuildKit
echo "🐳 Installing Docker with BuildKit..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Enable Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Install Bazel for even faster builds
echo "🔧 Installing Bazel..."
wget https://github.com/bazelbuild/bazelisk/releases/download/v1.20.0/bazelisk-linux-amd64
chmod +x bazelisk-linux-amd64
sudo mv bazelisk-linux-amd64 /usr/local/bin/bazel

# Verify installations
echo ""
echo "✅ Installation Verification:"
echo "  Docker: $(docker --version)"
echo "  Bazel: $(bazel version | head -1)"
echo "  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
echo ""

# Clone repository (replace with your repo)
echo "📂 Cloning AI Kiss Generator repository..."
if [ ! -d "ai-kiss-generator" ]; then
    git clone https://github.com/YOUR_USERNAME/ai-kiss-generator.git
fi

cd ai-kiss-generator/runpod-kiss-api

echo ""
echo "🎯 Build machine ready! Run these commands:"
echo ""
echo "1. Docker Hub login:"
echo "   docker login -u YOUR_USERNAME"
echo ""
echo "2. Fast Docker build:"
echo "   ./build_production_fast.sh"
echo ""  
echo "3. Ultra-fast Bazel build:"
echo "   bazel run //:push_production"
echo ""
echo "4. RTX 5090 optimized build:"
echo "   bazel run //:push_rtx_5090"
echo ""

