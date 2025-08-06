#!/bin/bash

# Fix Docker Daemon Not Running Issue
# Start Docker service and verify it's working

set -e

echo "🔧 Fixing Docker Daemon Issue"
echo "============================="
echo ""

echo "❌ Issue Detected: Docker daemon not running"
echo "   Error: Cannot connect to unix:///var/run/docker.sock"
echo ""

echo "🚀 Starting Docker daemon..."

# Start Docker service
service docker start

# Wait for Docker to fully start
echo "⏳ Waiting for Docker daemon to initialize..."
sleep 5

# Check Docker status
if systemctl is-active --quiet docker; then
    echo "✅ Docker daemon is now running"
else
    echo "⚠️  Starting Docker manually..."
    dockerd &
    sleep 10
fi

# Verify Docker is working
echo ""
echo "🧪 Testing Docker functionality..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker is working properly!"
    
    echo ""
    echo "📋 Docker System Info:"
    docker version --format 'Client: {{.Client.Version}}'
    docker version --format 'Server: {{.Server.Version}}'
    
    # Show available resources
    echo ""
    echo "💾 System Resources:"
    echo "  CPU cores: $(nproc)"
    echo "  Memory: $(free -h | awk '/^Mem:/ {print $2}')"
    echo "  Disk space: $(df -h / | awk 'NR==2 {print $4}') available"
    
    # Check GPU access from Docker
    echo ""
    echo "🎮 GPU Access Check:"
    if command -v nvidia-smi >/dev/null 2>&1; then
        echo "✅ NVIDIA drivers available"
        docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "⚠️  GPU access from Docker needs testing"
    else
        echo "⚠️  NVIDIA drivers not found"
    fi
    
    echo ""
    echo "🎯 Ready to build! Run:"
    echo "   bash build_production_ultra_fast.sh"
    
else
    echo "❌ Docker still not working. Let's troubleshoot..."
    
    echo ""
    echo "🔍 Troubleshooting Steps:"
    
    # Check if Docker is installed
    if command -v docker >/dev/null 2>&1; then
        echo "✅ Docker is installed"
    else
        echo "❌ Docker not installed. Installing..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
    fi
    
    # Check Docker service status
    echo ""
    echo "📊 Docker Service Status:"
    systemctl status docker --no-pager -l
    
    # Try starting Docker differently
    echo ""
    echo "🔄 Alternative Docker start methods..."
    
    # Method 1: Direct systemctl
    echo "  Method 1: systemctl start docker"
    systemctl start docker && echo "    ✅ Success" || echo "    ❌ Failed"
    
    # Method 2: Service command
    echo "  Method 2: service docker start"
    service docker start && echo "    ✅ Success" || echo "    ❌ Failed"
    
    # Method 3: Manual dockerd
    echo "  Method 3: Starting dockerd manually..."
    pkill dockerd 2>/dev/null || true
    dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2376 &
    sleep 10
    docker info >/dev/null 2>&1 && echo "    ✅ Manual start successful" || echo "    ❌ Manual start failed"
fi

echo ""
echo "💡 Pro Tips:"
echo "============"
echo "  ✅ Always start Docker daemon before building"
echo "  ✅ Docker should auto-start on most RunPod templates"
echo "  ✅ If issues persist, try a different Pod template"
echo "  ✅ PyTorch templates usually have Docker pre-configured"
echo ""