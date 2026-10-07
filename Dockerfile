# syntax=docker/dockerfile:1
# YAPNR is an external, pinned dependency. No upstream source is stored in this repo.
FROM ghcr.io/studio-fug/yapnr@sha256:7434f6a7390db07e2bd43bd8f48df8d3536edd0ba5cff5ce9fc73e872bc32c58
USER root
# Work around the pinned wheel's missing subpackages by fetching the full upstream
# Python source at build time. Keep its matching native solver from the base image.
RUN python3 - <<'PY'
import hashlib
import io
from pathlib import Path
import tarfile
import urllib.request
revision = '57df589747565bb85cde37a861c5939f844b1a13'
url = f'https://codeload.github.com/Studio-Fug/yapnr/tar.gz/{revision}'
expected = '0808d292867599ca04636c38a101c8a66d7222bb4e65483b8ba4a28ecbbc831a'
with urllib.request.urlopen(url, timeout=120) as response:
    archive = response.read()
assert hashlib.sha256(archive).hexdigest() == expected, 'YAPNR dependency archive checksum mismatch'
prefix = f'yapnr-{revision}/'
root = Path('/opt/yapnr-dependency')
with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tar:
    for member in tar.getmembers():
        relative = member.name.removeprefix(prefix)
        if not member.name.startswith(prefix) or not relative.startswith('yapnr/'):
            continue
        if not member.isfile():
            continue
        target = root / relative
        assert target.resolve().is_relative_to(root), 'Unsafe archive member'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(tar.extractfile(member).read())
source = root/'yapnr/rf/fdtd/native'
actual = hashlib.sha256((source/'fdtd.c').read_bytes() + (source/'fdtd_kernels.h').read_bytes()).hexdigest()
assert actual == '9f149dc44267e05574813e7482ec39fb5030d5cf3b7f5d7c362dbb40a70d4a33'
PY
ENV PYTHONPATH=/opt/yapnr-dependency
# Fail at build time if exports, Torch, or the matching native backend cannot load.
RUN python3 -c 'import torch; from yapnr.rf import driver, validate; from yapnr.rf.export import report, kicad, touchstone; from yapnr.rf.fdtd.native_kernel import source_sha256, status; assert status()["loaded"]; assert source_sha256() == "9f149dc44267e05574813e7482ec39fb5030d5cf3b7f5d7c362dbb40a70d4a33"'
WORKDIR /project
