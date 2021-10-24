#!/bin/dash
set -eux

DEB_DIST_DIR=${DEB_DIST_DIR:-/dist/deb_dist}
PY2DSC_COMPAT=${PY2DSC_COMPAT:-10}
PY2DSC_WITH_PY3=${PY2DSC_WITH_PY3:-True}

SRCGZ_PATH="$(ls /dist/doveadm-*.tar.gz)"

py2dsc \
  --compat="${PY2DSC_COMPAT}" \
  --dist-dir="${DEB_DIST_DIR}" \
  --with-python3="${PY2DSC_WITH_PY3}" \
  "${SRCGZ_PATH}"

py2dsc-deb \
  --compat="${PY2DSC_COMPAT}" \
  --dist-dir="${DEB_DIST_DIR}" \
  --with-python3="${PY2DSC_WITH_PY3}" \
  "${SRCGZ_PATH}"

rm --recursive --force --verbose "${DEB_DIST_DIR}"/doveadm-*/

# [EOF]
