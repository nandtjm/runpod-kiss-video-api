# 📤 RunPod File Upload Methods - Complete Guide

Based on official RunPod documentation and community tools, here are all the methods to upload files to your RunPod Pod:

## 🎯 Upload Methods Comparison

| Method | Ease of Use | File Size Limit | Drag & Drop | Best For |
|--------|-------------|-----------------|-------------|----------|
| **Web Interface** | ⭐⭐⭐⭐⭐ | Small-Medium | ✅ Yes | Quick uploads |
| **RunPod File Uploader** | ⭐⭐⭐⭐⭐ | Large | ✅ Yes | Multi-file, resumable |
| **runpodctl** | ⭐⭐⭐⭐ | Small | ❌ No | CLI users |
| **SCP/rsync** | ⭐⭐⭐ | Large | ❌ No | Power users |

---

## 🖥️ Method 1: Built-in Web Interface (Simplest)

### **Step-by-Step Instructions:**

#### 1. Connect to Pod Web Terminal
```
RunPod Dashboard → Your Pod → "Connect" → "Start Web Terminal"
```

#### 2. Navigate to Upload Location
```bash
# Create workspace directory
mkdir -p /workspace/build
cd /workspace/build
```

#### 3. Upload via Web Interface
**Option A: Drag & Drop**
- Look for file manager icon in web terminal
- Drag your `pod-upload-complete.tar.gz` directly into the file area
- Files appear in current directory

**Option B: Upload Button**
- Click the "Upload" button (📤 icon) in web terminal toolbar  
- Select your `pod-upload-complete.tar.gz` file
- Wait for upload progress to complete

#### 4. Verify Upload
```bash
ls -la *.tar.gz
# Should show: pod-upload-complete.tar.gz (19K)
```

#### 5. Extract Files
```bash
tar -xzf pod-upload-complete.tar.gz
chmod +x *.sh
```

---

## 🔧 Method 2: RunPod File Uploader (Advanced Web UI)

### **Features:**
- ✅ **Multi-file uploads** - Upload multiple files simultaneously
- ✅ **Pause/Resume** - Interrupted uploads can be resumed
- ✅ **Large file support** - No size limits like basic web interface
- ✅ **Progress tracking** - Real-time upload progress
- ✅ **Drag & Drop** - Modern web interface

### **Installation on Pod:**
```bash
# Install the uploader (run on Pod, not locally!)
curl -sSL https://github.com/kodxana/RunPod-FilleUploader/raw/main/scripts/installer.sh -o installer.sh
chmod +x installer.sh
./installer.sh

# Start the uploader service
runpod-uploader
```

### **Access Web Interface:**
```
http://YOUR_POD_IP:2999
```
- Make sure port 2999 is exposed in Pod configuration
- Use the web interface to drag & drop files
- Supports resumable uploads if connection drops

### **Upload Your Files:**
1. Open the web interface at port 2999
2. Drag `pod-upload-complete.tar.gz` into the upload area
3. Monitor progress with pause/resume capabilities
4. Files are saved to `/workspace/uploads/` by default

---

## ⚡ Method 3: runpodctl (Built-in CLI)

### **Simple File Upload:**
```bash
# From your local machine
runpodctl send pod-upload-complete.tar.gz
```

### **Get One-Time Transfer Code:**
```bash
# On your local machine
runpodctl send pod-upload-complete.tar.gz
# Returns: Transfer code: ABC123

# On the Pod  
runpodctl receive ABC123
```

### **Benefits:**
- ✅ Pre-installed on all Pods
- ✅ Secure one-time codes
- ✅ No additional setup required
- ❌ Limited to smaller files
- ❌ No drag & drop interface

---

## 🔐 Method 4: SCP/SSH (Power Users)

### **Setup SSH Access:**
```bash
# On Pod - enable SSH
service ssh start

# Get Pod connection details from RunPod dashboard
# SSH Port, IP address, and key requirements
```

### **Upload via SCP:**
```bash
# From local machine
scp -P SSH_PORT -i ~/.ssh/your_key pod-upload-complete.tar.gz root@POD_IP:/workspace/build/
```

### **Upload via rsync (Advanced):**
```bash
# Supports resume, compression, progress
rsync -avz --progress -e "ssh -p SSH_PORT -i ~/.ssh/your_key" \
  pod-upload-complete.tar.gz root@POD_IP:/workspace/build/
```

---

## 📋 Recommended Workflow for AI Kiss Generator

### **For Your Specific Use Case:**

#### **Option 1: Quick Upload (Recommended)**
```bash
# 1. Create Pod with web terminal access
# 2. Connect → Web Terminal  
# 3. mkdir -p /workspace/build && cd /workspace/build
# 4. Drag & drop pod-upload-complete.tar.gz via web interface
# 5. tar -xzf pod-upload-complete.tar.gz && chmod +x *.sh
# 6. bash setup_pod.sh
```

#### **Option 2: Professional Setup (For Repeated Builds)**
```bash
# 1. Install RunPod File Uploader on Pod
curl -sSL https://github.com/kodxana/RunPod-FilleUploader/raw/main/scripts/installer.sh -o installer.sh && ./installer.sh

# 2. Start uploader service
runpod-uploader &

# 3. Access http://POD_IP:2999 in browser
# 4. Drag & drop all your build files
# 5. Navigate to upload location and extract
```

---

## 🎯 Working with Zip Archives in RunPod

### **Create Zip Archives on Pod:**
```bash
# Install zip utility
apt install zip -y

# Create zip archive
zip -r my-files.zip /path/to/files/

# Extract zip archive
unzip my-files.zip -d /destination/path/
```

### **Download Zip Archives from Pod:**
```bash
# Create archive for download
zip -r build-results.zip /workspace/build/

# Right-click in file manager → Download
# Or use runpodctl to send back to local machine
```

---

## 💡 Pro Tips for File Upload

### **Speed Optimization:**
- ✅ Use compressed archives (.tar.gz, .zip) to reduce upload time
- ✅ RunPod Pods have 10Gbps+ network - much faster than home internet
- ✅ Upload during off-peak hours for maximum speed
- ✅ Keep files under 1GB for web interface uploads

### **Reliability:**
- ✅ Use RunPod File Uploader for large files (resumable uploads)
- ✅ Verify file integrity after upload: `md5sum filename`
- ✅ Keep Pod terminal active during upload
- ✅ Use `screen` or `tmux` for long-running uploads

### **Cost Management:**
- ✅ Upload efficiently - time is money on Pods
- ✅ Compress files before upload
- ✅ Delete Pod after successful Docker push
- ✅ Use network volumes for persistent storage between Pods

---

## 🚀 Your AI Kiss Generator Upload Plan

### **Recommended Steps:**
1. **Create Pod:** RTX 4090/5090 with 50GB storage
2. **Connect:** Web Terminal access  
3. **Upload:** Drag & drop `pod-upload-complete.tar.gz` (19KB)
4. **Extract:** `tar -xzf pod-upload-complete.tar.gz`
5. **Build:** `bash setup_pod.sh && bash build_with_bazel.sh`
6. **Push:** Images automatically pushed to Docker Hub
7. **Cleanup:** Delete Pod, deploy to serverless endpoint

### **Expected Timeline:**
- 📤 **Upload:** 30 seconds (19KB archive)
- 🏗️ **Build:** 10 minutes (Bazel + superior bandwidth)
- 📤 **Push:** 2 minutes (to Docker Hub)
- 💰 **Total Cost:** ~$2 (vs hours of local frustration)

You're now equipped with multiple upload methods - choose the one that fits your workflow best! 🎯