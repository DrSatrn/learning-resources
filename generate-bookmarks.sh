#!/usr/bin/env sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_SCRIPT="$SCRIPT_DIR/scripts/resource_tools.py"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "$PYTHON_SCRIPT" export-bookmarks
fi

if command -v python >/dev/null 2>&1; then
    exec python "$PYTHON_SCRIPT" export-bookmarks
fi

echo "Python 3 is required to generate the bookmarks export." >&2
exit 1
