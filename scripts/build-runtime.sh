#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker build --tag 28ghz-divider-rf:57df5897-1 .
