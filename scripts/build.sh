#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Default: don't load images into Minikube
LOAD_MINIKUBE=false

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --minikube) LOAD_MINIKUBE=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

DOCKER_REPO="devscouse/privatelibrary"

echo "Building API Docker image..."

if $LOAD_MINIKUBE; then
    echo "Activating Minikube Docker environment..."
    eval $(minikube docker-env)
fi

# Build and push the API docker image
api_version=$(cat api/VERSION)
tag_name=core-synapse-api-$api_version
docker build -t $tag_name -f api/Dockerfile .
docker tag $tag_name $DOCKER_REPO:$tag_name
docker push $DOCKER_REPO:$tag_name

if $LOAD_MINIKUBE; then
    minikube image load "$DOCKER_REPO:$tag_name"
fi

for model_dir in models/*/ ; do
    model_name=$(basename "$model_dir")
    if [ $model_name = "common" ]; then
       continue
    fi

    model_version=$(cat "$model_dir/VERSION")
    tag_name=core-synapse-$model_name-$model_version
    echo "Building $model_name Docker image..."

    docker build -t $tag_name -f "$model_dir/Dockerfile" "$model_dir"
    docker tag $tag_name $DOCKER_REPO:$tag_name
    docker push $DOCKER_REPO:$tag_name
    echo "$tag_name pushed to $DOCKER_REPO"

    if $LOAD_MINIKUBE; then
        minikube image load "$DOCKER_REPO:$tag_name"
    fi
done

echo "Build and push complete! 🚀"
