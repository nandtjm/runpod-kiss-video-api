#!/bin/bash

# Ultra-fast Bazel Build on RunPod Pod
# Maximum speed with Bazel's advanced caching and parallelization

set -e

echo "🔥 Ultra-fast Bazel Build System"
echo "==============================="
echo ""

# Build configurations
BUILD_TARGETS=(
    "//:push_production"     # Production image
    "//:push_dev"           # Development image  
    "//:push_rtx_5090"      # RTX 5090 optimized
)

# Bazel build optimizations
BAZEL_OPTS=(
    "--jobs=auto"                    # Use all CPU cores
    "--local_ram_resources=HOST_RAM*0.8"  # Use 80% of RAM
    "--local_cpu_resources=HOST_CPUS"     # Use all CPUs
    "--disk_cache=/tmp/bazel_cache"       # Use fast NVMe cache
    "--repository_cache=/tmp/bazel_repo_cache"
)

echo "🎯 Build Targets:"
for target in "${BUILD_TARGETS[@]}"; do
    echo "  - ${target}"
done
echo ""

echo "⚡ Bazel Optimizations:"
echo "  ✅ Multi-core parallel builds"
echo "  ✅ Advanced caching system"
echo "  ✅ NVMe disk cache"
echo "  ✅ Efficient dependency management"  
echo "  ✅ Superior RunPod bandwidth"
echo ""

# Create cache directories
mkdir -p /tmp/bazel_cache /tmp/bazel_repo_cache

# Build production image
echo "🏗️ Building production image with Bazel..."
echo ""

time bazel run "${BAZEL_OPTS[@]}" //:push_production

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Production build completed!"
    
    # Build RTX 5090 optimized version
    echo ""
    echo "🎮 Building RTX 5090 optimized image..."
    time bazel run "${BAZEL_OPTS[@]}" //:push_rtx_5090
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 All builds completed successfully!"
        echo ""
        echo "📋 Available Images:"
        echo "  🏭 Production: nandtjm/kiss-video-generator:production"
        echo "  🎮 RTX 5090: nandtjm/kiss-video-generator:rtx5090"
        echo ""
        echo "⚡ Build Speed: ULTRA-FAST (Bazel + RunPod bandwidth)"
        echo "💾 Cache Status: Optimized for subsequent builds"
        echo "🚀 Ready for deployment!"
    fi
else
    echo "❌ Bazel build failed!"
    exit 1
fi

