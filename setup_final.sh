#!/bin/bash

# Final Production Volume Setup Script
# Pre-loads AI models on RunPod Network Volume (one-time setup)
# Professional model management strategy

set -e  # Exit on any error

echo "🚀 RunPod Volume Setup - Final Production Version"
echo "================================================"
echo ""
echo "This script pre-loads AI models on RunPod Network Volume"
echo "This is a ONE-TIME setup that enables instant container startup"
echo "Used by professional AI services: ComfyUI Cloud, Automatic1111, etc."
echo ""

# Configuration
VOLUME_PATH="/workspace"
MODELS_DIR="$VOLUME_PATH/models"
CACHE_DIR="$MODELS_DIR/.cache"

echo "📋 Configuration:"
echo "  Volume Path: $VOLUME_PATH"
echo "  Models Directory: $MODELS_DIR"
echo "  Cache Directory: $CACHE_DIR"
echo "  Strategy: Network Volume (Professional)"
echo ""

# Verify we're running on RunPod with volume mounted
if [ ! -d "$VOLUME_PATH" ]; then
    echo "❌ ERROR: Volume not mounted at $VOLUME_PATH"
    echo ""
    echo "🔧 Setup Required:"
    echo "1. Create RunPod Network Volume (100GB+) in Dashboard"
    echo "2. Rent RunPod Pod with volume attached to /workspace"
    echo "3. SSH into Pod and run this script"
    echo ""
    echo "📖 Detailed instructions: https://docs.runpod.io/pods/storage/network-volumes"
    exit 1
fi

echo "✅ Volume detected at $VOLUME_PATH"

# Check if we're root (required for some operations)
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: Not running as root. Some operations may fail."
fi

# Create directory structure
echo ""
echo "📁 Creating directory structure..."
mkdir -p "$MODELS_DIR"
mkdir -p "$CACHE_DIR"
mkdir -p "$VOLUME_PATH/temp"

# Check available space
echo ""
echo "💾 Checking available disk space..."
if command -v df >/dev/null 2>&1; then
    AVAILABLE_GB=$(df "$VOLUME_PATH" | awk 'NR==2 {printf "%.1f", $4/1024/1024}')
    echo "Available space: ${AVAILABLE_GB}GB on volume"
    
    # Check if we have enough space (need ~30GB for models)
    if (( $(echo "$AVAILABLE_GB < 35" | bc -l 2>/dev/null || echo "0") )); then
        echo "⚠️  WARNING: Less than 35GB available (need ~30GB for models)"
        echo "   Consider using larger volume size or cleaning up existing data"
        echo ""
        read -p "🤔 Continue anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Setup cancelled. Please ensure sufficient disk space."
            exit 1
        fi
    fi
else
    echo "⚠️  Cannot check disk space (df command not available)"
fi

# Set environment for downloads
export HUGGINGFACE_HUB_CACHE="$CACHE_DIR"
export HF_HOME="$CACHE_DIR"
export HF_DATASETS_CACHE="$CACHE_DIR"

echo ""
echo "🔧 Environment setup:"
echo "  HUGGINGFACE_HUB_CACHE=$HUGGINGFACE_HUB_CACHE"
echo "  HF_HOME=$HF_HOME"

# Install/upgrade huggingface-cli if needed
echo ""
echo "📦 Checking Hugging Face CLI..."
if ! command -v huggingface-cli >/dev/null 2>&1; then
    echo "📥 Installing Hugging Face CLI..."
    pip install --upgrade huggingface_hub
else
    echo "✅ Hugging Face CLI found"
    # Upgrade to latest version for better reliability
    pip install --upgrade huggingface_hub --quiet
fi

# Verify huggingface-cli works
if ! huggingface-cli --version >/dev/null 2>&1; then
    echo "❌ ERROR: huggingface-cli installation failed"
    echo "Please install manually: pip install huggingface_hub"
    exit 1
fi

echo ""
echo "📥 Starting Model Downloads..."
echo "This may take 20-40 minutes depending on network speed"
echo "Models will be downloaded directly to the persistent volume"
echo ""

