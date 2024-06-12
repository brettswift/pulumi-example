#!/usr/bin/env bash

cd "$(dirname "$0")" || exit 1

build_lambda() {
    echo "Building $1"
    cd lambdas/"$1" || exit 1
    rm -rf ./publish
    mkdir -p ./publish
    rsync -av --progress . ./publish/ --exclude publish
    
    # Build the Docker image
    docker build -t lambda-package .

    # Run the Docker image and copy the zip file from the container to the host
    docker run --name lambda-container lambda-package
    docker cp lambda-container:/app/package.zip ./publish/

    # Clean up the Docker container
    docker rm lambda-container

    # Clean up the Docker image
    # docker rmi lambda-package

    cd ..
}

build_lambda "queue_processor"