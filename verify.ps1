$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot "src"
    Write-Host "==> Running progen check..."
    python -m progen check
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "==> All progen checks passed!"
} finally {
    Pop-Location
}
