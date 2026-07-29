# Integration Notes: Digital Operating Room → Cloud Eval

Open items to resolve before this tutorial can become a real `evaluation.rti.com` workspace
template, based on what was verified while building this draft.

## 1. GUI applications need a display in the browser sandbox

Existing cloud eval templates (Publish-Subscribe, RPC, Last-Value Cache, Content Filtering,
Sandbox) are all **console-only** Python scripts run in the IDE's integrated terminal — no
GUI. The Digital Operating Room's 5 applications open **native GUI windows** (Tkinter/PyQt
plots for Patient Monitor and Arm; GTK windows for Arm Controller and Orchestrator).

Decision (per stakeholder): keep the real GUI apps rather than building a simplified
console-only variant. For the cloud sandbox, this means the workspace container will need a
VNC/noVNC (or similar browser-embeddable X server) setup so these windows are visible/clickable
in-browser — this is new infrastructure relative to the existing templates and should be
scoped as its own platform work item.

## 2. Full licensed Connext install + native build, not just `pip install rti.connext`

The existing templates only need `pip install rti.connext` (a pure Python wheel) — no license
file, no C++ build. The Digital Operating Room requires:

- RTI Connext Professional 7.7 installed with `NDDSHOME` set (license-gated).
- A C++ toolchain (CMake ≥ 3.17, a C++17 compiler) and `gtkmm-3.0` (for ArmController/Orchestrator).
- A one-time `python3 build.py` (generates both C++ binaries **and** the Python `Types.py`
  bindings used by `Arm.py`/`PatientMonitor.py` — running it with `--target module-01`
  builds only the C++ side and **skips** the Python codegen target `refArchTypesPy`,
  which breaks `Arm.py`/`PatientMonitor.py` with `ModuleNotFoundError: No module named 'Types'`.
  Always run the full `python3 build.py` at least once.)

Any cloud sandbox image for this workspace needs Connext 7.7 pre-installed/pre-licensed and
the build dependencies baked in (or a pre-built `build/` output committed/cached), since asking
a healthcare prospect to compile C++ mid-tutorial would break the "seconds to get started"
promise of the existing cloud eval templates.

## 3. Confirmed working locally (macOS, arm64)

```bash
source /Applications/rti_connext_dds-7.7.0/resource/scripts/rtisetenv_arm64Darwin23clang16.0.zsh
cd medtech-reference-architecture
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install rti.connext.activated -f $NDDSHOME/resource/python_api
python3 build.py
python3 launch.py 01-operating-room
```

All 5 applications (PatientSensor, PatientMonitor, Arm, ArmController, Orchestrator) started
cleanly with no errors after the full build.

## 4. Recommendation for a phased rollout

1. **Now:** use `run_digital_or.sh` for local, in-person/screen-share demos to stakeholders.
2. **Next:** platform team evaluates VNC/noVNC feasibility in the existing workspace container
   image, and decides whether to pre-bake a licensed, pre-built Connext 7.7 image for this
   template (recommended) vs. requiring per-session build.
3. **Then:** wire `digital-or-tutorial.json`'s 10 steps into "Connext Studio" as a new
   workspace template, reusing the existing "open file" / "run in named terminal" /
   "Visualize System" / "Create View with AI" actions already built for Publish-Subscribe.
