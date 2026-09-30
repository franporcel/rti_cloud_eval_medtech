# Integration Notes: Digital Operating Room → Cloud Eval

Open items to resolve before this locally working demo can become a real `evaluation.rti.com`
workspace template. The web-tab experience has been verified in local desktop VS Code on macOS,
not in the hosted browser-based workspace.

## 1. Validate web tabs and tutorial UI in the browser sandbox

Existing cloud eval templates (Publish-Subscribe, RPC, Last-Value Cache, Content Filtering,
Sandbox) are all **console-only** Python scripts run in the IDE's integrated terminal — no
GUI. The default local Digital Operating Room launch uses four HTTP web UIs (Patient Monitor,
Arm, Arm Controller, Orchestrator) in VS Code web tabs, plus a headless Patient Sensor. Native
windows remain an optional `--native` mode.

The bundled MedTech Web Tabs extension opens `localhost` HTTP pages inside a VS Code webview;
the local launcher dispatches `vscode://` URIs to desktop VS Code. Check whether the hosted
extension host can load this extension, forward each of ports 8090–8093 into the webview, and
open the four tabs without desktop URI handling. The guided `tutorial_gui.py` is a separate
PySide6 desktop window: either integrate the JSON steps into the hosted Connext Studio panel
or provide a browser-accessible display for that window. Neither route has been validated
in the hosted workspace.

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
git clone --recurse-submodules ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git
cd cloud_eval_medical
./tutorial/launch_all.sh
```

The launcher detects the local Connext 7.7 install, builds the project, and starts all five
applications: four VS Code web tabs and a headless Patient Sensor, alongside the tutorial GUI.
This local result does not establish hosted template compatibility.

## 4. Recommendation for a phased rollout

1. **Now:** use `./tutorial/launch_all.sh` for local, in-person/screen-share demos to stakeholders.
2. **Next:** validate webview port forwarding, extension installation, and tab opening in the
   hosted workspace; decide how to present the tutorial steps there. Pre-bake a licensed,
   pre-built Connext 7.7 image or measure whether per-session builds are acceptable.
3. **Then:** wire `digital-or-tutorial.json`'s 10 steps into "Connext Studio" as a new
   workspace template, reusing the existing "open file" / "Visualize System" /
   "Create View with AI" actions already built for Publish-Subscribe.
