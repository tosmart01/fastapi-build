#!/bin/sh
IMAGE_NAME=example


DATE=$(date "+%Y%m%d")
COMMIT_ID=$(git rev-parse --verify HEAD)
COMMIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
release_part=$(echo "$COMMIT_BRANCH" | cut -d'/' -f1)
TAG=${release_part}_${DATE}_${COMMIT_ID: 0: 7}

docker build -t ${IMAGE_NAME}:${TAG} -f ./build/Dockerfile .
docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_NAME}:${TAG}
docker push ${IMAGE_NAME}:${TAG}

echo "docker pull ${IMAGE_NAME}:${TAG}"
docker push ${IMAGE_NAME}:${TAG