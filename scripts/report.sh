#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 scripts/make_validation_report.py
rr validate requirements/
rr report --model requirements/ --evidence reports/testlogs/validation/test.xml \
  --sets-lock requirements/verification.rrlock \
  --html reports/traceability.html --json reports/traceability.json \
  --md reports/traceability.md --queue-out reports/gaps.json \
  --title '28 GHz two-way divider revision A' --fail-on none
rr check-report reports/traceability.json
