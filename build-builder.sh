#!/bin/sh
# shellcheck shell=dash
set -eux

BUILD_IMAGE_NAME=${BUILD_IMAGE_NAME:-debian}
BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG:-bullseye-slim}
CI_PIPELINE_ID=${CI_PIPELINE_ID:-devel}

UV_HOST_HARBOR=${UV_HOST_HARBOR:-artifacts.knut.univention.de}
UPX_IMAGE_REGISTRY=${UPX_IMAGE_REGISTRY:-${UV_HOST_HARBOR}/upx/}

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
