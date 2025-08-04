# 🚀 Professional Volume-Based Deployment Guide

## 🌍 **Real-World Solution**
This guide implements the **professional model management strategy** used by:
- **ComfyUI Cloud** - Pre-loaded persistent storage
- **Automatic1111 services** - Shared model volumes
- **Stability AI** - Model server architecture
- **Production AI video services** - Cost-effective scaling

---

## 📋 **Step-by-Step Deployment**

### **Step 1: Create RunPod Network Volume**

1. **Login to RunPod Console**
   - Go to [RunPod.io](https://runpod.io) → Console

2. **Create Network Volume**
   - Navigate to **Storage** → **Network Volumes**
   - Click **"Create Network Volume"**
   - **Name**: `ai-models-shared`
   - **Size**: `100 GB` (minimum for Wan-AI + LoRA + cache)
   - **Region**: Choose closest to your users
   - Click **"Create"**

3. **Note Volume ID**
   - Save the Volume ID (e.g., `vol_abc123def456`)
   - You'll need this for deployment

---

### **Step 2: Pre-load Models (One-time Setup)**

1. **Rent RunPod Instance for Setup**
   ```
   Go to RunPod → Rent → Secure Cloud
   - GPU: Any (A4000 is cheapest for setup)
   - Template: RunPod PyTorch 2.1
   - Network Volume: Attach "ai-models-shared" to /workspace
   - Start instance
   ```

2. **SSH into Instance and Run Setup**
   ```bash
   # SSH into your RunPod instance
   ssh root@your-instance-ip
   
   # Download setup script
   curl -O https://raw.githubusercontent.com/your-repo/setup_volume.sh
   chmod +x setup_volume.sh
   
   # Run setup (downloads models to volume)
   ./setup_volume.sh
   ```

3. **Wait for Completion**
   - Wan-AI model: ~15-30 minutes (28GB)
   - LoRA model: ~2-5 minutes (400MB)
   - **Total setup time: ~30-45 minutes**

4. **Verify Setup**
   ```bash
   # Check models are downloaded
   ls -la /workspace/models/
   du -sh /workspace/models/*
   
   # Should show:
   # ~28GB  Wan2.1-I2V-14B-720P/
   # ~400MB kissing-lora/
   ```

5. **Stop Setup Instance**
   - Models are now permanently on the volume
   - Stop the instance to save costs

---

### **Step 3: Build Docker Image**

1. **Build Volume-Ready Image**
   ```bash
   # On your local machine
   cd runpod-kiss-api
   chmod +x build_volume.sh
   ./build_volume.sh
   ```

2. **Push to Docker Hub**
   ```bash
   docker push nandtjm/kiss-video-generator:volume-ready
   ```

---

### **Step 4: Create RunPod Serverless Endpoint**

1. **Go to RunPod Serverless**
   - Navigate to **Serverless** → **Functions**
   - Click **"New Endpoint"**

2. **Configure Endpoint**
   ```
   Endpoint Configuration:
   ┌─────────────────────────────────────┐
   │ Name: kiss-video-generator          │
   │ Image: nandtjm/kiss-video-generator:volume-ready │
   │ Docker Registry: Docker Hub         │
   └─────────────────────────────────────┘
   
   Hardware:
   ┌─────────────────────────────────────┐
   │ GPU: NVIDIA RTX 4090 (recommended) │
   │ vCPUs: 8                           │
   │ Memory: 32 GB                      │
   │ Container Disk: 50 GB              │
   └─────────────────────────────────────┘
   
   Network Volume:
   ┌─────────────────────────────────────┐
   │ Volume: ai-models-shared           │
   │ Mount Path: /workspace             │
   └─────────────────────────────────────┘
   
   Environment Variables:
   ┌─────────────────────────────────────┐
   │ MODEL_CACHE_DIR=/workspace/models   │
   │ TEMP_DIR=/tmp                      │
   │ HUGGINGFACE_HUB_CACHE=/workspace/models/.cache │
   └─────────────────────────────────────┘
   
   Advanced Settings:
   ┌─────────────────────────────────────┐
   │ Max Workers: 10                    │
   │ Idle Timeout: 5 minutes           │
   │ Request Timeout: 10 minutes       │
   └─────────────────────────────────────┘
   ```

3. **Deploy Endpoint**
   - Click **"Create Endpoint"**
   - Wait for deployment (~2-3 minutes)
   - Note your endpoint ID and URL

---

### **Step 5: Test Deployment**

1. **Test Endpoint Health**
   ```bash
   curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/health" \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

2. **Test Video Generation**
   ```bash
   curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "input": {
         "source_image": "data:image/jpeg;base64,/9j/4AAQ...",
         "target_image": "data:image/jpeg;base64,/9j/4AAQ...",
         "model": "wan_ai"
       }
     }'
   ```

3. **Expected Response**
   ```json
   {
     "status": "success",
     "video": "base64_encoded_video_data",
     "model_used": "wan_ai",
     "resolution": [1280, 720],
     "message": "Video generated using pre-loaded volume models"
   }
   ```

---

## 🎯 **Performance Benefits**

### **Startup Time Comparison**
| Strategy | First Request | Subsequent Requests |
|----------|---------------|-------------------|
| **Runtime Download** | 10-15 minutes ❌ | 2-3 minutes |
| **API Services** | 30 seconds | 30 seconds |
| **Volume Strategy** | **30 seconds ✅** | **30 seconds ✅** |

### **Cost Comparison (1000 videos/month)**
| Strategy | Setup Cost | Monthly Cost | Total |
|----------|------------|--------------|--------|
| **API Services** | $0 | $200-500 | $200-500 |
| **Volume Strategy** | $5 (one-time) | $20-50 | $25-55 |
| **Savings** | | | **$175-445/month** |

---

## 🔧 **Advanced Configuration**

### **Custom Model Paths**
```python
# In your main_volume.py
MODEL_CACHE_DIR = "/workspace/models"

