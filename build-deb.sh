#!/bin/ash
# shellcheck shell=dash
set -euxo pipefail

BUILD_IMAGE_NAME=${BUILD_IMAGE_NAME:-debian}
BUILD_IMAGE_TAG=${BUILD_IMAGE_TAG:-bullseye-slim}

INTERNAL_DOCKER_REPO=${INTERNAL_DOCKER_REPO:-artifacts.knut.univention.de}
UPX_IMAGE_REGISTRY=${UPX_IMAGE_REGISTRY:-${INTERNAL_DOCKER_REPO}/upx/}

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
