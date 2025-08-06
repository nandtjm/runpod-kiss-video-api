#!/bin/bash

# Fix Docker Daemon ulimit Issue
# Comprehensive solution for Docker daemon startup problems in containers

set -e

echo "🔧 Fixing Docker Daemon ulimit Issue"
echo "===================================="
echo ""

echo "❌ Issue Detected: ulimit error setting limit (Invalid argument)"
echo "   This is common in RunPod containers due to ulimit restrictions"
echo ""

echo "🚀 Applying comprehensive Docker fixes..."
echo ""

# Method 1: Fix ulimit in Docker init script
echo "📝 Method 1: Patching Docker init script..."
if [ -f /etc/init.d/docker ]; then
    # Backup original
    cp /etc/init.d/docker /etc/init.d/docker.backup
    
    # Comment out problematic ulimit line
    sed -i 's/^.*ulimit -n.*$/# &/' /etc/init.d/docker
    sed -i 's/^.*ulimit -p.*$/# &/' /etc/init.d/docker
    sed -i 's/^.*ulimit -c.*$/# &/' /etc/init.d/docker
    
    echo "  ✅ Docker init script patched"
else
    echo "  ⚠️  Docker init script not found"
fi

# Method 2: Start Docker daemon manually with safe parameters
echo ""
echo "🐳 Method 2: Starting Docker daemon manually..."

# Kill any existing Docker processes
pkill dockerd 2>/dev/null || true
pkill docker-containerd 2>/dev/null || true
sleep 2

# Create Docker directories if they don't exist
mkdir -p /var/lib/docker
mkdir -p /var/run/docker
mkdir -p /etc/docker

# Create Docker daemon configuration
cat > /etc/docker/daemon.json << 'EOF'
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "name": "nofile",
      "hard": 65536,
      "soft": 65536
    }
  }
}
EOF

echo "  ✅ Docker daemon config created"

# Start Docker daemon with custom parameters
echo ""
echo "🚀 Starting Docker daemon with safe ulimits..."

dockerd \
  --host=unix:///var/run/docker.sock \
  --host=tcp://0.0.0.0:2376 \
  --storage-driver=overlay2 \
  --default-ulimit nofile=65536:65536 \
  --default-ulimit nproc=8192:8192 \
  > /var/log/dockerd.log 2>&1 &

# Wait for Docker to start
echo "⏳ Waiting for Docker daemon to initialize..."
for i in {1..30}; do
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker daemon started successfully!"
        break
    fi
    echo "  Attempt $i/30..."
    sleep 2
done

# Verify Docker is working
echo ""
echo "🧪 Testing Docker functionality..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker is working properly!"
    
    echo ""
    echo "📋 Docker System Info:"
    docker version --format 'Client: {{.Client.Version}}'
    docker version --format 'Server: {{.Server.Version}}'
    
    echo ""
    echo "💾 Docker Storage:"
    docker system df
    
    echo ""
    echo "🎮 GPU Test:"
    if command -v nvidia-smi >/dev/null 2>&1; then
        echo "✅ NVIDIA drivers available"
        # Test GPU access from Docker
        if docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null; then
            echo "✅ GPU access from Docker works!"
        else
            echo "⚠️  GPU access from Docker needs configuration"
        fi
    else
        echo "⚠️  NVIDIA drivers not found"
    fi
    
    echo ""
    echo "🎯 Docker is ready! You can now run:"
    echo "   bash build_production_ultra_fast.sh"
    
else
    echo "❌ Docker still not working. Trying alternative methods..."
    
    # Method 3: Use Docker from host if available
    echo ""
    echo "🔄 Method 3: Checking for host Docker..."
    if [ -S /var/run/docker.sock.host ]; then
        echo "  ✅ Host Docker socket found"
        ln -sf /var/run/docker.sock.host /var/run/docker.sock
        docker info && echo "  ✅ Host Docker working"
    else
        echo "  ❌ Host Docker not available"
    fi
    
    # Method 4: Install Docker in Docker (dind)
    echo ""
    echo "🐳 Method 4: Installing Docker-in-Docker..."
    
    # Add Docker's official GPG key
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start Docker service
    service docker start
    sleep 5
    
    if docker info >/dev/null 2>&1; then
        echo "✅ Fresh Docker installation working!"
    else
        echo "❌ Fresh Docker installation failed"
    fi
fi

echo ""
echo "📋 Docker Daemon Status Summary:"
echo "================================"
echo "Docker daemon PID: $(pgrep dockerd || echo 'Not running')"
echo "Docker socket: $(ls -la /var/run/docker.sock 2>/dev/null || echo 'Not found')"
echo "Docker info test: $(docker info >/dev/null 2>&1 && echo 'Working' || echo 'Failed')"

echo ""
echo "💡 If Docker still fails:"
echo "========================"
echo "1. Try a different RunPod template (PyTorch 2.1.0 + CUDA 11.8)"
echo "2. Use RunPod serverless instead of Pods for building"
echo "3. Build locally and push (slower but guaranteed to work)"
echo "4. Contact RunPod support for container-specific Docker issues"
echo ""