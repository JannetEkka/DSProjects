#!/usr/bin/env bash
# One-shot quality gate (run from the repository root): unit tests, full run + contract validator,
# then the sample evaluation (metrics, metamorphic suite, ablations, sensitivity).
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== unit tests";        python3 -m pytest code/tests -q -p no:cacheprovider
echo "== full run";          python3 code/main.py          # exits 1 if the validator reports a problem
echo "== evaluation";        python3 code/evaluation/main.py | tail -n 25
echo "== all checks passed"
