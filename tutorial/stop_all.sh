#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 - "$SCRIPT_DIR/.." <<'PY'
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import uuid

root = Path(sys.argv[1]).resolve()
repo = root / "medtech-reference-architecture"
scripts = {
    root / "tutorial" / "launch_all.sh",
    root / "tutorial" / "run_digital_or.sh",
    root / "tutorial" / "tutorial_gui.py",
    repo / "modules" / "01-operating-room" / "src" / "Arm.py",
    repo / "modules" / "01-operating-room" / "src" / "PatientMonitor.py",
}


def targets():
    result = {}
    listing = subprocess.run(
        ["ps", "-u", str(os.getuid()), "-o", "pid=,args="],
        check=True, capture_output=True, text=True,
    )
    for row in listing.stdout.splitlines():
        fields = row.strip().split(None, 1)
        if len(fields) != 2:
            continue
        pid = int(fields[0])
        if pid in (os.getpid(), os.getppid()):
            continue
        try:
            if sys.platform.startswith("linux"):
                arguments = [os.fsdecode(value) for value in Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0") if value]
            else:
                arguments = shlex.split(fields[1])
            if not arguments:
                continue
            executable = Path(arguments[0]).name
            if re.fullmatch(r"python[\d.]*|bash|zsh|sh", executable, re.IGNORECASE):
                arguments = arguments[1:]
                while arguments and arguments[0] in ("-u", "-B", "-E", "-I", "-s"):
                    arguments = arguments[1:]
            if not arguments or arguments[0].startswith("-"):
                continue
            candidate = Path(arguments[0])
            if candidate.name not in ("launch_all.sh", "run_digital_or.sh", "tutorial_gui.py", "launch.py", "Arm.py", "PatientMonitor.py", "ArmController", "Orchestrator", "PatientSensor"):
                continue
            if not candidate.is_absolute():
                if sys.platform.startswith("linux"):
                    cwd = Path(os.readlink(f"/proc/{pid}/cwd"))
                else:
                    listing = subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"], capture_output=True, text=True, check=True)
                    cwd = Path(next(line[1:] for line in listing.stdout.splitlines() if line.startswith("n")))
                candidate = cwd / candidate
            candidate = candidate.resolve()
            is_launcher = candidate == repo / "launch.py" and "01-operating-room" in arguments[1:]
            is_binary = (
                candidate.is_relative_to(repo / "build")
                and candidate.parent.name == "01-operating-room"
                and candidate.name in ("ArmController", "Orchestrator", "PatientSensor")
            )
            if candidate in scripts or is_launcher or is_binary:
                result[pid] = candidate.name
        except (OSError, ValueError, StopIteration, subprocess.CalledProcessError):
            continue
    return result


def stop(pids, requested_signal):
    for pid in pids:
        try:
            os.kill(pid, requested_signal)
        except ProcessLookupError:
            pass


selected = targets()
stop(selected, signal.SIGTERM)
deadline = time.monotonic() + 3
remaining = set(selected)
while remaining and time.monotonic() < deadline:
    remaining.intersection_update(targets())
    if remaining:
        time.sleep(0.1)
stop(remaining, signal.SIGKILL)

if Path("/app/code-server").is_dir():
    requests = Path(tempfile.gettempdir()) / f"medtech-web-tabs-{os.getuid()}" / "requests"
    requests.mkdir(parents=True, exist_ok=True)
    request = requests / f"{time.time_ns()}-{uuid.uuid4().hex}.json"
    pending = request.with_suffix(".tmp")
    pending.write_text(json.dumps({"uri": "vscode://rti.medtech-web-tabs/close"}))
    pending.replace(request)

print(f"Stopped {len(selected)} Digital Operating Room process(es)." if selected else "No Digital Operating Room processes running.")
PY