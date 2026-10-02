#!/usr/bin/env bash
# Sets up, builds, and launches the Digital Operating Room demo (Module 01) from the
# medtech-reference-architecture repo, for local demos ahead of any cloud eval integration.
#
# Usage: ./run_digital_or.sh [--secure] [--web] [--setup-only|--launch-only]
#
# Requires: RTI Connext Professional 7.7 installed and licensed locally.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/../medtech-reference-architecture"
mode=all
launch_args=()
for arg in "$@"; do
  case "$arg" in
    --setup-only) mode=setup ;;
    --launch-only) mode=launch ;;
    --secure) launch_args+=(--security) ;;
    *) launch_args+=("$arg") ;;
  esac
done

if [[ ! -f "$REPO_DIR/launch.py" ]]; then
  echo "error: $REPO_DIR is missing. Run ./tutorial/launch_all.sh to initialize the submodule." >&2
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
venv_dir="${MEDTECH_VENV:-$REPO_DIR/.venv}"

if [[ "$mode" != launch ]]; then
  if [[ ! -d "$venv_dir" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv "$venv_dir"
  fi
fi
if [[ ! -f "$venv_dir/bin/activate" ]]; then
  echo "error: virtual environment missing; run setup first." >&2
  exit 1
fi
# shellcheck disable=SC1091
source "$venv_dir/bin/activate"

if [[ "$mode" != launch ]]; then
  echo "Installing Python dependencies..."
  if [[ "${MEDTECH_CLOUD:-0}" == 1 ]]; then
    python3 -c 'import rti.connextdds, argcomplete, stun, requests' || {
      echo "error: cloud Python dependencies missing; rebuild the cloud image." >&2
      exit 1
    }
  else
    python3 -m pip install -q -r requirements.txt
    python3 -m pip install -q rti.connext.activated -f "$NDDSHOME/resource/python_api"
  fi

  echo "Building (C++ targets + Python type support)..."
  python3 build.py
fi

if [[ "$mode" == setup ]]; then
  exit 0
fi
echo "Launching Digital Operating Room..."
exec python3 launch.py 01-operating-room "${launch_args[@]}"
