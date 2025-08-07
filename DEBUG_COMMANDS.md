# 🔍 Debug Your RunPod Volume - Find Your Models

## Issue Identified:
```json
"errors": ["Models directory not found: /runpod-volume/models"]
```

Your network volume is mounted but models aren't where the handler expects them.

---

## 🚀 Run These Debug Commands

### **Step 1: Find Your Models**
Run this command to explore your volume structure:

```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"debug": "check_volume"}}'
```

**This will show you:**
- ✅ What's actually in `/runpod-volume/`
- ✅ Where your AI models are stored
- ✅ Recommended `MODEL_CACHE_DIR` path

### **Step 2: Check GPU Compatibility**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"debug": "check_gpu"}}'
```

**This will confirm:**
- ⚠️ RTX 5090 compatibility issue details
- 🎯 GPU switching recommendations

---

## 🔧 Expected Debug Results

### **Volume Debug Response:**
```json
{
  "status": "debug_complete",
  "volume_info": {
    "volume_mounted": true,
    "volume_contents": {
      "Models/": ["Wan2.1-I2V-14B-720P", "other-model"],
      "cache/": ["huggingface", "torch"],
      "data/": ["some-file"]
    },
    "model_search_results": {
      "/runpod-volume": ["Models/ (15 files)"],
      "/runpod-volume/Models": ["Wan2.1-I2V-14B-720P/ (19 files)"]
    },
    "recommendations": [
      "Found models in /runpod-volume/Models: ['Wan2.1-I2V-14B-720P']",
      "🎯 Recommended MODEL_CACHE_DIR: /runpod-volume/Models"
    ]
  }
}
```

### **GPU Debug Response:**
```json
{
  "status": "gpu_debug_complete", 
  "gpu_info": {
    "gpu_name": "NVIDIA GeForce RTX 5090",
    "compatibility_issue": true,
    "issue_description": "RTX 5090 uses sm_120 but PyTorch 2.1.0 only supports up to sm_90",
    "recommendations": [
      "Switch to RTX 4090 GPU (fully compatible)",
      "Use A100 40GB GPU (enterprise grade)",
      "Update base image to: runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04"
    ]
  }
}
```

---

## 🎯 Most Likely Scenarios

### **Scenario A: Models in Different Directory**
If debug shows models in `/runpod-volume/Models/` (capital M):
1. Update environment variable: `MODEL_CACHE_DIR=/runpod-volume/Models`
2. Save endpoint configuration
3. Test again

### **Scenario B: Models in Root Volume**
If models are directly in `/runpod-volume/Wan2.1-I2V-14B-720P/`:
1. Update environment variable: `MODEL_CACHE_DIR=/runpod-volume`
2. Save endpoint configuration  
3. Test again

### **Scenario C: Models in HuggingFace Cache**
If models are in `/runpod-volume/huggingface/` or `/runpod-volume/cache/`:
1. Update environment variable: `MODEL_CACHE_DIR=/runpod-volume/huggingface`
2. Or: `MODEL_CACHE_DIR=/runpod-volume/cache`
3. Test again

---

## ⚡ Quick Fix Steps

1. **Run volume debug command** (above)
2. **Find where models actually are** from the response
3. **Update MODEL_CACHE_DIR** in your RunPod endpoint settings:
   ```
   Environment Variables → MODEL_CACHE_DIR → /runpod-volume/ACTUAL_PATH
   ```
4. **Save configuration**
5. **Test health check:**
   ```bash
   curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -d '{"input": {"health_check": true}}'
   ```

---

## 🎉 Success Indicators

After fixing the path, health check should show:
```json
{
  "status": "healthy",
  "models_ready": true,
  "network_volume": {
    "wan_model_exists": true,
    "total_models": 2
  }
}
```

**Then you can generate AI kiss videos!** 🎬✨

---

## 💡 Pro Tip

The most common issue is models being in:
- `/runpod-volume/Models/` (capital M) instead of `/runpod-volume/models/`
- Or directly in `/runpod-volume/` without a subdirectory

The debug command will show you exactly where they are! 🔍