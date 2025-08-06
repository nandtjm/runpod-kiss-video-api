# AI Kiss Video Generator - Serverless Deployment

## 🚀 RunPod Serverless Configuration

### Repository Settings:
```
Repository: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
Branch: main
Path: runpod-kiss-api/
```

### Docker Configuration:
```
Base Image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04
Start Command: pip install -r requirements.serverless.txt && python3 handler.serverless.py
```

### Environment Variables:
```
MODEL_CACHE_DIR=/runpod-volume/models
PYTHONPATH=/app
PYTHONUNBUFFERED=1
CUDA_LAUNCH_BLOCKING=0
HF_HOME=/runpod-volume/models/.cache
```

### Network Volume:
```
Volume: ai-models-kiss-video
Mount Path: /runpod-volume
```

### GPU Settings:
```
GPU Types: RTX 4090, RTX 5090
Min Memory: 16GB
Max Workers: 3
Idle Timeout: 5s
Request Timeout: 300s
```

## 🧪 Test Commands

Health Check:
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"input": {"health_check": true}}'
```

Generate Video:
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"input": {"source_image": "BASE64_IMG1", "target_image": "BASE64_IMG2"}}'
```
