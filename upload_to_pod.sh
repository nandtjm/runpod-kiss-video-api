#!/bin/bash

# Upload Files to RunPod Pod - Multiple Methods
# Choose the method that works best for your setup

echo "📤 Upload Files to RunPod Pod - Build Machine Setup"
echo "================================================="
echo ""

echo "🎯 Files to Upload:"
echo "==================="

# List all required files
REQUIRED_FILES=(
    "Dockerfile.production"
    "handler.production.py"
    "requirements.production.txt"
    "start_production.sh"
    "BUILD.bazel"
    "WORKSPACE"
    "runpod_serverless.py"
    "setup_pod.sh"
    "build_production_fast.sh"
    "build_with_bazel.sh"
)

echo "📋 Build System Files:"
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "  ✅ $file ($size)"
    else
        echo "  ❌ $file (missing)"
    fi
done

echo ""
echo "📊 Total files: ${#REQUIRED_FILES[@]}"
echo ""

echo "🚀 Upload Methods:"
echo "=================="
echo ""

echo "1️⃣ METHOD 1: Git Repository (Recommended)"
echo "   Pros: Version control, easy updates, collaborative"
echo "   Steps:"
echo "   a) Push files to GitHub:"
echo "      git add ."
echo "      git commit -m 'Add production build system'"
echo "      git push origin main"
echo ""
echo "   b) Clone in Pod:"
echo "      git clone https://github.com/YOUR_USERNAME/ai-kiss-generator.git"
echo "      cd ai-kiss-generator/runpod-kiss-api"
echo ""

echo "2️⃣ METHOD 2: Direct Upload via Web Interface"
echo "   Pros: No GitHub needed, drag & drop"
echo "   Steps:"
echo "   a) RunPod Dashboard → Your Pod → Connect → Web Terminal"
echo "   b) Create directory: mkdir -p /workspace/ai-kiss-generator"
echo "   c) Use file manager to drag & drop all files"
echo "   d) Or use upload button in web terminal"
echo ""

echo "3️⃣ METHOD 3: SCP/RSYNC (Advanced)"
echo "   Pros: Fast bulk transfer, automated"
echo "   Steps:"
echo "   a) Get Pod SSH details from RunPod dashboard"
echo "   b) scp -r ./* root@pod-ip:/workspace/build/"
echo ""

echo "4️⃣ METHOD 4: Create Upload Archive"
echo "   Pros: Single file upload, preserves permissions"
echo "   Steps:"
echo "   a) Create archive locally (this script will do it)"
echo "   b) Upload single .tar.gz file to Pod"
echo "   c) Extract on Pod"
echo ""

# Create upload archive
echo "📦 Creating Upload Archive..."
ARCHIVE_NAME="ai-kiss-generator-build-$(date +%Y%m%d-%H%M%S).tar.gz"

tar -czf "$ARCHIVE_NAME" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    "${REQUIRED_FILES[@]}" 2>/dev/null

if [ -f "$ARCHIVE_NAME" ]; then
    archive_size=$(ls -lh "$ARCHIVE_NAME" | awk '{print $5}')
    echo "✅ Archive created: $ARCHIVE_NAME ($archive_size)"
    echo ""
    echo "📋 Upload Archive Instructions:"
    echo "1. Upload $ARCHIVE_NAME to your Pod"
    echo "2. Extract: tar -xzf $ARCHIVE_NAME"
    echo "3. Run: bash setup_pod.sh"
else
    echo "❌ Failed to create archive"
fi

echo ""
echo "🎯 Recommended Workflow:"
echo "======================="
echo ""
echo "For Development (frequent changes):"
echo "→ Use METHOD 1 (Git Repository)"
echo ""
echo "For Quick Test:"
echo "→ Use METHOD 4 (Upload Archive)"
echo ""
echo "For Production Deployment:"
echo "→ Use METHOD 1 (Git) + Automated CI/CD"
echo ""

echo "🔧 Pod Setup Commands:"
echo "====================="
echo ""
echo "After uploading files to Pod, run:"
echo ""
echo "# Make scripts executable"
echo "chmod +x *.sh"
echo ""
echo "# Setup build environment"
echo "bash setup_pod.sh"
echo ""
echo "# Login to Docker Hub"
echo "docker login -u YOUR_USERNAME"
echo ""
echo "# Start build process"
echo "bash build_with_bazel.sh        # Ultra-fast Bazel build"
echo "# OR"
echo "bash build_production_fast.sh   # Fast Docker build"
echo ""

echo "💡 Pro Tips:"
echo "==========="
echo ""
echo "✅ Use Git for version control and easy updates"
echo "✅ Test with small files first"
echo "✅ Keep Pod terminal open during uploads"
echo "✅ Use network volumes for large model files"
echo "✅ Delete Pod after successful Docker push to save costs"
echo ""

echo "🎉 Ready to upload! Choose your preferred method above."