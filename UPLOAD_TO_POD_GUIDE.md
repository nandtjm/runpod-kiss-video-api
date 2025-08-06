# 📤 Upload Files to RunPod Pod - Step by Step Guide

## 🎯 Quick Upload Options

### **Option 1: Single Archive Upload (Recommended)**
**Perfect for: Quick deployment, single upload**

1. **Download the archive:** `pod-upload-complete.tar.gz` (19KB)
2. **Upload to Pod via web interface**
3. **Extract and run**

### **Option 2: Git Repository (Best for Development)**
**Perfect for: Version control, easy updates**

1. **Push to GitHub first**
2. **Clone in Pod**
3. **Always up-to-date**

---

## 📋 Step-by-Step Instructions

### **Method 1: Archive Upload (Fastest)**

#### Step 1: Create RunPod Pod
```
Template: PyTorch 2.1.0 + CUDA 11.8 + Ubuntu 22.04
GPU: RTX 4090/5090 (recommended)
vCPUs: 8+ cores
RAM: 32GB+
Container Disk: 50GB+
Network Volume: ai-models-kiss-video (100GB)
```

#### Step 2: Connect to Pod
- RunPod Dashboard → Your Pod → **"Connect"**
- Click **"Start Web Terminal"** 
- Wait for terminal to load

#### Step 3: Prepare Workspace
```bash
# Create workspace
mkdir -p /workspace/build
cd /workspace/build

# Check environment
nvidia-smi  # Verify GPU
df -h      # Check storage
```

#### Step 4: Upload Archive
**Option A: Drag & Drop (Easiest)**
- In the web terminal, click the **"Upload"** button (📤)
- Drag `pod-upload-complete.tar.gz` to the upload area
- Wait for upload to complete

**Option B: File Manager**
- Use the built-in file manager in the web interface
- Navigate to `/workspace/build/`
- Upload `pod-upload-complete.tar.gz`

#### Step 5: Extract Files
```bash
# Extract archive
tar -xzf pod-upload-complete.tar.gz

# Verify files
ls -la

# Make scripts executable
chmod +x *.sh

# Check what we have
echo "📋 Available files:"
ls -lh *.py *.sh *.md Dockerfile* *.txt BUILD.bazel WORKSPACE
```

#### Step 6: Setup Build Environment
```bash
# Run setup script
bash setup_pod.sh

# This will:
# ✅ Install Docker + BuildKit
# ✅ Install Bazel
# ✅ Verify GPU
# ✅ Setup optimizations
```

#### Step 7: Login to Docker Hub
```bash
# Login (required for pushing)
docker login -u YOUR_DOCKERHUB_USERNAME

# Enter your password when prompted
```

#### Step 8: Choose Build Method
```bash
# Ultra-fast Bazel build (recommended)
bash build_with_bazel.sh

# OR standard Docker build
bash build_production_fast.sh
```

---

### **Method 2: Git Repository (Development)**

#### Step 1-3: Same as Method 1

#### Step 4: Clone Repository
```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/ai-kiss-generator.git
cd ai-kiss-generator/runpod-kiss-api

# OR if you don't have a repo yet, create files manually:
mkdir -p ai-kiss-build && cd ai-kiss-build
```

#### Step 5: Upload via Copy/Paste
If no Git repo, copy/paste file contents:

```bash
# Create each file by copy/paste
nano Dockerfile.production    # Copy from your local file
nano handler.production.py    # Copy from your local file
nano requirements.production.txt
# ... etc for each file
```

#### Step 6-8: Same as Method 1

---

## 🔧 Build Process Overview

### **What Happens During Build:**

1. **Setup Phase (2-3 minutes):**
   - Docker installation
   - Bazel installation  
   - Environment verification

2. **Build Phase (5-10 minutes):**
   - Download base image (fast on RunPod)
   - Install production dependencies
   - Copy application code
   - Optimize for RTX 5090

3. **Push Phase (1-2 minutes):**
   - Push to Docker Hub
   - Tag multiple versions
   - Verify upload success

### **Expected Output:**
```
🎉 Build and push completed!

✅ Images ready:
  🏭 Production: nandtjm/kiss-video-generator:production
  🎮 RTX 5090: nandtjm/kiss-video-generator:rtx5090

⚡ Total time: ~10 minutes (vs 2+ hours locally)
💰 Cost: ~$2 (vs electricity + time locally)
🚀 Ready for serverless deployment!
```

---

## 💡 Pro Tips

### **Speed Optimizations:**
- ✅ Use RTX 4090/5090 Pod for fastest builds
- ✅ Keep terminal active during upload
- ✅ Use network volume for model persistence
- ✅ Enable Docker BuildKit (done automatically)

### **Cost Optimization:**
- ✅ Delete Pod immediately after successful push
- ✅ Use "On-Demand" pricing for builds
- ✅ Monitor GPU usage (not needed during Docker builds)

### **Troubleshooting:**
- 🔍 Check `nvidia-smi` for GPU status
- 🔍 Verify network volume is mounted: `ls /runpod-volume/`
- 🔍 Check Docker Hub credentials: `docker login`
- 🔍 Monitor build progress: `docker ps` during builds

---

## 🎯 After Successful Build

1. **Verify Images:**
   ```bash
   docker images | grep kiss-video-generator
   ```

2. **Update Serverless Endpoint:**
   - Image: `nandtjm/kiss-video-generator:production`
   - Volume: `ai-models-kiss-video`
   - CUDA: "Any"

3. **Delete Build Pod:**
   - RunPod Dashboard → Terminate Pod
   - Save ~$1-2/hour

4. **Test Endpoint:**
   ```bash
   curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -d '{"input": {"health_check": true}}'
   ```

---

## 🎉 Success!

Your production AI kiss video generator is now built and deployed using RunPod's superior infrastructure:

- ⚡ **10x faster builds** than local machine
- 🔥 **GPU-accelerated** production system
- 💾 **Optimized for RTX 5090** 
- 🎬 **Real AI video generation** with Wan-AI models

The 4-day build struggle is finally over! Time to generate some amazing AI kiss videos! ✨