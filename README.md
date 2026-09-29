# Digital Operating Room Cloud Eval Handoff

This repo contains the guided Digital Operating Room tutorial and a pinned checkout of the [MedTech Reference Architecture](https://github.com/rticommunity/rticonnextdds-medtech-reference-architecture) with VS Code web tabs. The parent repository pins commit `695a897c8f8507141f6ab36b650504f4e569a9ce` from the `web-based-tutorial-apps` branch; use the pinned commit, not the branch tip.

## Dependencies

Install these on the host or bake them into the cloud eval image before running:

- Git (access to this Bitbucket repo and the public GitHub MedTech submodule), Bash, and network access to PyPI and npm for the first run.
- Licensed RTI Connext DDS Professional 7.7.0, including its C++ libraries, build tools, and the `rti.connext.activated` Python wheel under `$NDDSHOME/resource/python_api`. Set `NDDSHOME` and source the matching `rtisetenv_<arch>` script; the launcher auto-detects `/Applications/rti_connext_dds-7.7.0` on macOS. The script cannot download or license Connext.
- Python 3.10+ with `pip` and `venv`; CMake 3.17+; a C++17 compiler; `pkg-config`; and the `gtkmm-3.0` development libraries for Arm Controller and Orchestrator.
- A graphical display for the PySide6 tutorial window (X11/Wayland or a browser-accessible display in a hosted workspace).
- For the default VS Code tab mode: VS Code 1.100+ with the `code` CLI and Node.js with `npx` (which downloads `@vscode/vsce` to package the bundled extension). On macOS, the launcher also detects the CLI in the standard VS Code app bundle. `--web` and `--native` do not need VS Code or Node.js.

On Ubuntu/Debian, install the system build packages with `sudo apt install build-essential cmake pkg-config libgtkmm-3.0-dev python3-venv`; install Python, Git, Node.js, and VS Code separately if absent. On macOS, install the Xcode command-line tools and use `brew install cmake pkg-config gtkmm3 python3 git node`; install VS Code separately.

The launcher creates a virtual environment and installs the MedTech Python requirements: `argcomplete>=3.1`, `numpy>=1.24`, `pyqtgraph>=0.13`, `PySide6>=6.5` (also used by the tutorial GUI), `pystun3>=2.0`, and `requests>=2.31`. It installs `rti.connext.activated` from the local Connext installation separately. Python transitive dependencies are resolved by `pip`.

## Run locally

```bash
git clone --recurse-submodules ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git
cd cloud_eval_medical
./tutorial/launch_all.sh
```

The single launch command also works after a plain `git clone`: it initializes the MedTech submodule at the pinned commit if missing, installs the bundled VS Code extension, creates a virtual environment, installs the Python requirements and Connext Python wheel, builds the C++ apps and Python types, and launches the Digital OR applications in VS Code tabs alongside the guided tutorial GUI. The submodule checkout is never advanced to the latest branch tip. Existing tracked changes in a checkout at another commit block the update rather than being discarded.

Use `./tutorial/launch_all.sh --web` to open the applications in browser tabs without the VS Code extension, or `--native` for native application windows. Add `--secure` only after generating the security artifacts described in the MedTech README. Close the tutorial GUI or press Ctrl+C in the launch terminal to stop the demo. Direct demo-only startup remains available with `./tutorial/run_digital_or.sh --vscode` after the submodule is initialized.

## Verify a clean clone

From a fresh clone, run the command above. Check that `git submodule status` reports `695a897c8f8507141f6ab36b650504f4e569a9ce` without a leading `-` or `+`, and that the demo starts with four web UI tabs (Arm Controller, Surgical Arm Monitor, Orchestrator, Patient Monitor), a PatientSensor process, and a tutorial window showing ten steps. The first run downloads dependencies and builds binaries, so allow time for it. Re-run `./tutorial/launch_all.sh` to verify the already-present submodule path. For an intentionally incomplete clone, omit `--recurse-submodules` and run the same launch command to verify auto-initialization.

The tutorial's [content and local usage](tutorial/README.md), [cloud integration constraints](tutorial/INTEGRATION_NOTES.md), and [web extension details](medtech-reference-architecture/vscode-extension/README.md) are documented separately. A cloud workspace still needs a licensed Connext image, native build dependencies, a display for the PySide6 tutorial GUI, and a compatible VS Code extension host; this script prepares a local or suitably provisioned workspace, not a hosted evaluation template.
