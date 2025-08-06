# Bazel WORKSPACE for AI Kiss Video Generator
# Optimized for RunPod Pod builds

workspace(name = "ai_kiss_video_generator")

# Docker rules for container builds
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Rules Docker
http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "b1e80761a8a8243d03ebca8845e9cc1ba6c82ce7c5179ce2b295cd36f7e394bf",
    urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.25.0/rules_docker-v0.25.0.tar.gz"],
)

load(
    "@io_bazel_rules_docker//repositories:repositories.bzl",
    container_repositories = "repositories",
)

container_repositories()

load("@io_bazel_rules_docker//repositories:deps.bzl", container_deps = "deps")
container_deps()

# Python rules
load(
    "@io_bazel_rules_docker//python:image.bzl",
    _py_image_repos = "repositories",
)
_py_image_repos()

# Container image repositories
load(
    "@io_bazel_rules_docker//container:container.bzl",
    "container_pull",
)

# Pull RunPod PyTorch base image
container_pull(
    name = "runpod_pytorch_base",
    registry = "docker.io",
    repository = "runpod/pytorch",
    tag = "2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
)

# Pull latest Python base for lightweight builds
container_pull(
    name = "python_base",
    registry = "docker.io", 
    repository = "python",
    tag = "3.10-slim-bullseye",
)

# Platform detection for multi-arch builds
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "platforms",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/platforms/releases/download/0.0.6/platforms-0.0.6.tar.gz",
        "https://github.com/bazelbuild/platforms/releases/download/0.0.6/platforms-0.0.6.tar.gz",
    ],
    sha256 = "5308fc1d8865406a49427ba24a9ab53087f17f5266a7aabbfc28823f3916e1ca6",
)