# we check all 3 python versions to account for WSL, python install from ms.store and standard pyhton3
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptRoot "scripts/resource_tools.py"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $pythonScript export-bookmarks
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python $pythonScript export-bookmarks
    exit $LASTEXITCODE
}

if (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 $pythonScript export-bookmarks
    exit $LASTEXITCODE
}

throw "Python 3 is required to generate the bookmarks export."
