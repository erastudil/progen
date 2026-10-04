$ErrorActionPreference = "Stop"

Write-Host "==> Running progen check..."
python -m progen check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> All progen checks passed!"
