# 🔧 Fix Docker Build Issues (ARM64 Mac → AMD64 RunPod)

## 🚨 **Issues Fixed:**
1. **Platform Mismatch**: Building AMD64 image on ARM64 Mac
2. **Corrupted Base Image**: "short read" error from incomplete download

## 🛠️ **Quick Fix Commands:**

### **Step 1: Clean Up Corrupted Images**
```bash
cd "/Users/nandlal/Local Sites/projects/ai-kiss-video-app/ai-kiss-generator/runpod-kiss-api"

# Clean Docker cache and corrupted images
docker system prune -f
docker builder prune -f

# Remove any partial/corrupted images
docker rmi runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04 --force || true
```

### **Step 2: Pull Fresh Base Image with Correct Platform**
```bash
# Pull AMD64 base image explicitly
docker pull --platform=linux/amd64 runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
```

### **Step 3: Build with Platform Specification**
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build for AMD64 platform (RunPod compatible)
docker build \
    --platform=linux/amd64 \
    -f Dockerfile.production \
    -t nandtjm/kiss-video-generator:production-preloaded \
    --progress=plain \
    --no-cache \
    .
```

### **Alternative: Use Updated Automated Script**
```bash
# Pull latest fixes
git pull origin main

# Run updated build script (includes all fixes)
chmod +x build_production.sh
./build_production.sh
```

## 📋 **What Changed:**

### **Dockerfile.production:**
- Added `--platform=linux/amd64` to FROM statement
- Forces AMD64 build even on ARM64 Mac

### **build_production.sh:**
- Added Docker cache cleanup
- Explicit base image pull with platform
- Added `--platform=linux/amd64` to build command
- Added `--no-cache` to avoid corrupted cache

## ⚠️ **Important Notes:**

### **Cross-Platform Building:**
- **Your Mac**: ARM64 (Apple Silicon)
- **RunPod**: AMD64 (Intel/NVIDIA GPUs)
- **Solution**: Build AMD64 image on ARM64 Mac using emulation

### **Performance Impact:**
- **Slower build** on ARM64 Mac (emulation overhead)
- **Larger memory usage** during build
- **Final image works perfectly** on RunPod AMD64

### **Expected Behavior:**
- ✅ **Warning about platform mismatch**: This is expected and safe to ignore
- ✅ **Slower build times**: ARM64 → AMD64 emulation
- ✅ **Final image**: Works perfectly on RunPod

## 🎯 **Verification Commands:**

### **Check Image Platform:**
```bash
# Verify built image is AMD64
docker inspect nandtjm/kiss-video-generator:production-preloaded \
    --format='{{.Architecture}}'
# Should output: amd64
```

### **Test Image Locally (with emulation):**
```bash
# Test that models are included
docker run --platform=linux/amd64 --rm \
    nandtjm/kiss-video-generator:production-preloaded \
    python3 -c "
import os
print('Wan-AI model:', os.path.exists('/app/models/Wan2.1-I2V-14B-720P'))
print('LoRA model:', os.path.exists('/app/models/kissing-lora'))
"
```

## 🚀 **After Successful Build:**

```bash
# Push to Docker Hub
docker push nandtjm/kiss-video-generator:production-preloaded

# Deploy on RunPod with image:
# nandtjm/kiss-video-generator:production-preloaded
```

## 🐛 **If Still Failing:**

### **Alternative Base Images:**
If the RunPod base image continues to have issues, try:
```dockerfile
FROM --platform=linux/amd64 pytorch/pytorch:2.1.0-cuda11.8-devel-ubuntu22.04
```

### **Check Docker Desktop Settings:**
- Ensure **"Use Rosetta for x86/amd64 emulation"** is enabled
- Docker Desktop → Settings → General → Use Rosetta

### **Manual Platform Check:**
```bash
# Check what platforms are available
docker buildx ls
```

The fixes ensure your ARM64 Mac can build AMD64 images for RunPod deployment!