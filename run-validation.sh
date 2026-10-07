#!/bin/sh
set -eu
cd "$(dirname "$0")"
./scripts/build-runtime.sh >&2
exec docker run --rm --name rf-design-validation --cpus 2 --memory 6g \
  -v "$PWD:/project" -w /project \
  -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=2 -e YAPNR_RF_THREADS=2 \
  -e YAPNR_RF_REQUIRE_NATIVE=1 \
  --entrypoint python3 \
  28ghz-divider-rf:57df5897-1 \
  -u validate_design.py
