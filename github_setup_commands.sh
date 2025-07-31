#!/bin/bash

# GitHub Repository Setup Commands
# Replace YOUR_GITHUB_USERNAME with your actual GitHub username

echo "Setting up GitHub repository for RunPod Kiss Video API..."

# Add remote origin (replace YOUR_GITHUB_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/runpod-kiss-video-api.git

# Verify remote was added
git remote -v

# Push to main branch
git branch -M main
git push -u origin main

echo "Repository successfully pushed to GitHub!"
echo ""
echo "Your repository will be available at:"
echo "https://github.com/YOUR_GITHUB_USERNAME/runpod-kiss-video-api"
echo ""
echo "Next steps:"
echo "1. Update the Docker image name in runpod_config.py"
echo "2. Set up RunPod account and API key"
echo "3. Deploy using: python deploy.py"