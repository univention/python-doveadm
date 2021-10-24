#!/bin/ash
# shellcheck shell=dash
set -euxo pipefail

BUILD_IMAGE_NAME=${BUILD_IMAGE_NAME:-debian}
BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG:-bullseye-slim}
CI_PIPELINE_ID=${CI_PIPELINE_ID:-devel}

INTERNAL_DOCKER_REPO=${INTERNAL_DOCKER_REPO:-artifacts.knut.univention.de}
UPX_IMAGE_REGISTRY=${UPX_IMAGE_REGISTRY:-${INTERNAL_DOCKER_REPO}/upx/}

BASE_NAME="${UPX_IMAGE_REGISTRY}builder-python-doveadm-${BUILD_IMAGE_NAME}-${BUILD_IMAGE_TAG}"
BUILD_NAME="${BASE_NAME}:build-${CI_PIPELINE_ID}"
RELEASE_NAME="${BASE_NAME}:latest"

docker build \
  --tag="${BUILD_NAME}" \
  --tag="${RELEASE_NAME}" \
  --build-arg "BUILD_IMAGE_NAME=${BUILD_IMAGE_NAME}" \
  --build-arg "BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG}" \
  --file Dockerfile .

docker push "${BUILD_NAME}"
docker push "${RELEASE_NAME}"

# [EOF]
