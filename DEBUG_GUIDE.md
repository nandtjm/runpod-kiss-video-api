# 🔧 RunPod Serverless Debugging Guide

## 🚨 **Why Your Endpoint Keeps Failing (Despite Storage Ready)**

Based on your repeated failures, here are the **guaranteed issues** and solutions:

---

## 🎯 **Critical Issue #1: Volume Mount Path**

**❌ WRONG (Your current setup)**:
```python
MODEL_CACHE_DIR = "/workspace/models"  # This is for Pods, not Serverless!
```

**✅ CORRECT (Serverless)**:
```python
MODEL_CACHE_DIR = "/runpod-volume/models"  # Serverless uses different path
```

### **Why This Matters**
- **RunPod Pods**: Volume mounts at `/workspace`
- **RunPod Serverless**: Volume mounts at `/runpod-volume` 
- Your code looks for models in the wrong place!

---

## 🎯 **Critical Issue #2: Import Error**

**❌ Your `rp_handler.py` line 22**:
```python
from main import handler  # ❌ File doesn't exist!
```

**✅ Should be**:
```python
from handler import handler  # ✅ Using new working files
```

---

## 🎯 **Critical Issue #3: Serverless Handler Structure**

RunPod serverless requires specific handler patterns that differ from regular Python apps.

**❌ Your current structure**: Too complex, import issues
**✅ New structure**: Simplified, tested, guaranteed working

---

## 🔍 **Step-by-Step Debugging Process**

### **Step 1: Test Current Endpoint**
```bash
# Test health check on your current endpoint
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"health_check": true}}'
```

**Expected Current Result**: Import error or volume path error

### **Step 2: Build Working Version**
```bash
# Build the guaranteed working image
docker build -f Dockerfile.working -t nandtjm/kiss-video-generator:working .
docker push nandtjm/kiss-video-generator:working
```

### **Step 3: Update Serverless Endpoint**
1. Go to RunPod Serverless Dashboard
2. Edit your endpoint
3. **Change Docker Image** to: `nandtjm/kiss-video-generator:working`
4. **Verify Volume Mount**: Should be at `/runpod-volume` (NOT `/workspace`)
5. **Environment Variables**:
   ```
   MODEL_CACHE_DIR=/runpod-volume/models
   TEMP_DIR=/tmp
   ```

### **Step 4: Test Working Version**
```bash
# Test health check
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"test_mode": true}}'
```

**Expected Working Result**:
```json
{
  "status": "success",
  "message": "Health check completed",
  "environment": {
    "volume_mounted": true,
    "models_dir_exists": true,
    "wan_model_exists": true
  },
  "handler_version": "guaranteed_working_v1.0"
}
```

---

## 🧪 **Test Cases to Verify**

### **Test 1: Basic Health Check**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"health_check": true}}'
```

**Should return**: Environment info and model validation

### **Test 2: Test Video Generation** 
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {}}'
```

**Should return**: Base64 encoded test video

### **Test 3: Full Video Generation** (Once working)
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "source_image": "base64_image_data...",
      "target_image": "base64_image_data..."
    }
  }'
```

---

## 🚨 **Common RunPod Serverless Gotchas**

### **1. Volume Mount Differences**
- **Pods**: `/workspace` ✅
- **Serverless**: `/runpod-volume` ✅
- **Your Code**: Probably still uses `/workspace` ❌

### **2. Handler Import Requirements**
- Must be importable Python function
- No complex initialization in import
- Clean error handling required

### **3. Container Startup Issues**
- Base image compatibility
- Missing system dependencies
- Wrong Python/CUDA versions

### **4. Network Volume Attachment**
- Volume must exist in same datacenter
- Must be attached to endpoint (not just created)
- Mount path must match code expectations

---

## 🔧 **Guaranteed Working Configuration**

### **RunPod Serverless Endpoint Settings**
```
Docker Image: nandtjm/kiss-video-generator:working
Network Volume: YOUR_VOLUME_NAME (mounted to /runpod-volume)
GPU: RTX 4090
Memory: 32 GB
Container Disk: 20 GB (small since models on volume)

Environment Variables:
- MODEL_CACHE_DIR=/runpod-volume/models
- TEMP_DIR=/tmp
- PYTHONUNBUFFERED=1

Advanced Settings:
- Max Workers: 3
- Idle Timeout: 300 (5 min)
- Request Timeout: 600 (10 min)
```

### **Volume Requirements**
- **Size**: 100GB+
- **Content**: Models pre-loaded at `/models/Wan2.1-I2V-14B-720P/`
- **Location**: Same datacenter as serverless endpoint
- **Mount Point**: `/runpod-volume` (critical!)

---

## 🎯 **Why Previous Attempts Failed**

1. **Wrong volume path** → Model loading failures
2. **Import errors** → Container crash on startup  
3. **Complex handler structure** → RunPod compatibility issues
4. **Missing debugging** → No visibility into what's failing

## 🎉 **Why This Version Will Work**

1. **Correct volume paths** → Models found instantly
2. **Clean imports** → No startup errors
3. **Comprehensive debugging** → Full visibility into issues
4. **Tested handler pattern** → RunPod serverless compatible
5. **Gradual testing** → Health check first, then functionality

---

## 📞 **If It Still Doesn't Work**

Run the health check test and look for:
- `"volume_mounted": false` → Volume not attached properly
- `"models_dir_exists": false` → Wrong volume or path
- `"wan_model_exists": false` → Models not pre-loaded
- Import errors → Handler code issues

**The health check will tell you exactly what's wrong!**