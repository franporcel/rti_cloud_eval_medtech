#!/usr/bin/env bash
# Sets up, builds, and launches the Digital Operating Room demo (Module 01) from the
# medtech-reference-architecture repo, for local demos ahead of any cloud eval integration.
#
# Usage: ./run_digital_or.sh [--secure]
#
# Requires: RTI Connext Professional 7.7 installed and licensed locally.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/../medtech-reference-architecture"

if [[ ! -d "$REPO_DIR" ]]; then
  echo "error: $REPO_DIR not found. Clone rticonnextdds-medtech-reference-architecture there first." >&2
  exit 1
fi

if [[ -z "${NDDSHOME:-}" ]]; then
  echo "NDDSHOME is not set. Trying to auto-detect a local Connext 7.7 install..."
  CANDIDATE=$(ls -d /Applications/rti_connext_dds-7.7.0 2>/dev/null | head -1 || true)
  if [[ -z "$CANDIDATE" ]]; then
    echo "error: could not find a Connext install. Set NDDSHOME and source rtisetenv_<arch> first." >&2
    exit 1
  fi
  SETENV=$(ls "$CANDIDATE"/resource/scripts/rtisetenv_*.bash 2>/dev/null | head -1 || true)
  if [[ -z "$SETENV" ]]; then
    echo "error: could not find an rtisetenv_<arch> script under $CANDIDATE/resource/scripts." >&2
    exit 1
  fi
  echo "Sourcing $SETENV"
  set +u
  # shellcheck disable=SC1090
  source "$SETENV"
  set -u
fi

cd "$REPO_DIR"

if [[ ! -d .venv ]]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt
pip install -q rti.connext.activated -f "$NDDSHOME/resource/python_api"

echo "Building (C++ targets + Python type support)..."
python3 build.py

echo "Launching Digital Operating Room..."
if [[ "${1:-}" == "--secure" ]]; then
  python3 launch.py 01-operating-room -s
else
  python3 launch.py 01-operating-room
fi
