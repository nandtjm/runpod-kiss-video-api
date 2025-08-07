# 🚀 Complete Environment Variables - RunPod Serverless

## 📋 Required Environment Variables

Copy these **exact** environment variables to your RunPod serverless endpoint:

### **Basic Configuration**
```yaml
MODEL_CACHE_DIR: /runpod-volume/models
PYTHONPATH: /workspace
PYTHONUNBUFFERED: 1
```

### **GPU & CUDA Optimization**
```yaml
CUDA_LAUNCH_BLOCKING: 0
TORCH_BACKENDS_CUDNN_BENCHMARK: 1
CUDA_VISIBLE_DEVICES: 0
```

### **AI Model Configuration**
```yaml
HF_HOME: /runpod-volume/models/.cache
TRANSFORMERS_CACHE: /runpod-volume/models/.cache/transformers
DIFFUSERS_CACHE: /runpod-volume/models/.cache/diffusers
TORCH_HOME: /runpod-volume/models/.cache/torch
```

### **Memory & Performance**
```yaml
PYTORCH_CUDA_ALLOC_CONF: max_split_size_mb:512
OMP_NUM_THREADS: 8
MKL_NUM_THREADS: 8
```

### **Temporary Directories**
```yaml
TEMP_DIR: /tmp
TMPDIR: /tmp
TMP: /tmp
```

---

## 🔧 Alternative Model Paths (Based on Debug Results)

### **If models are in `/runpod-volume/Models/` (capital M):**
```yaml
MODEL_CACHE_DIR: /runpod-volume/Models
HF_HOME: /runpod-volume/Models/.cache
TRANSFORMERS_CACHE: /runpod-volume/Models/.cache/transformers
DIFFUSERS_CACHE: /runpod-volume/Models/.cache/diffusers
```

### **If models are directly in `/runpod-volume/`:**
```yaml
MODEL_CACHE_DIR: /runpod-volume
HF_HOME: /runpod-volume/.cache
TRANSFORMERS_CACHE: /runpod-volume/.cache/transformers
DIFFUSERS_CACHE: /runpod-volume/.cache/diffusers
```

### **If models are in `/runpod-volume/huggingface/`:**
```yaml
MODEL_CACHE_DIR: /runpod-volume/huggingface
HF_HOME: /runpod-volume/huggingface
TRANSFORMERS_CACHE: /runpod-volume/huggingface/transformers
DIFFUSERS_CACHE: /runpod-volume/huggingface/diffusers
```

---

## 🎯 Complete RunPod Serverless Configuration

### **Container Configuration**
```yaml
Container Image: runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
Container Start Command: python3 app.py
Container Registry Credentials: (None)
```

### **Network Volume**
```yaml
Network Volume: ai-models-kiss-video
Container Mount Path: /runpod-volume
```

### **GPU Settings**
```yaml
GPU Types: RTX 4090 (recommended for compatibility)
          # OR RTX 5090 (if using newer PyTorch base image)
GPU Count: 1
Min vRAM: 16 GB
Max vRAM: 48 GB
```

### **Scaling Settings**
```yaml
Max Workers: 3
Idle Timeout: 5 seconds
Max Job Timeout: 300 seconds (5 minutes)
Request Queue Limit: 50
```

### **Advanced Settings**
```yaml
Max Response Size: 100 MB
Container Disk Size: 20 GB
Container Start Timeout: 120 seconds
```

---

## 📋 Environment Variables - Copy/Paste Format

```
MODEL_CACHE_DIR=/runpod-volume/models
PYTHONPATH=/workspace
PYTHONUNBUFFERED=1
CUDA_LAUNCH_BLOCKING=0
TORCH_BACKENDS_CUDNN_BENCHMARK=1
CUDA_VISIBLE_DEVICES=0
HF_HOME=/runpod-volume/models/.cache
TRANSFORMERS_CACHE=/runpod-volume/models/.cache/transformers
DIFFUSERS_CACHE=/runpod-volume/models/.cache/diffusers
TORCH_HOME=/runpod-volume/models/.cache/torch
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
OMP_NUM_THREADS=8
MKL_NUM_THREADS=8
TEMP_DIR=/tmp
TMPDIR=/tmp
TMP=/tmp
```

---

## 🔍 Debug-Based Path Updates

After running the debug command:
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"input": {"debug": "check_volume"}}'
```

**Update these variables based on where your models are actually found:**

### **Example: If debug shows models in `/runpod-volume/Models/Wan2.1-I2V-14B-720P/`**
```yaml
MODEL_CACHE_DIR: /runpod-volume/Models
```

### **Example: If debug shows models in `/runpod-volume/cache/models/`**
```yaml
MODEL_CACHE_DIR: /runpod-volume/cache/models
```

---

## 🧪 Test Configuration

### **Health Check Test:**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"health_check": true}}'
```

### **Expected Healthy Response:**
```json
{
  "status": "healthy",
  "models_ready": true,
  "environment": {
    "torch_version": "2.1.0+cu118",
    "cuda_available": true,
    "gpu_name": "NVIDIA GeForce RTX 4090",
    "deployment_mode": "serverless_network_volume"
  },
  "network_volume": {
    "volume_mounted": true,
    "wan_model_exists": true,
    "total_models": 2
  }
}
```

---

## ⚠️ RTX 5090 Compatibility

If using RTX 5090, also consider updating to newer base image:

### **RTX 5090 Compatible Configuration:**
```yaml
Container Image: runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04
```

**Additional environment variables for RTX 5090:**
```yaml
TORCH_CUDA_ARCH_LIST: 9.0
CUDA_ARCH: sm_90
```

---

## 🎬 Ready for AI Video Generation!

Once environment variables are set and health check passes:

### **Generate AI Kiss Video:**
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

### **Expected Success Response:**
```json
{
  "status": "success",
  "message": "AI kiss video generated using network volume models",
  "video": "BASE64_ENCODED_MP4_VIDEO",
  "processing_time": "45.2s",
  "model_used": "Wan2.1-I2V-14B-720P",
  "model_source": "network_volume"
}
```

---

## 🎉 Success Checklist

- [ ] Environment variables configured
- [ ] Network volume mounted at `/runpod-volume`
- [ ] `MODEL_CACHE_DIR` pointing to actual model location
- [ ] GPU compatibility addressed (RTX 4090 or newer PyTorch)
- [ ] Health check returns "healthy"
- [ ] AI video generation working

**Your 4-day struggle ends here!** 🚀✨