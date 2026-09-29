#!/usr/bin/env bash
# Launches the Digital Operating Room demo and the guided Tutorial GUI together.
#
# Usage: ./launch_all.sh [--secure] [--web|--native] (VS Code tabs by default)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$ROOT_DIR/medtech-reference-architecture"
launch_args=(--vscode)
for arg in "$@"; do
  case "$arg" in
    --secure) launch_args+=(--secure) ;;
    --web) launch_args=(--web "${launch_args[@]:1}") ;;
    --native) launch_args=("${launch_args[@]:1}") ;;
    *) echo "error: unknown option $arg" >&2; exit 2 ;;
  esac
done

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

if [[ "${launch_args[0]:-}" == --vscode ]]; then
  if command -v code >/dev/null 2>&1; then
    code_cli=$(command -v code)
  elif [[ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]]; then
    code_cli="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
  else
    echo "error: VS Code CLI not found; install it or run with --web/--native." >&2
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
source "$REPO_DIR/.venv/bin/activate"

cleanup() {
  echo
  echo "Shutting down Digital Operating Room..."
  if [[ -n "${DEMO_PID:-}" ]] && kill -0 "$DEMO_PID" 2>/dev/null; then
    pkill -TERM -P "$DEMO_PID" 2>/dev/null || kill "$DEMO_PID" 2>/dev/null || true
    wait "$DEMO_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

echo "Starting Digital Operating Room demo in the background..."
"$SCRIPT_DIR/run_digital_or.sh" --launch-only "${launch_args[@]}" &
DEMO_PID=$!

echo "Starting Tutorial GUI..."
cd "$SCRIPT_DIR"
python3 tutorial_gui.py

# When the Tutorial GUI window is closed, fall through to cleanup via the trap.
wait "$DEMO_PID" 2>/dev/null || true
