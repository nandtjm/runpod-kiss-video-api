#!/bin/bash

echo "🚀 RunPod Kiss Video Generator - Fast Build"
echo "=========================================="
echo ""

# Quick validation
echo "🔍 Validating environment..."
python3 -c "import torch; print(f'PyTorch: {torch.__version__}')" || exit 1
python3 -c "import runpod; print('RunPod: Ready')" || exit 1

# Check volume mount
echo "📁 Volume check: $(test -d /runpod-volume && echo '✅ Mounted' || echo '❌ Missing')"

# Check models if volume mounted
if [ -d "/runpod-volume/models" ]; then
    echo "📦 Models directory: ✅ Found"
else
    echo "📦 Models directory: ❌ Not found"
fi

# Start handler
echo ""
echo "✅ Starting handler..."
python3 runpod_serverless.py