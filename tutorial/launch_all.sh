#!/usr/bin/env bash
# Launches the Digital Operating Room web apps.
#
# Usage: ./launch_all.sh [--secure] [--cloud|--web] (cloud by default)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$ROOT_DIR/medtech-reference-architecture"
launch_args=(--web)
cloud_mode=1
for arg in "$@"; do
  case "$arg" in
    --secure) launch_args+=(--secure) ;;
    --web) cloud_mode=0 ;;
    --native)
      echo "error: native device GUIs were removed; use --web or --cloud." >&2
      exit 2
      ;;
    --cloud) cloud_mode=1 ;;
    *) echo "error: unknown option $arg" >&2; exit 2 ;;
  esac
done
export MEDTECH_CLOUD="$cloud_mode"

python3 - <<'PY'
import socket

busy = []
ports = [("Orchestrator", 8090), ("Arm Controller", 8091),
     ("Arm", 8092), ("Patient Monitor", 8093)]
for name, port in ports:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            busy.append(f"{name} ({port})")
    except OSError:
        pass

if busy:
    raise SystemExit("error: demo ports already in use: " + ", ".join(busy)
                     + ". Stop the existing demo before launching another one.")
PY

expected_commit=$(git -C "$ROOT_DIR" rev-parse :medtech-reference-architecture)
if [[ -e "$REPO_DIR/.git" ]]; then
  current_commit=$(git -C "$REPO_DIR" rev-parse HEAD)
  if [[ "$current_commit" != "$expected_commit" ]] &&
     { ! git -C "$REPO_DIR" diff --quiet || ! git -C "$REPO_DIR" diff --cached --quiet; }; then
    echo "error: nested repo has local changes; cannot switch to pinned commit $expected_commit" >&2
    exit 1
  fi
fi
echo "Initializing MedTech at $expected_commit..."
git -C "$ROOT_DIR" submodule update --init --recursive -- medtech-reference-architecture

"$SCRIPT_DIR/run_digital_or.sh" --setup-only
source "${MEDTECH_VENV:-$REPO_DIR/.venv}/bin/activate"

echo "Tutorial: $SCRIPT_DIR/TUTORIAL.md"
if [[ "$cloud_mode" == 1 ]]; then
  cloud_url="${MEDTECH_CLOUD_URL:-http://127.0.0.1:8080}"
  echo "Orchestrator: ${cloud_url%/}/proxy/8090/"
  echo "Arm Controller: ${cloud_url%/}/proxy/8091/"
  echo "Arm: ${cloud_url%/}/proxy/8092/"
  echo "Patient Monitor: ${cloud_url%/}/proxy/8093/"
fi

echo "Starting Digital Operating Room demo in the background..."
DEMO_LOG=$(mktemp "${TMPDIR:-/tmp}/medtech-digital-or.XXXXXX")
nohup "$SCRIPT_DIR/run_digital_or.sh" --launch-only "${launch_args[@]}" >"$DEMO_LOG" 2>&1 </dev/null &
DEMO_PID=$!
disown "$DEMO_PID"

echo "Demo supervisor PID: $DEMO_PID"
echo "Demo log: $DEMO_LOG"
echo "Stop: $SCRIPT_DIR/stop_all.sh"
echo "Restart: $SCRIPT_DIR/restart_all.sh"