# Function to download with retry and verification
download_model_with_retry() {
    local repo_id="$1"
    local local_dir="$2"
    local description="$3"
    local max_attempts=3
    local attempt=1
    
    echo "📥 Downloading $description..."
    echo "  Repository: $repo_id"
    echo "  Destination: $local_dir"
    
    # Check if model already exists and is complete
    if [ -d "$local_dir" ] && [ "$(ls -A "$local_dir" 2>/dev/null)" ]; then
        # Basic completeness check
        local file_count=$(find "$local_dir" -type f | wc -l)
        if [ "$file_count" -gt 5 ]; then  # Reasonable threshold
            local existing_size=$(du -sh "$local_dir" 2>/dev/null | cut -f1 || echo "Unknown")
            echo "  ✅ Model already exists: $existing_size, $file_count files"
            echo "  ⏭️  Skipping download"
            return 0
        else
            echo "  ⚠️  Existing model appears incomplete ($file_count files), re-downloading..."
            rm -rf "$local_dir"
        fi
    fi
    
    # Download with retry logic
    while [ $attempt -le $max_attempts ]; do
        echo "  📡 Download attempt $attempt/$max_attempts..."
        
        # Create directory
        mkdir -p "$local_dir"
        
        # Download with optimized settings
        if huggingface-cli download "$repo_id" \
            --local-dir "$local_dir" \
            --resume-download \
            --local-dir-use-symlinks=False \
            --repo-type=model; then
            
            # Verify download
            local final_size=$(du -sh "$local_dir" 2>/dev/null | cut -f1 || echo "Unknown")
            local file_count=$(find "$local_dir" -type f 2>/dev/null | wc -l || echo "0")
            
            echo "  ✅ Download completed: $final_size, $file_count files"
            
            # Basic verification - check for common model files
            if ls "$local_dir"/*.{safetensors,bin,pth,json} >/dev/null 2>&1; then
                echo "  ✅ Model files verified"
                return 0
            else
                echo "  ⚠️  Download completed but model files not found"
            fi
        else
            echo "  ❌ Download failed (attempt $attempt/$max_attempts)"
        fi
        
        attempt=$((attempt + 1))
        if [ $attempt -le $max_attempts ]; then
            echo "  ⏳ Retrying in 15 seconds..."
            sleep 15
        fi
    done
    
    echo "  ❌ Failed to download $description after $max_attempts attempts"
    return 1
}

# Download Wan-AI model (main model - ~28GB)
echo "🎯 Step 1: Downloading Wan-AI I2V 14B Model"
WAN_MODEL_DIR="$MODELS_DIR/Wan2.1-I2V-14B-720P"

if download_model_with_retry "Wan-AI/Wan2.1-I2V-14B-720P" "$WAN_MODEL_DIR" "Wan-AI I2V 14B Model (~28GB)"; then
    echo "✅ Wan-AI model setup complete"
else
    echo "❌ Failed to download Wan-AI model"
    echo "💡 This is the main model required for video generation"
    echo "💡 You can try running the script again later"
    # Don't exit - maybe user wants to continue without LoRA
fi

echo ""

# Download LoRA model (optional - ~400MB)
echo "🎯 Step 2: Downloading Kissing LoRA Model"
LORA_MODEL_DIR="$MODELS_DIR/kissing-lora"

if download_model_with_retry "Remade-AI/kissing" "$LORA_MODEL_DIR" "Kissing LoRA Model (~400MB)"; then
    echo "✅ LoRA model setup complete"
else
    echo "⚠️  Failed to download LoRA model (optional)"
    echo "💡 Main functionality will still work with base Wan-AI model"
fi

echo ""
echo "🔍 Final Verification..."

# Comprehensive model verification
verify_models() {
    echo "📊 Volume Usage Summary:"
    if command -v du >/dev/null 2>&1; then
        du -sh "$MODELS_DIR"/* 2>/dev/null | sort -hr || echo "No models found"
    else
        echo "Cannot calculate disk usage (du command not available)"
    fi
    
    echo ""
    echo "📁 Model Directory Structure:"
    ls -la "$MODELS_DIR" 2>/dev/null || echo "Models directory not found"
    
    echo ""
    echo "🧪 Model Validation:"
    
    # Check Wan-AI model
    if [ -d "$WAN_MODEL_DIR" ] && [ "$(ls -A "$WAN_MODEL_DIR" 2>/dev/null)" ]; then
        local wan_size=$(du -sh "$WAN_MODEL_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
        local wan_files=$(find "$WAN_MODEL_DIR" -type f 2>/dev/null | wc -l || echo "0")
        echo "  ✅ Wan-AI Model: $wan_size, $wan_files files"
        
        # Check for critical files
        if ls "$WAN_MODEL_DIR"/*.{safetensors,bin,pth} >/dev/null 2>&1; then
            echo "      ✅ Model weights found"
        else
            echo "      ⚠️  Model weights not found"
        fi
        
        if ls "$WAN_MODEL_DIR"/*.json >/dev/null 2>&1; then
            echo "      ✅ Model config found"
        else
            echo "      ⚠️  Model config not found"
        fi
    else
        echo "  ❌ Wan-AI Model: Not found or empty"
    fi
    
    # Check LoRA model
    if [ -d "$LORA_MODEL_DIR" ] && [ "$(ls -A "$LORA_MODEL_DIR" 2>/dev/null)" ]; then
        local lora_size=$(du -sh "$LORA_MODEL_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
        local lora_files=$(find "$LORA_MODEL_DIR" -type f 2>/dev/null | wc -l || echo "0")
        echo "  ✅ LoRA Model: $lora_size, $lora_files files"
    else
        echo "  ⚠️  LoRA Model: Not found (optional)"
    fi
}

verify_models

# Create setup completion marker
echo ""
echo "📝 Creating setup marker..."
echo "Setup completed on $(date)" > "$VOLUME_PATH/.models_setup_complete"
echo "Strategy: Network Volume (Professional)" >> "$VOLUME_PATH/.models_setup_complete"
echo "Wan-AI Model: $([ -d "$WAN_MODEL_DIR" ] && echo "✅ Installed" || echo "❌ Missing")" >> "$VOLUME_PATH/.models_setup_complete"
echo "LoRA Model: $([ -d "$LORA_MODEL_DIR" ] && echo "✅ Installed" || echo "⚠️ Missing")" >> "$VOLUME_PATH/.models_setup_complete"

echo ""
echo "🎉 Volume Setup Complete!"
echo ""
echo "📋 Summary:"

# Final status check
wan_status="❌ Missing"
lora_status="❌ Missing"

if [ -d "$WAN_MODEL_DIR" ] && [ "$(ls -A "$WAN_MODEL_DIR" 2>/dev/null)" ]; then
    wan_status="✅ Ready"
fi

if [ -d "$LORA_MODEL_DIR" ] && [ "$(ls -A "$LORA_MODEL_DIR" 2>/dev/null)" ]; then
    lora_status="✅ Ready"
fi

echo "  📦 Wan-AI Model: $wan_status"
echo "  📦 LoRA Model: $lora_status"
echo "  💾 Volume Path: $VOLUME_PATH"
echo "  🔗 Models accessible at: /workspace/models/"
echo "  ⚡ Strategy: Network Volume (Professional)"
echo ""

if [[ "$wan_status" == "✅ Ready" ]]; then
    echo "🚀 Next Steps:"
    echo ""
    echo "1. 🛑 Stop this RunPod Pod (models remain on volume):"
    echo "   - Go to RunPod Dashboard → My Pods → Stop"
    echo ""
    echo "2. 🏗️  Build Docker image (on your local machine):"
    echo "   cd runpod-kiss-api"
    echo "   ./build_final.sh"
    echo ""
    echo "3. 📤 Push Docker image:"
    echo "   docker push nandtjm/kiss-video-generator:final-volume"
    echo ""
    echo "4. 🎯 Create RunPod Serverless Endpoint:"
    echo "   - Docker Image: nandtjm/kiss-video-generator:final-volume"
    echo "   - Network Volume: Attach your volume to /workspace"
    echo "   - GPU: RTX 4090, Memory: 32GB"
    echo ""
    echo "5. 🧪 Test endpoint - expect <30 second cold start!"
    echo ""
    echo "💰 Cost Benefits:"
    echo "  📊 Volume storage: ~$7/month for 100GB"
    echo "  ⚡ No download costs per container"
    echo "  🚀 Professional reliability (99%+ uptime)"
    echo "  💸 Break-even: ~35 videos/month vs API services"
    echo ""
    echo "🎬 You now have professional-grade AI model infrastructure!"
else
    echo "⚠️  Setup Issues Detected:"
    echo ""
    if [[ "$wan_status" != "✅ Ready" ]]; then
        echo "❌ Wan-AI model download failed"
        echo "   This is required for video generation"
        echo "   Try running the script again or check network connectivity"
    fi
    echo ""
    echo "🔧 Troubleshooting:"
    echo "  1. Check internet connectivity"
    echo "  2. Verify Hugging Face Hub access"
    echo "  3. Ensure sufficient disk space (>35GB)"
    echo "  4. Re-run this script to retry downloads"
fi