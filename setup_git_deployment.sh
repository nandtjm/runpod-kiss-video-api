#!/bin/bash

# Setup Git Repository for RunPod Serverless Deployment
# Creates the proper repository structure for Git-based deployment

set -e

echo "📋 Git Repository Setup for RunPod Serverless"
echo "============================================="
echo ""

echo "🎯 This script will:"
echo "  1. Initialize git repository (if needed)"
echo "  2. Create proper file structure"
echo "  3. Generate deployment-ready files"
echo "  4. Provide push instructions"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create proper directory structure
echo ""
echo "📁 Creating deployment structure..."

# Ensure we have the serverless files
SERVERLESS_FILES=(
    "handler.serverless.py"
    "requirements.serverless.txt" 
    "runpod_serverless.py"
)

echo "🔍 Checking serverless files..."
for file in "${SERVERLESS_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file missing!"
        echo ""
        echo "Please ensure these files exist:"
        echo "  - handler.serverless.py (main AI handler)"
        echo "  - requirements.serverless.txt (dependencies)"
        echo "  - runpod_serverless.py (RunPod integration)"
        echo ""
        echo "Run this first: bash deploy_direct_to_serverless.sh"
        exit 1
    fi
done

# Create runpod_serverless.py if it doesn't exist
if [ ! -f "runpod_serverless.py" ]; then
    echo "📝 Creating runpod_serverless.py..."
    cat > runpod_serverless.py << 'EOF'
#!/usr/bin/env python3
"""
RunPod Serverless Integration
Simple integration wrapper for the handler
"""

import runpod
from handler.serverless import handler

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
EOF
    echo "✅ runpod_serverless.py created"
fi

# Create a deployment-specific README
echo ""
echo "📝 Creating deployment README..."
cat > README_DEPLOYMENT.md << 'EOF'
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
EOF

echo "✅ Deployment README created"

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo ""
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/

# Jupyter Notebook
.ipynb_checkpoints

# Local environment
.env
.venv

# Large model files (use network volume instead)
*.safetensors
*.bin
*.pth
models/

# Docker
Dockerfile.backup

# Logs
*.log

# Temporary files
tmp/
temp/
*.tmp

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    echo "✅ .gitignore created"
fi

# Check git configuration
echo ""
echo "🔧 Checking Git configuration..."
if ! git config user.name >/dev/null 2>&1; then
    echo "⚠️  Git user not configured. Please set:"
    echo "   git config --global user.name 'Your Name'"
    echo "   git config --global user.email 'your.email@example.com'"
else
    echo "✅ Git user configured: $(git config user.name)"
fi

# Show current status
echo ""
echo "📊 Repository Status:"
echo "===================="
echo "Files ready for deployment:"
ls -la *.py *.txt *.md 2>/dev/null | head -10

echo ""
echo "Git status:"
git status --porcelain | head -10

# Stage files
echo ""
echo "📦 Staging files for commit..."
git add .

echo ""
echo "🚀 Ready to Deploy!"
echo "=================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 📤 Commit and push to GitHub:"
echo "   git commit -m 'Deploy serverless AI kiss video generator"
echo ""  
echo "   - Uses network volume models (no downloads)"
echo "   - Optimized for RunPod serverless deployment"
echo "   - Real AI video generation with Wan-AI models'"
echo ""
echo "   git push origin main"
echo ""
echo "2. 🔗 Create GitHub repository if needed:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: ai-kiss-generator"
echo "   - Make it public (or give RunPod access)"
echo "   - Don't initialize with README (we have files already)"
echo ""
echo "3. 🔧 Add remote if new repository:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/ai-kiss-generator.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. 🚀 Configure RunPod Serverless:"
echo "   - Dashboard → Serverless → New Endpoint"
echo "   - Source Code → GitHub"
echo "   - Repository: https://github.com/YOUR_USERNAME/ai-kiss-generator"
echo "   - Path: runpod-kiss-api/"
echo "   - Base Image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
echo "   - Network Volume: ai-models-kiss-video → /runpod-volume"
echo ""
echo "5. 🧪 Test deployment:"
echo "   - Health check should return 'healthy'"
echo "   - Video generation should work with your network volume models"
echo ""
echo "🎉 After this, you'll have a working AI kiss video generator!"
echo "   No more Docker issues, no more build problems."
echo "   Just pure AI-powered video generation! 🎬✨"

# Offer to commit automatically
echo ""
read -p "💡 Commit files now? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 Committing files..."
    git commit -m "Deploy serverless AI kiss video generator

- Uses network volume models (no downloads in build)
- Optimized for RunPod serverless deployment  
- Real AI video generation with Wan-AI models
- Lightweight handler with efficient memory management
- Network volume path: /runpod-volume/models"

    echo "✅ Files committed!"
    echo ""
    echo "🚀 Now push to GitHub:"
    echo "   git push origin main"
    echo ""
    echo "   (Set up GitHub remote first if this is a new repo)"
else
    echo "ℹ️  Files staged but not committed. Commit when ready:"
    echo "   git commit -m 'Your commit message'"
    echo "   git push origin main"
fi

echo ""
echo "🎯 The end is in sight! Your AI kiss video generator will be running soon! 🚀"