# Custom model paths
CUSTOM_MODELS = {
    "wan_ai": "/workspace/models/Wan2.1-I2V-14B-720P",
    "custom_lora": "/workspace/models/your-custom-lora",
    "fine_tuned": "/workspace/models/your-fine-tuned-model"
}
```

### **Multiple Models Support**
```bash
# Add more models to your volume
huggingface-cli download stable-video-diffusion/stable-video-diffusion-img2vid-xt \
  --local-dir /workspace/models/stable-video-diffusion

huggingface-cli download your-username/custom-model \
  --local-dir /workspace/models/custom-model
```

### **Model Versioning**
```bash
# Organize by version
/workspace/models/
├── wan-ai/
│   ├── v2.1/          # Current production
│   └── v2.2/          # Testing
├── loras/
│   ├── kissing-v1/
│   └── kissing-v2/
└── .cache/
```

---

## 🚨 **Troubleshooting**

### **Volume Not Mounted**
```bash
# Check if volume is mounted
ls -la /workspace/
# Should show models/ directory

# If not mounted, check RunPod endpoint configuration
# Ensure Network Volume is attached to /workspace
```

### **Models Not Found**
```bash
# Check models exist on volume
ls -la /workspace/models/
du -sh /workspace/models/*

# If empty, re-run setup_volume.sh on RunPod instance
```

### **Permission Issues**
```bash
# Fix permissions on volume
chmod -R 755 /workspace/models/
chown -R root:root /workspace/models/
```

### **Out of Space**
```bash
# Check volume usage
df -h /workspace/

# Clean up cache if needed
rm -rf /workspace/models/.cache/
```

---

## 📊 **Monitoring & Scaling**

### **Health Monitoring**
```python
# Built-in health check validates volume models
GET /health
# Returns model validation status
```

### **Auto-Scaling Configuration**
```json
{
  "min_workers": 0,
  "max_workers": 10,
  "idle_timeout": 300,
  "scale_up_threshold": 5,
  "scale_down_threshold": 1
}
```

### **Cost Optimization**
- **Idle Timeout**: 5 minutes (balance cost vs warmup)
- **Max Workers**: Based on expected concurrent load
- **GPU Type**: RTX 4090 for best performance/cost ratio

---

## 🎉 **Success Metrics**

After deployment, you should see:

✅ **Container startup**: 30 seconds (no model downloads)  
✅ **First video generation**: 30-60 seconds  
✅ **Cost per video**: $0.01-0.05 (vs $0.20+ APIs)  
✅ **Success rate**: 99%+ (no download failures)  
✅ **Scalability**: 10+ concurrent requests  

---

## 🚀 **Next Steps**

1. **Production Optimizations**
   - Add model caching layers
   - Implement request queuing
   - Add monitoring and logging

2. **Model Management**
   - Version control for models  
   - A/B testing framework
   - Custom fine-tuning pipeline

3. **Integration**
   - Frontend integration with your app
   - Webhook notifications for completion
   - User management and billing

This professional volume-based approach gives you the scalability and cost-effectiveness of real AI video services! 🎬✨