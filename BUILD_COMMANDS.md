# 🚀 Docker Build & Push Commands for nandtjm

## **Step 1: Navigate to Project Directory**
```bash
cd "/Users/nandlal/Local Sites/projects/ai-kiss-video-app/ai-kiss-generator/runpod-kiss-api"
```

## **Step 2: Login to Docker Hub**
```bash
docker login
# Enter username: nandtjm
# Enter password: [your-docker-hub-password]
```

## **Step 3: Build Production Image (Automated)**
```bash
# Make build script executable
chmod +x build_production.sh

# Run automated build (will take 20-30 minutes)
./build_production.sh
```

**OR Manual Build:**

## **Step 3 Alternative: Manual Build Commands**
```bash
# Set environment variable
export DOCKER_REGISTRY="nandtjm"

# Build the image (takes 20-30 minutes due to model downloads)
docker build \
  -f Dockerfile.production \
  -t nandtjm/kiss-video-generator:production-preloaded \
  --progress=plain \
  .

# Verify models are in the image
docker run --rm nandtjm/kiss-video-generator:production-preloaded \
  python3 -c "
import os
wan_path = '/app/models/Wan2.1-I2V-14B-720P'
lora_path = '/app/models/kissing-lora'
print('✅ Wan-AI model found:', os.path.exists(wan_path) and len(os.listdir(wan_path)) > 0)
print('✅ LoRA model found:', os.path.exists(lora_path) and len(os.listdir(lora_path)) > 0)
"

# Push to Docker Hub
docker push nandtjm/kiss-video-generator:production-preloaded
```

## **Step 4: Verify Push Success**
```bash
# Check image on Docker Hub
echo "🔗 Your image is now available at:"
echo "   https://hub.docker.com/r/nandtjm/kiss-video-generator"
echo "   Image: nandtjm/kiss-video-generator:production-preloaded"
```

## **Expected Output:**
- ✅ Build time: 20-30 minutes (downloading 28GB+ models)
- ✅ Final image size: ~8-10GB compressed, ~30GB uncompressed  
- ✅ Models verified: Wan-AI + Remade-AI LoRA included
- ✅ Ready for RunPod deployment

## **Next: RunPod Deployment**
Use this image in RunPod:
```
Image: nandtjm/kiss-video-generator:production-preloaded
GPU: RTX 4090
Memory: 32GB
Disk: 50GB
```

## **Troubleshooting:**
- If build fails, check Docker is running: `docker info`
- If Hugging Face download fails, try: `huggingface-cli login`
- If push fails, verify login: `docker login`
- Large image size is normal for AI models (~30GB total)