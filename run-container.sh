#!/bin/sh
set -eu
cd "$(dirname "$0")"
IMAGE=ghcr.io/studio-fug/yapnr@sha256:7434f6a7390db07e2bd43bd8f48df8d3536edd0ba5cff5ce9fc73e872bc32c58
exec docker run --rm --name rf-design-jlc20mil --cpus 2 --memory 6g \
    -v "$PWD:/project" -w /project \
    -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=2 -e YAPNR_RF_THREADS=2 \
    -e PYTHONPATH=/project/vendor/yapnr \
    -e YAPNR_RF_REQUIRE_NATIVE=1 --entrypoint python3 "$IMAGE" \
    -u -c 'import subprocess; subprocess.run(["python3","-u","optimize.py"],check=True,timeout=9000)'
