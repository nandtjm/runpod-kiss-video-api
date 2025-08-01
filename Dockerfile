FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    unzip \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgoogle-perftools4 \
    libtcmalloc-minimal4 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH=/app
ENV CUDA_HOME=/usr/local/cuda
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better Docker caching
COPY requirements_minimal.txt requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip

# Install core dependencies first
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Install PyTorch with CUDA support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Optional dependencies can be added later if needed
# RUN pip install --no-cache-dir xformers
# RUN pip install --no-cache-dir controlnet-aux==0.0.10

# Copy application code
COPY . .

# Create directories for models and temporary files
RUN mkdir -p /app/models /app/temp /runpod-volume

# Set proper permissions
RUN chmod +x main.py rp_handler.py test_handler.py

# Test entry point to isolate issues
CMD ["python3", "-u", "test_handler.py"]