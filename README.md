# RunPod Kiss Video Generator API

A serverless API for generating kiss videos using state-of-the-art AI models from Hugging Face, deployed on RunPod infrastructure.

## Features

- **Multiple AI Models**: Support for Wan-AI and Remade-AI kissing video generation models
- **Serverless Deployment**: Auto-scaling RunPod infrastructure
- **GPU Acceleration**: Optimized for NVIDIA RTX GPUs
- **RESTful API**: Easy integration with web applications
- **Base64 I/O**: Simple image input and video output handling

## Supported Models

- **Wan-AI/Wan2.1-I2V-14B-720P**: Base image-to-video model (720P resolution)
- **Remade-AI/kissing**: LoRA for kiss video generation (requires special "k144ing" trigger word)
  - Trained on Wan2.1 14B I2V 480p base model
  - 30 epochs training on 50 seconds of kissing video clips
  - Recommended settings: LoRA strength 1.0, guidance scale 6.0, flow shift 5.0

## Quick Start

### Prerequisites

- Docker installed
- RunPod account with API key
- Docker Hub account (or alternative registry)
- **RunPod instance with minimum 50GB disk space** (150GB recommended)
- GPU with 16+ GB VRAM (RTX 4090 recommended)

### 1. Clone and Setup

```bash
git clone https://github.com/nandtjm/runpod-kiss-video-api.git
cd runpod-kiss-api
```

### 2. Environment Setup

```bash
# Set your RunPod API key
export RUNPOD_API_KEY="your-runpod-api-key-here"

# Set your Docker registry (optional, defaults to Docker Hub)
export DOCKER_REGISTRY="your-dockerhub-username"
```

### 3. Pre-download Models

**Important**: Models must be pre-downloaded to RunPod volume storage before deployment.

```bash
# Download all required models (this may take 30+ minutes)
python download_models.py

# Verify models are downloaded correctly
python download_models.py verify
```

### 4. Deploy to RunPod

```bash
# Make deployment script executable
chmod +x deploy.py

# Deploy (builds image, pushes to registry, creates endpoint)
python deploy.py
```

### 4. Test the API

```python
import requests
import base64

# Load endpoint URL from deployment
with open('endpoint_info.json', 'r') as f:
    endpoint_info = json.load(f)

endpoint_url = endpoint_info['endpoint_url']

# Prepare request
payload = {
    "input": {
        "source_image": "base64_encoded_source_image",
        "target_image": "base64_encoded_target_image",
        "model": "wan_ai",
        "parameters": {
            "num_frames": 16,
            "guidance_scale": 7.5,
            "prompt": "Two people kissing romantically"
        }
    }
}

# Make request
response = requests.post(f"{endpoint_url}/run", json=payload)
result = response.json()

print(f"Status: {result['status']}")
```

## API Reference

### Endpoint: `POST /run`

Generate a kiss video from two input images.

#### Request Body

```json
{
  "input": {
    "source_image": "base64_encoded_image_data",
    "target_image": "base64_encoded_image_data", 
    "model": "wan_ai",
    "parameters": {
      "num_frames": 16,
      "fps": 24,
      "guidance_scale": 7.5,
      "num_inference_steps": 50,
      "prompt": "Two people kissing romantically",
      "seed": -1
    }
  }
}
```

#### Parameters

- `source_image` (required): Base64 encoded source image
- `target_image` (required): Base64 encoded target image  
- `model` (optional): Model to use (`wan_ai` or `remade_ai`, default: `wan_ai`)
- `parameters` (optional): Generation parameters

#### Generation Parameters

- `num_frames`: Number of video frames (8-32, default: 16)
- `fps`: Frames per second (12-30, default: 24)
- `guidance_scale`: Classifier-free guidance scale (1.0-15.0, default: 7.5)
- `num_inference_steps`: Denoising steps (20-100, default: 50)
- `prompt`: Text prompt for generation
- `seed`: Random seed (-1 for random, default: -1)

#### Response

```json
{
  "status": "success",
  "video_data": "base64_encoded_video_data",
  "model_used": "wan_ai",
  "message": "Kiss video generated successfully"
}
```

## Integration with Main App

### Backend Integration (FastAPI)

