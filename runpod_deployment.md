# RunPod Serverless Deployment Strategy

## 🎯 **Strategy Overview**

Instead of baking 28GB models into Docker images, we use **RunPod Network Storage**:

1. **Small Docker Image** (~2-3GB) with code only
2. **Models stored on RunPod Network Storage** (persistent, shared across containers)
3. **One-time model download** on first request
4. **All subsequent containers reuse the same models**

## 🚀 **Deployment Steps**

### Step 1: Build & Push Image
```bash
# Build RunPod-optimized image
chmod +x build_runpod.sh
./build_runpod.sh

# Push to Docker Hub
docker push nandtjm/kiss-video-generator:runpod-serverless
```

### Step 2: Create RunPod Serverless Endpoint

1. **Go to RunPod Dashboard** → Serverless
2. **Create New Endpoint** with these settings:

**Container Configuration:**
- **Docker Image**: `nandtjm/kiss-video-generator:runpod-serverless`
- **Container Registry Credentials**: Docker Hub (if private)

**Hardware:**
- **GPU**: RTX 4090 or A100 (recommended)
- **vCPU**: 8+ cores
- **RAM**: 32GB+
- **Container Disk**: 50GB+ 
- **Network Storage**: **Enable 100GB+** (this is key!)

**Environment Variables:**
```
RUNPOD_VOLUME_PATH=/runpod-volume
MODEL_CACHE_DIR=/runpod-volume/models
HUGGINGFACE_HUB_CACHE=/runpod-volume/models/.cache
```

**Advanced Settings:**
- **Max Workers**: 5-10 (based on expected load)
- **Idle Timeout**: 5 minutes
- **Request Timeout**: 10 minutes (for model downloads)

### Step 3: Test Deployment

```bash
# Test endpoint
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image_url": "https://example.com/source_image.jpg",
      "model_type": "wan-ai-base"
    }
  }'
```

## 💡 **How Network Storage Works**

### First Request (Model Download):
```
Container 1 starts → Checks /runpod-volume/models/
                  → Models not found
                  → Downloads Wan-AI model (~5-10 minutes)
                  → Saves to /runpod-volume/models/
                  → Processes request
                  → Container shuts down
```

### Subsequent Requests (Fast):
```
Container 2 starts → Checks /runpod-volume/models/
                  → Models found! ✅
                  → Loads models (~30 seconds)
                  → Processes request immediately
                  → Container shuts down
```

## 📊 **Performance Benefits**

| Metric | Traditional Approach | RunPod Network Storage |
|--------|---------------------|----------------------|
| **Docker Image Size** | 30GB+ | 2-3GB |
| **First Request** | 2-3 minutes (model loading) | 5-10 minutes (download once) |
| **Subsequent Requests** | 2-3 minutes | 30 seconds |
| **Storage Costs** | High (per container) | Low (shared) |
| **Cold Start** | Slow (large image pull) | Fast (small image) |

## 🔧 **Configuration Files**

### `.runpod-endpoint.json` (optional)
```json
{
  "name": "kiss-video-generator",
  "image": "nandtjm/kiss-video-generator:runpod-serverless",
  "gpu_type": "RTX4090",
  "network_storage": {
    "size": "100GB",
    "mount_path": "/runpod-volume"
  },
  "environment": {
    "MODEL_CACHE_DIR": "/runpod-volume/models",
    "RUNPOD_VOLUME_PATH": "/runpod-volume"
  },
  "scaling": {
    "max_workers": 10,
    "idle_timeout": 300
  }
}
```

## 🚨 **Important Notes**

### Network Storage Requirements:
- **Minimum 50GB** for Wan-AI model alone
- **Recommended 100GB+** for multiple models + cache
- **Persistent across all containers** (key advantage)

### First-Time Setup:
- **First request takes 5-10 minutes** (model download)
- **Show users appropriate loading messages**
- **Consider pre-warming with a test request**

### Cost Optimization:
- **Models downloaded once** (not per container)
- **No repeated 28GB transfers**
- **Pay only for compute time + small storage fee**

## 🧪 **Testing Commands**

```bash
# Test local build
docker run --rm -p 8000:8000 \
  -e MODEL_CACHE_DIR=/tmp/models \
  nandtjm/kiss-video-generator:runpod-serverless

# Check model download status
curl http://localhost:8000/health

# Test video generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"image_url": "test.jpg", "model_type": "wan-ai-base"}'
```

This strategy eliminates the 28GB Docker image download issue while providing optimal performance and cost efficiency!