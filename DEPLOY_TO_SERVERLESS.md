# 🚀 Deploy to RunPod Serverless - Complete Guide

RunPod serverless supports **only** these deployment methods:
1. **Git Repository Import** (Recommended - Easy)
2. **Docker Registry Import** (Advanced)

## 🎯 Method 1: Git Repository Deployment (Recommended)

### **Step 1: Push Files to GitHub**

```bash
# Add all serverless files to git
git add .
git commit -m "Add serverless-optimized AI kiss video generator

- Uses network volume models (no downloads)
- Optimized for RunPod serverless deployment  
- Lightweight handler with real AI generation"

git push origin main
```

### **Step 2: Create RunPod Serverless Endpoint**

1. **Go to RunPod Dashboard** → Serverless
2. **Click "New Endpoint"**
3. **Choose "Source Code" tab**

### **Step 3: Configure Git Import**

```yaml
Repository Type: GitHub
Repository URL: https://github.com/YOUR_USERNAME/ai-kiss-generator
Branch: main
Repository Path: runpod-kiss-api/
```

### **Step 4: Configure Serverless Settings**

#### **Docker Configuration:**
```yaml
Base Image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
Docker Command: python3 handler.serverless.py
```

#### **Environment Variables:**
```yaml
MODEL_CACHE_DIR: /runpod-volume/models
PYTHONPATH: /app
PYTHONUNBUFFERED: 1
CUDA_LAUNCH_BLOCKING: 0
HF_HOME: /runpod-volume/models/.cache
```

#### **Volume Configuration:**
```yaml
Network Volume: ai-models-kiss-video
Mount Path: /runpod-volume
```

#### **GPU Settings:**
```yaml
GPU Types: RTX 4090, RTX 5090
Min GPU Memory: 16GB
Max Workers: 3
Idle Timeout: 5 seconds
```

### **Step 5: Advanced Settings**

```yaml
Container Start Command: pip install -r requirements.serverless.txt && python3 handler.serverless.py
Max Response Size: 100MB (for video base64)
Request Timeout: 300 seconds (5 minutes)
```

---

## 🐳 Method 2: Docker Registry Deployment

### **Step 1: Build Docker Image Locally**

Since Docker won't work on your current Pod, build locally:

```bash
# On your local machine
cd /path/to/your/project/runpod-kiss-api

# Build serverless image
docker build -f Dockerfile.serverless -t nandtjm/kiss-video-generator:serverless .

# Push to Docker Hub
docker push nandtjm/kiss-video-generator:serverless
```

### **Step 2: Create Serverless Endpoint**

1. **RunPod Dashboard** → Serverless → "New Endpoint"  
2. **Choose "Container Image" tab**

#### **Docker Settings:**
```yaml
Container Image: nandtjm/kiss-video-generator:serverless
Container Start Command: python3 handler.serverless.py
```

#### **Volume & Environment:** (Same as Method 1)
```yaml
Network Volume: ai-models-kiss-video
Mount Path: /runpod-volume
Environment Variables: (same as above)
```

---

## 🎯 Recommended Approach: Git Repository

### **Why Git Repository is Better:**

| Git Repository | Docker Registry |
|----------------|-----------------|
| ✅ No Docker build issues | ❌ Requires working Docker |
| ✅ Easy updates via git push | ❌ Rebuild/push for changes |
| ✅ Version control | ❌ Manual versioning |
| ✅ Immediate deployment | ❌ Build time required |
| ✅ Free GitHub hosting | ❌ Docker Hub limits |

### **File Structure for Git Deployment:**

```
your-repo/
├── runpod-kiss-api/
│   ├── handler.serverless.py      # Main handler
│   ├── requirements.serverless.txt # Dependencies  
│   ├── runpod_serverless.py       # RunPod integration (if needed)
│   └── README.md                  # Documentation
```

---

## 🚀 Quick Git Setup Guide

### **If You Don't Have a Git Repo Yet:**

```bash
# Initialize repository
git init
git add .
git commit -m "Initial AI kiss video generator"

# Create GitHub repo and push
# Go to github.com → New Repository → "ai-kiss-generator"
git remote add origin https://github.com/YOUR_USERNAME/ai-kiss-generator.git
git branch -M main  
git push -u origin main
```

### **Repository Structure:**
```
ai-kiss-generator/
├── runpod-kiss-api/
│   ├── handler.serverless.py
│   ├── requirements.serverless.txt
│   ├── Dockerfile.serverless
│   └── deployment-guides/
└── README.md
```

---

## 🧪 Testing Your Deployment

### **Step 1: Health Check**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"health_check": true}}'
```

### **Expected Response:**
```json
{
  "status": "healthy",
  "models_ready": true,
  "network_volume": {
    "volume_mounted": true,
    "wan_model_exists": true,
    "total_models": 2
  },
  "deployment_mode": "serverless_network_volume"
}
```

### **Step 2: Test AI Generation**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "source_image": "BASE64_ENCODED_FACE_IMAGE_1",
      "target_image": "BASE64_ENCODED_FACE_IMAGE_2"
    }
  }'
```

---

## 🔧 Troubleshooting

### **Common Issues:**

#### **1. Repository Not Found**
- ✅ Ensure repo is public or RunPod has access
- ✅ Check repository path is correct
- ✅ Verify branch name (main vs master)

#### **2. Dependencies Installation Failed**
- ✅ Check requirements.serverless.txt exists
- ✅ Verify base image has pip installed
- ✅ Add container start command: `pip install -r requirements.serverless.txt && python3 handler.serverless.py`

#### **3. Network Volume Not Mounted**
- ✅ Verify volume name: `ai-models-kiss-video`  
- ✅ Check mount path: `/runpod-volume`
- ✅ Ensure volume exists and has models

#### **4. Handler Import Errors**
- ✅ Check file name: `handler.serverless.py`
- ✅ Verify Python syntax
- ✅ Ensure all imports are available

---

## 💡 Pro Tips

### **For Git Deployment:**
- ✅ Use clear commit messages
- ✅ Tag releases: `git tag v1.0.0 && git push --tags`
- ✅ Use `.gitignore` to exclude large files
- ✅ Keep requirements minimal for faster installs

### **For Updates:**
```bash
# Make changes
git add .
git commit -m "Update AI model parameters"
git push origin main

# RunPod will auto-deploy the update!
```

### **Environment Variables Management:**
- ✅ Set `MODEL_CACHE_DIR` to match your volume mount
- ✅ Use `PYTHONUNBUFFERED=1` for better logging
- ✅ Set appropriate timeout values for video generation

---

## 🎉 Final Deployment Checklist

- [ ] Files pushed to GitHub repository
- [ ] RunPod serverless endpoint created
- [ ] Git repository configured in endpoint
- [ ] Base image set: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04`
- [ ] Network volume mounted: `ai-models-kiss-video` → `/runpod-volume`
- [ ] Environment variables configured
- [ ] Health check returns "healthy"
- [ ] Test video generation works
- [ ] Ready to generate AI kiss videos! 🎬✨

---

## 🚀 Next: Generate Your First AI Kiss Video!

Once deployed, your serverless endpoint will:
- ✅ Load Wan-AI models from your network volume
- ✅ Generate high-quality AI kiss videos  
- ✅ Return results in 30-60 seconds
- ✅ Scale automatically based on demand
- ✅ Only charge for actual generation time

**The 4-day build struggle is finally over!** 🎉