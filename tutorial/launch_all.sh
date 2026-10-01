#!/usr/bin/env bash
# Launches the Digital Operating Room web apps and the VS Code tutorial sidebar.
#
# Usage: ./launch_all.sh [--secure] [--web|--cloud] (VS Code tabs by default)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$ROOT_DIR/medtech-reference-architecture"
launch_args=(--vscode)
ui_mode=--vscode
cloud_mode=0
if [[ -d /app/code-server && -z "${DISPLAY:-}" ]]; then
  cloud_mode=1
fi
export MEDTECH_SECURITY=0
for arg in "$@"; do
  case "$arg" in
    --secure) launch_args+=(--secure); export MEDTECH_SECURITY=1 ;;
    --web) launch_args=(--web "${launch_args[@]:1}"); ui_mode=--web; cloud_mode=0 ;;
    --native)
      echo "error: native device GUIs were removed; use VS Code tabs, --web, or --cloud." >&2
      exit 2
      ;;
    --cloud) launch_args=(--vscode "${launch_args[@]:1}"); ui_mode=--vscode; cloud_mode=1 ;;
    *) echo "error: unknown option $arg" >&2; exit 2 ;;
  esac
done
export MEDTECH_UI_MODE="$ui_mode"

if [[ "$cloud_mode" == 1 ]]; then
  export MEDTECH_CLOUD=1
fi

if [[ "$ui_mode" != --native ]]; then
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
fi

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

if [[ "$cloud_mode" == 1 ]]; then
  extension_dir="${MEDTECH_CODE_SERVER_EXTENSIONS:-/config/extensions}/rti.medtech-web-tabs-0.1.0"
  mkdir -p "$extension_dir"
  for file in package.json extension.js tutorial-view.js tutorial.svg; do
    cp "$REPO_DIR/vscode-extension/$file" "$extension_dir/$file"
  done
  echo "MedTech tutorial extension installed. Reload the browser IDE once if its Tutorial view is not visible."
elif [[ "${launch_args[0]:-}" == --vscode ]]; then
  if command -v code >/dev/null 2>&1; then
    code_cli=$(command -v code)
  elif [[ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
    code_cli="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
  else
    echo "error: VS Code CLI not found; install it or run with --web." >&2
    exit 1
  fi
  if ! command -v npx >/dev/null 2>&1; then
    echo "error: Node.js/npx is required to package the VS Code extension." >&2
    exit 1
  fi
  echo "Installing MedTech VS Code extension..."
  (cd "$REPO_DIR/vscode-extension" && npx --yes @vscode/vsce package --allow-missing-repository --skip-license &&
    "$code_cli" --install-extension "$(pwd)/medtech-web-tabs-0.1.0.vsix" --force)
fi

"$SCRIPT_DIR/run_digital_or.sh" --setup-only
source "${MEDTECH_VENV:-$REPO_DIR/.venv}/bin/activate"

if [[ "$cloud_mode" != 1 && "${launch_args[0]:-}" == --vscode ]]; then
  "$code_cli" "$ROOT_DIR"
fi

cleanup() {
  echo
  echo "Shutting down Digital Operating Room..."
  if [[ -n "${DEMO_PID:-}" ]] && kill -0 "$DEMO_PID" 2>/dev/null; then
    pkill -TERM -P "$DEMO_PID" 2>/dev/null || kill "$DEMO_PID" 2>/dev/null || true
    wait "$DEMO_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ "$ui_mode" == --vscode ]]; then
  (cd "$REPO_DIR" && python3 -c 'import os; from launch import _open_vscode_uri; _open_vscode_uri("vscode://rti.medtech-web-tabs/tutorial?secure=" + os.environ["MEDTECH_SECURITY"])')
  echo "Opening the Tutorial side panel and four device tabs in VS Code."
fi

echo "Starting Digital Operating Room demo in the background..."
"$SCRIPT_DIR/run_digital_or.sh" --launch-only "${launch_args[@]}" &
DEMO_PID=$!

wait "$DEMO_PID"
