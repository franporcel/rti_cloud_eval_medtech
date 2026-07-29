#!/usr/bin/env bash
# Launches the Digital Operating Room demo and the guided Tutorial GUI together.
#
# Usage: ./launch_all.sh [--secure]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
  echo
  echo "Shutting down Digital Operating Room..."
  if [[ -n "${DEMO_PID:-}" ]] && kill -0 "$DEMO_PID" 2>/dev/null; then
    kill "$DEMO_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "Starting Digital Operating Room demo in the background..."
"$SCRIPT_DIR/run_digital_or.sh" "${1:-}" &
DEMO_PID=$!

echo "Starting Tutorial GUI..."
cd "$SCRIPT_DIR"
if ! python3 -c "import PySide6" 2>/dev/null; then
  echo "PySide6 not found, installing..."
  pip install -q PySide6
fi
python3 tutorial_gui.py

# When the Tutorial GUI window is closed, fall through to cleanup via the trap.
wait "$DEMO_PID" 2>/dev/null || true
