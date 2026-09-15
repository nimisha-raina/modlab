#!/usr/bin/env bash
# Run the project from any working directory on macOS or Linux.
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${BLENDER_BIN:-}" ]]; then
    BLENDER_EXECUTABLE="$BLENDER_BIN"
elif command -v blender >/dev/null 2>&1; then
    BLENDER_EXECUTABLE="$(command -v blender)"
elif [[ -x /Applications/Blender.app/Contents/MacOS/Blender ]]; then
    BLENDER_EXECUTABLE=/Applications/Blender.app/Contents/MacOS/Blender
else
    echo "Blender was not found. Set BLENDER_BIN to its executable path." >&2
    exit 1
fi
exec "$BLENDER_EXECUTABLE" --background --python-exit-code 1 --python "$PROJECT_ROOT/run.py" -- "$@"
