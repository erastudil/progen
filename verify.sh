#!/usr/bin/env bash
set -euo pipefail

echo "==> Running progen check..."
python -m progen check

echo "==> All progen checks passed!"
