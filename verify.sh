#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Running progen check..."
python -m progen check

echo "==> All progen checks passed!"
