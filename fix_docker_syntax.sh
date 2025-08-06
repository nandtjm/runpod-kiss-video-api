#!/bin/bash

# Fix Docker Init Script Syntax Error
# Repair the corrupted Docker init script

set -e

echo "🔧 Fixing Docker Init Script Syntax Error"
echo "========================================="
echo ""

echo "❌ Issue: Docker init script corrupted with syntax error"
echo "   Error: Syntax error: 'fi' unexpected"
echo ""

# Restore original Docker init script if backup exists
if [ -f /etc/init.d/docker.backup ]; then
    echo "🔄 Restoring original Docker init script from backup..."
    cp /etc/init.d/docker.backup /etc/init.d/docker
    echo "✅ Original Docker init script restored"
else
    echo "⚠️  No backup found, reinstalling Docker init script..."
    
    # Reinstall Docker to get fresh init script
    apt-get update
    apt-get install --reinstall -y docker-ce
    echo "✅ Docker init script reinstalled"
fi

# Make sure the script is executable
chmod +x /etc/init.d/docker

echo ""
echo "🚀 Starting Docker with proper service command..."

# Try different methods to start Docker
echo "Method 1: Using systemctl..."
if systemctl start docker 2>/dev/null; then
    echo "✅ Docker started with systemctl"
elif service docker start 2>/dev/null; then
    echo "✅ Docker started with service command"  
else
    echo "⚠️  Service commands failed, trying manual start..."
    
    # Manual start without init script
    echo "🐳 Starting Docker daemon manually..."
    
    # Kill any existing processes
    pkill dockerd 2>/dev/null || true
    pkill containerd 2>/dev/null || true
    sleep 2
    
    # Create necessary directories
    mkdir -p /var/lib/docker
    mkdir -p /var/run/docker
    
    # Start containerd first
    containerd > /var/log/containerd.log 2>&1 &
    sleep 3
    
    # Start Docker daemon
    dockerd \
        --host=unix:///var/run/docker.sock \
        --host=tcp://0.0.0.0:2376 \
        --containerd=/run/containerd/containerd.sock \
        --storage-driver=overlay2 \
        > /var/log/dockerd.log 2>&1 &
    
    echo "⏳ Waiting for Docker to initialize..."
    sleep 10
fi

# Test Docker functionality
echo ""
echo "🧪 Testing Docker..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker is working!"
    
    echo ""
    echo "📋 Docker Status:"
    echo "Docker version: $(docker --version)"
    echo "Docker info: OK"
    echo "Docker daemon: Running"
    
    echo ""
    echo "🎯 Ready to build! Run:"
    echo "   bash build_production_ultra_fast.sh"
    
else
    echo "❌ Docker still not working"
    echo ""
    echo "🔍 Debug Information:"
    echo "Docker processes:"
    ps aux | grep -E '(docker|containerd)' | grep -v grep
    
    echo ""
    echo "Docker socket:"
    ls -la /var/run/docker.sock 2>/dev/null || echo "Socket not found"
    
    echo ""
    echo "Docker logs:"
    tail -10 /var/log/dockerd.log 2>/dev/null || echo "No Docker logs"
    
    echo ""
    echo "💡 Alternative Solutions:"
    echo "========================"
    echo ""
    echo "1. 🔄 Try different Pod template:"
    echo "   - Terminate this Pod"
    echo "   - Create new Pod with 'Ubuntu 22.04 + Docker' template"
    echo "   - Or 'Development Environment' template"
    echo ""
    echo "2. 🏠 Build locally (guaranteed to work):"
    echo "   - Download files to your machine"
    echo "   - docker build -f Dockerfile.production -t nandtjm/kiss-video-generator:production ."
    echo "   - docker push nandtjm/kiss-video-generator:production"
    echo ""
    echo "3. 🚀 Direct serverless deploy:"
    echo "   - Skip Docker build entirely" 
    echo "   - Deploy handler.production.py directly to serverless"
    echo "   - Use base image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
    echo ""
fi

echo ""
echo "📊 Current Pod Status:"
echo "====================="
echo "Pod ID: $(hostname)"
echo "Template: $(cat /etc/runpod-release 2>/dev/null || echo 'Unknown')"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'No GPU info')"
echo "Docker issue: Container ulimit restrictions"
echo ""
echo "💰 Cost consideration: This Pod is still billing while troubleshooting"
echo "🎯 Recommendation: Consider local build or different Pod template"