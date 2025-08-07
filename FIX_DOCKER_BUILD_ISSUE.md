# 🔧 Fix: RunPod Auto-Building Docker Instead of Using Source Code

## ❌ Current Issue:
```
loading container image from cache
registry.runpod.net/nandtjm-runpod-kiss-video-api-main-dockerfile:973ff8973
error creating container: nvidia-smi: parsing output of line 0: failed to parse (pcie.link.gen.max)
```

**Problem:** RunPod is auto-building a Docker image from your repository because it found Dockerfile files, instead of using direct source code deployment.

---

## 🚀 Quick Fix Options

### **Option 1: Remove Dockerfiles (Recommended)**

Remove Dockerfiles from your repository to force source code deployment:

```bash
# On your local machine or Pod
cd /path/to/runpod-kiss-api
git rm Dockerfile*
git commit -m "Remove Dockerfiles - use source code deployment only"
git push origin main
```

### **Option 2: Configure RunPod for Source Code Deployment**

Update your RunPod serverless endpoint configuration:

#### **Source Code Settings:**
```yaml
Repository Type: GitHub
Repository URL: https://github.com/nandtjm/runpod-kiss-video-api
Branch: main
Repository Path: runpod-kiss-api/
Build Method: Source Code (NOT Docker Build)
```

#### **Container Configuration:**
```yaml
Base Image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
Container Start Command: pip install -r requirements.serverless.txt && python3 app.py
Docker Command: (leave blank - use source code)
```

### **Option 3: Use .dockerignore**

Create `.dockerignore` to prevent Docker builds:

```bash
# Create .dockerignore file
echo "Dockerfile*" > .dockerignore
echo "*.dockerfile" >> .dockerignore
git add .dockerignore
git commit -m "Add dockerignore to prevent auto-builds"
git push origin main
```

---

## 🎯 Recommended Solution: Remove Dockerfiles

Since you want to use your network volume models (not embedded models), source code deployment is better:

### **Step 1: Clean Repository**
```bash
cd "/Users/nandlal/Local Sites/projects/ai-kiss-video-app/ai-kiss-generator/runpod-kiss-api"

# Remove all Dockerfile variants
git rm Dockerfile*
git rm *.dockerfile 2>/dev/null || true

# Commit changes  
git commit -m "🧹 Remove Dockerfiles - use source code deployment

- Forces RunPod to use source code instead of building Docker
- Avoids nvidia-smi parsing errors during container creation
- Uses network volume models directly (no embedded models)
- Faster deployment without Docker build process"

git push origin main
```

### **Step 2: Update RunPod Configuration**
```yaml
Deployment Type: Source Code
Repository: https://github.com/nandtjm/runpod-kiss-video-api
Path: runpod-kiss-api/
Base Image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
Start Command: pip install -r requirements.serverless.txt && python3 app.py
```

---

## 🔧 Alternative: Fix Docker Build Issues

If you want to keep Docker builds, fix the nvidia-smi issue:

### **Update Base Image**
Use a newer base image that handles RTX 5090 better:
```yaml
Base Image: runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
```

### **Or Switch GPU**
Change from RTX 5090 to RTX 4090 to avoid compatibility issues.

---

## 📋 Current Error Analysis

The error `nvidia-smi: parsing output... failed to parse (pcie.link.gen.max)` indicates:

1. **RTX 5090 Compatibility Issue** - nvidia-smi can't parse RTX 5090's PCIe info properly
2. **Docker Build Complexity** - Building Docker adds unnecessary complexity 
3. **Better Solution** - Use source code deployment with your network volume

---

## 🚀 Expected Result After Fix

With source code deployment:
```
✅ Repository cloned successfully
✅ Dependencies installed from requirements.serverless.txt  
✅ Handler started with python3 app.py
✅ Network volume models loaded
✅ GPU compatibility issues avoided
✅ Ready for AI video generation
```

---

## 💡 Why Source Code is Better

| Docker Build | Source Code |
|--------------|-------------|
| ❌ nvidia-smi parsing errors | ✅ No build-time GPU issues |
| ❌ Long build times | ✅ Fast deployment |
| ❌ Complex GPU compatibility | ✅ Runtime GPU detection |
| ❌ Embedded vs volume models | ✅ Uses network volume directly |

---

## 🎯 Quick Action Plan

1. **Remove Dockerfiles** from repository
2. **Configure source code deployment** in RunPod
3. **Switch to RTX 4090** for guaranteed compatibility  
4. **Test endpoint** - should work without Docker errors
5. **Run debug commands** to find models
6. **Generate AI videos** successfully!

**This eliminates the Docker build complexity and gets you straight to working AI generation!** 🎬✨