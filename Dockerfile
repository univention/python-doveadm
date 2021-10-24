
# License: AGPL-3.0-or-later
# Copyright (C) 2021 Univention GmbH

ARG DOCKERHUB_CACHE=""
ARG BUILD_IMAGE_NAME=debian
ARG BUILD_IMAGE_TAG=bullseye-slim

FROM ${DOCKERHUB_CACHE}${BUILD_IMAGE_NAME}:${BUILD_IMAGE_TAG} AS build

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive \
    apt-get install \
      --assume-yes \
      --verbose-versions \
      --no-install-recommends \
      build-essential=12.9 \
      dh-python=4.20201102+* \
      fakeroot=1.25.3-* \
      python3-all=3.9.2-* \
      python3-stdeb=0.10.0-* \
  && \
  rm -rf /var/lib/apt/lists/*

COPY builder-entrypoint.sh /

ENTRYPOINT ["/builder-entrypoint.sh"]

# [EOF]
