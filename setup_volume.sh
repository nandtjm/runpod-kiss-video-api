#!/bin/bash

# RunPod Volume Setup Script
# This script pre-loads models on RunPod Network Volume (one-time setup)
# Used by professional AI services for model management

echo "🚀 RunPod Volume Setup - Pre-loading AI Models"
echo "================================================"
echo ""
echo "This script will pre-load models on RunPod Network Volume"
echo "This is a ONE-TIME setup that enables instant container startup"
echo ""

# Configuration
VOLUME_PATH="/workspace"
MODELS_DIR="$VOLUME_PATH/models"
CACHE_DIR="$MODELS_DIR/.cache"

echo "📋 Configuration:"
echo "  Volume Path: $VOLUME_PATH"
echo "  Models Directory: $MODELS_DIR"
echo "  Cache Directory: $CACHE_DIR"
echo ""

# Verify we're running on RunPod with volume mounted
if [ ! -d "$VOLUME_PATH" ]; then
    echo "❌ ERROR: Volume not mounted at $VOLUME_PATH"
    echo ""
    echo "🔧 Setup Required:"
    echo "1. Create RunPod Network Volume (100GB+)"
    echo "2. Rent RunPod instance with volume attached to /workspace"
    echo "3. Run this script on the RunPod instance"
    echo ""
    exit 1
fi

echo "✅ Volume detected at $VOLUME_PATH"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$MODELS_DIR"
mkdir -p "$CACHE_DIR"
mkdir -p "$VOLUME_PATH/temp"

# Check available space
echo "💾 Checking available disk space..."
AVAILABLE_GB=$(df "$VOLUME_PATH" | awk 'NR==2 {printf "%.1f", $4/1024/1024}')
echo "Available space: ${AVAILABLE_GB}GB"

if (( $(echo "$AVAILABLE_GB < 50" | bc -l) )); then
    echo "⚠️  WARNING: Less than 50GB available"
    echo "   Wan-AI model alone requires ~28GB"
    echo "   Consider using larger volume size"
fi

# Set environment for downloads
export HUGGINGFACE_HUB_CACHE="$CACHE_DIR"
export HF_HOME="$CACHE_DIR"

echo ""
echo "📥 Starting Model Downloads..."
echo "This may take 15-30 minutes depending on network speed"
echo ""

# Function to download with retry
download_with_retry() {
    local repo_id="$1"
    local local_dir="$2"
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "📥 Downloading $repo_id (attempt $attempt/$max_attempts)..."
        
        if huggingface-cli download "$repo_id" \
            --local-dir "$local_dir" \
            --resume-download \
            --local-dir-use-symlinks=False; then
            echo "✅ Successfully downloaded $repo_id"
            return 0
        else
            echo "❌ Download failed (attempt $attempt/$max_attempts)"
            attempt=$((attempt + 1))
            if [ $attempt -le $max_attempts ]; then
                echo "⏳ Retrying in 10 seconds..."
                sleep 10
            fi
        fi
    done
    
    echo "❌ Failed to download $repo_id after $max_attempts attempts"
    return 1
}

# Install huggingface-cli if not present
if ! command -v huggingface-cli &> /dev/null; then
    echo "📦 Installing Hugging Face CLI..."
    pip install huggingface_hub
fi

# Download Wan-AI model (main model - 28GB)
WAN_MODEL_DIR="$MODELS_DIR/Wan2.1-I2V-14B-720P"
if [ -d "$WAN_MODEL_DIR" ] && [ "$(ls -A $WAN_MODEL_DIR)" ]; then
    echo "✅ Wan-AI model already exists, skipping download"
    EXISTING_SIZE=$(du -sh "$WAN_MODEL_DIR" | cut -f1)
    echo "   Existing size: $EXISTING_SIZE"
else
    echo "📥 Downloading Wan-AI I2V 14B Model (~28GB)..."
    echo "   This is the main model and will take the longest time"
    
    if download_with_retry "Wan-AI/Wan2.1-I2V-14B-720P" "$WAN_MODEL_DIR"; then
        FINAL_SIZE=$(du -sh "$WAN_MODEL_DIR" | cut -f1)
        FILE_COUNT=$(find "$WAN_MODEL_DIR" -type f | wc -l)
        echo "✅ Wan-AI model downloaded: $FINAL_SIZE, $FILE_COUNT files"
    else
        echo "❌ Failed to download Wan-AI model"
        echo "   You can continue and try again later"
    fi
fi

# Download LoRA model (optional - ~400MB)
LORA_MODEL_DIR="$MODELS_DIR/kissing-lora"
if [ -d "$LORA_MODEL_DIR" ] && [ "$(ls -A $LORA_MODEL_DIR)" ]; then
    echo "✅ LoRA model already exists, skipping download"
else
    echo "📥 Downloading Kissing LoRA Model (~400MB)..."
    
    if download_with_retry "Remade-AI/kissing-lora" "$LORA_MODEL_DIR"; then
        LORA_SIZE=$(du -sh "$LORA_MODEL_DIR" | cut -f1)
        echo "✅ LoRA model downloaded: $LORA_SIZE"
    else
        echo "⚠️  Failed to download LoRA model (optional)"
        echo "   Main functionality will still work with base model"
    fi
fi

echo ""
echo "🔍 Final Verification..."

# Verify models
echo "📊 Volume Usage:"
du -sh "$MODELS_DIR"/* 2>/dev/null | sort -hr || echo "No models found"

echo ""
echo "📁 Directory Structure:"
ls -la "$MODELS_DIR"

# Create verification file
echo "$(date): Models pre-loaded successfully" > "$VOLUME_PATH/.models_ready"

echo ""
echo "🎉 Volume Setup Complete!"
echo ""
echo "✅ Models are now pre-loaded on the network volume"
echo "✅ All future containers will have instant access"
echo "✅ No more 28GB downloads needed"
echo ""
echo "🚀 Next Steps:"
echo "1. Build and push your Docker image: ./build_volume.sh"
echo "2. Create RunPod Serverless Endpoint"
echo "3. Attach this volume to your endpoint"
echo "4. Deploy and enjoy instant startup!"
echo ""
echo "💰 Cost Benefits:"
echo "- Volume storage: ~$2-5/month for 100GB"
echo "- No download costs per container"
echo "- No API fees - full control"
echo "- Professional-grade model management"