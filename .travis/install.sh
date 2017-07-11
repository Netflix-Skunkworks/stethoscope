#!/bin/sh

set -e
set -u

case "${TEST_SUITE}" in
  js)
    make install-node-requirements;
  ;;
  py)
    make install-python-requirements;
  ;;
  *)
    echo "Unknown test suite: $TEST_SUITE"
    exit 1
esac;
