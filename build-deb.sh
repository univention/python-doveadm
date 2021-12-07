#!/bin/sh
# shellcheck shell=dash
set -eux

BUILD_IMAGE_NAME=${BUILD_IMAGE_NAME:-debian}
BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG:-bullseye-slim}

UV_HOST_HARBOR=${UV_HOST_HARBOR:-artifacts.knut.univention.de}
UPX_IMAGE_REGISTRY=${UPX_IMAGE_REGISTRY:-${UV_HOST_HARBOR}/upx/}

BASE_NAME="${UPX_IMAGE_REGISTRY}builder-python-doveadm-${BUILD_IMAGE_NAME}-${BUILD_IMAGE_TAG}"
RELEASE_NAME="${BASE_NAME}:latest"

DIST_DIR="${PWD}/dist"

mkdir --parents "${DIST_DIR}/deb_dist"

python3 setup.py sdist

docker run \
  --rm \
  --volume="${DIST_DIR}":/dist:rw \
  --env="BUILD_IMAGE_NAME=${BUILD_IMAGE_NAME}" \
  --env="BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG}" \
  "${RELEASE_NAME}"

# "--verbose" the long version of "-v" is not available in BusyBox
rm -v "$(ls "${DIST_DIR}"/doveadm-*.tar.gz)"

# [EOF]
