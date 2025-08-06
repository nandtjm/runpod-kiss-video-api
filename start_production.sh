#!/bin/bash

echo "🚀 Production AI Kiss Video Generator"
echo "===================================="
echo ""

# Environment info
echo "📋 Environment Information:"
echo "  Python: $(python3 --version)"
echo "  Working Directory: $(pwd)"
echo "  Model Cache: ${MODEL_CACHE_DIR}"
echo "  Device: ${CUDA_VISIBLE_DEVICES:-auto}"
echo ""

# GPU validation
echo "🎮 GPU Validation:"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits | while IFS=, read gpu_name memory_total memory_free; do
        echo "  GPU: $gpu_name"
        echo "  VRAM: ${memory_free}MB free / ${memory_total}MB total"
    done
else
    echo "  ⚠️  nvidia-smi not available"
fi
echo ""

# PyTorch validation
echo "🔥 PyTorch Validation:"
python3 -c "
import torch
print(f'  PyTorch: {torch.__version__}')
print(f'  CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  CUDA Version: {torch.version.cuda}')
    print(f'  GPU Count: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'  GPU {i}: {torch.cuda.get_device_name(i)}')
" || echo "  ❌ PyTorch validation failed"
echo ""

# Volume validation
echo "📁 Volume Validation:"
if [ -d "/runpod-volume" ]; then
    echo "  ✅ Volume mounted at /runpod-volume"
    volume_size=$(df -h /runpod-volume | awk 'NR==2 {print $2}')
    volume_used=$(df -h /runpod-volume | awk 'NR==2 {print $3}')
    echo "  Volume Size: ${volume_used} used / ${volume_size} total"
    
    if [ -d "${MODEL_CACHE_DIR}" ]; then
        echo "  ✅ Models directory found"
        model_count=$(find "${MODEL_CACHE_DIR}" -type f 2>/dev/null | wc -l)
        echo "  Model files: ${model_count}"
        
        # Check Wan-AI model specifically
        wan_model_path="${MODEL_CACHE_DIR}/Wan2.1-I2V-14B-720P"
        if [ -d "$wan_model_path" ]; then
            wan_files=$(find "$wan_model_path" -type f 2>/dev/null | wc -l)
            echo "  ✅ Wan-AI model: ${wan_files} files"
        else
            echo "  ❌ Wan-AI model not found"
        fi
    else
        echo "  ❌ Models directory not found: ${MODEL_CACHE_DIR}"
    fi
else
    echo "  ❌ Volume not mounted"
fi
echo ""

# Dependencies validation
echo "🔧 Dependencies Validation:"
python3 -c "
import sys
required_packages = [
    'runpod', 'torch', 'diffusers', 'transformers', 
    'PIL', 'cv2', 'numpy', 'loguru'
]

for package in required_packages:
    try:
        if package == 'PIL':
            import PIL
            version = PIL.__version__
        elif package == 'cv2':
            import cv2
            version = cv2.__version__
        else:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
        print(f'  ✅ {package}: {version}')
    except ImportError:
        print(f'  ❌ {package}: not found')
        sys.exit(1)
" || echo "  ❌ Dependencies validation failed"
echo ""

# Memory optimization
echo "🧠 Memory Optimization:"
python3 -c "
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print('  ✅ GPU memory cleared')
    print('  ✅ CUDA optimizations enabled')
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
else:
    print('  ⚠️  CUDA not available, using CPU')
" || echo "  ❌ Memory optimization failed"
echo ""

# Final health check
echo "🏥 Production Health Check:"
python3 -c "
from handler import health_check
import json
result = health_check()
print(json.dumps(result, indent=2))
if result.get('status') != 'healthy':
    print('❌ Health check failed!')
    exit(1)
else:
    print('✅ All systems ready!')
" || echo "❌ Health check script failed"
echo ""

# Start the serverless handler
echo "✅ Starting production serverless handler..."
echo ""
python3 runpod_serverless.py