# RunPod Serverless AI Kiss Video Generator
# Use RunPod's official PyTorch 2.8 base image with RTX 5090 Blackwell support (CUDA 12.8.1)

FROM runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Environment variables for RTX 5090 optimization
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0
ENV TORCH_CUDA_ARCH_LIST="8.9,9.0,12.0"
ENV MODEL_CACHE_DIR=/runpod-volume/models

# RTX 5090 GPU memory optimization
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
ENV CUDA_LAUNCH_BLOCKING=0
ENV TORCH_BACKENDS_CUDNN_BENCHMARK=1
ENV OMP_NUM_THREADS=1

# Cache directories (use network volume)
ENV HF_HOME=/runpod-volume/models/.cache
ENV TRANSFORMERS_CACHE=/runpod-volume/models/.cache/transformers
ENV DIFFUSERS_CACHE=/runpod-volume/models/.cache/diffusers
ENV TORCH_HOME=/runpod-volume/models/.cache/torch

# System dependencies for CUDA 12.8+
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install RunPod SDK first
RUN pip install --no-cache-dir runpod>=1.6.0

# Copy requirements and install Python dependencies
COPY requirements.serverless.txt .
RUN pip install --no-cache-dir -r requirements.serverless.txt

# Copy application code
COPY . .

# Make sure handler is executable
RUN chmod +x handler.serverless.py app.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Expose port (if needed)
EXPOSE 8000

# Entry point - RunPod will call the handler
CMD ["python", "app.py"]