```python
import requests
import base64
from fastapi import HTTPException

class RunPodKissAPI:
    def __init__(self, endpoint_url: str, api_key: str):
        self.endpoint_url = endpoint_url
        self.api_key = api_key
    
    async def generate_kiss_video(self, source_image_path: str, target_image_path: str, 
                                model: str = "wan_ai", **params):
        # Convert images to base64
        with open(source_image_path, 'rb') as f:
            source_b64 = base64.b64encode(f.read()).decode()
        
        with open(target_image_path, 'rb') as f:
            target_b64 = base64.b64encode(f.read()).decode()
        
        payload = {
            "input": {
                "source_image": source_b64,
                "target_image": target_b64,
                "model": model,
                "parameters": params
            }
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.post(f"{self.endpoint_url}/run", json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="RunPod API failed")
        
        return response.json()

# Usage in your FastAPI app
runpod_api = RunPodKissAPI(
    endpoint_url="your-runpod-endpoint-url",
    api_key="your-runpod-api-key"
)

@app.post("/generate-kiss-video")
async def generate_video(request: VideoRequest):
    result = await runpod_api.generate_kiss_video(
        source_image_path=request.source_image,
        model=request.model,
        guidance_scale=request.guidance_scale,
        prompt=request.prompt
    )
    return result
```

### Frontend Integration (React)

```javascript
const generateKissVideo = async (sourceImage, options = {}) => {
  const formData = new FormData();
  formData.append('source_image', sourceImage);
  formData.append('model', options.model || 'remade_ai');
  formData.append('parameters', JSON.stringify({
    guidance_scale: 6.0,
    flow_shift: 5.0,
    lora_strength: 1.0,
    prompt: 'Two heads, cinematic romantic lighting, k144ing kissing softly',
    ...options.parameters
  }));
  
  const response = await fetch('/api/generate-kiss-video', {
    method: 'POST',
    body: formData,
    headers: {
      'Authorization': `Bearer ${authToken}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to generate video');
  }
  
  return response.json();
};
```

## Configuration

### Model Configuration

Edit `runpod_config.py` to adjust:

- GPU requirements
- Memory allocation  
- Model parameters
- Performance settings

### Environment Variables

- `RUNPOD_API_KEY`: Your RunPod API key
- `MODEL_CACHE_DIR`: Directory for model caching
- `TEMP_DIR`: Temporary file directory
- `HUGGINGFACE_HUB_CACHE`: Hugging Face model cache

## Performance Optimization

### GPU Memory Management

- Use `fp16` precision for memory efficiency
- Enable attention slicing for larger images
- Configure CPU offloading if needed

### Scaling

- Configure idle timeout for cost optimization
- Set appropriate execution timeout
- Monitor usage in RunPod dashboard

## Costs

Estimated costs on RunPod (RTX 4090):

- **Wan-AI I2V Base Model**: ~$0.15-0.25 per video (30-60 seconds generation)
- **Remade-AI Kissing LoRA**: ~$0.20-0.35 per video (45-90 seconds generation)

*Costs vary based on GPU availability and generation parameters*

## Troubleshooting

### Common Issues

1. **Model Loading Failures - "No space left on device"**
   - **Problem**: RunPod instance has insufficient disk space (Wan-AI model is ~28GB)
   - **Solution**: Use RunPod instance with 50+ GB disk space (150GB recommended)
   - **Check disk space**: Response includes `disk_space_gb` field
   - **Alternative**: Use smaller models or pre-download to volume storage

2. **Model Loading Failures - Network Issues**
   - Check internet connection for model downloads
   - Verify Hugging Face model IDs are correct
   - Models download automatically on first use (may take 5-10 minutes)

3. **Deployment Issues**
   - Verify Docker is running
   - Check RunPod API key permissions
   - Ensure image registry credentials are set
   - **Disk Space**: Minimum 150GB recommended in RunPod configuration

4. **Generation Failures**
   - Validate input images are proper format
   - Check generation parameters are within bounds
   - Monitor GPU memory usage (16+ GB VRAM required)

### Logs

```bash
# View RunPod logs
runpod logs <endpoint-id>

# Local testing
python main.py
```

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (mock mode)
python main.py
```

### Model Updates

1. Update model IDs in `runpod_config.py`
2. For new LoRAs, update `generate_with_lora.py`
3. Test locally with mock implementation
4. Rebuild and redeploy:
   ```bash
   python deploy.py
   ```

### Important Prompt Guidelines

#### For Remade-AI Kissing LoRA:
- **Always include "k144ing kissing"** in the prompt
- Examples:
  - "Two heads, cinematic romantic lighting, k144ing kissing softly"
  - "A man and woman in snowy mountains, k144ing kissing"
  - "Passionate scene with k144ing kissing"

#### For Wan-AI Base Model:
- Use descriptive scene prompts
- Examples:
  - "Two people in a romantic scene, cinematic lighting"
  - "Couple embracing in beautiful garden setting"

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check RunPod documentation
- Review Hugging Face model pages
- Open GitHub issue for bugs
