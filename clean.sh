#!/bin/sh

python3 setup.py clean --all
rm -rf MANIFEST .coverage dist/doveadm* build/* ./*.egg-info .tox .eggs docs/.build/* .mypy_cache
rm -f doveadm/*.py? tests/*.py? ./*.py?
find . -name __pycache__ -print0 | xargs --null --replace=name rm -r name
