# Digital Operating Room Cloud Eval Handoff

This repo contains the guided Digital Operating Room tutorial and a pinned checkout of the [MedTech Reference Architecture](https://github.com/rticommunity/rticonnextdds-medtech-reference-architecture) with VS Code web tabs. The parent repository pins commit `4050cd3beba407a8cdef3ae65c0f04d995be7a25` from the `web-based-tutorial-apps` branch; use the pinned commit, not the branch tip.

## Cloud Image And Recovery

The version-controlled [cloud image runbook](docker/README_cloud_eval_image.md)
contains the Dockerfile, pinned Python requirements, recorded image/archive
identities, port-8080 clean-install procedure, acceptance checks, and image plus
workspace-volume backup/restore commands. Use `docker/` as the canonical image
recipe, not the historical sibling directory. Licensed archives and volume
backups must be kept in authorized external storage; they are not included in Git.
The cloud tutorial uses a native VS Code side panel and four live editor-grid UIs,
without a desktop tutorial window or noVNC display. The dependency discussion
below includes the separate local-desktop workflow and packaging proposals.

## Dependencies

There are two different dependency sets: **building from source** and **running prebuilt applications**. The current local launcher does both. A Cloud Eval runtime image does not need to contain the compiler, CMake, development headers, or the complete Connext SDK if compatible applications and generated Python types are supplied ahead of time. It still needs the native and Python runtime libraries below.

### Build And Setup Dependencies

These belong on a developer machine or in a CI/builder image, not necessarily in the user workspace:

- Git (access to this Bitbucket repo and the public GitHub MedTech submodule), Bash, and network access to PyPI and npm for the first run.
- Licensed RTI Connext DDS Professional 7.7.0, including its C++ libraries, build tools, and the `rti.connext.activated` Python wheel under `$NDDSHOME/resource/python_api`. Set `NDDSHOME` and source the matching `rtisetenv_<arch>` script; the launcher auto-detects `/Applications/rti_connext_dds-7.7.0` on macOS. The script cannot download or license Connext.
- Python 3.10+ with `pip` and `venv`; CMake 3.17+; a C++17 compiler; `pkg-config`; and the `gtkmm-3.0` development libraries for Arm Controller and Orchestrator.
- For packaging the bundled VS Code extension: Node.js with `npx` (which downloads `@vscode/vsce`). A prepackaged VSIX avoids this setup dependency in the user workspace.

On Ubuntu/Debian, install the system build packages with `sudo apt install build-essential cmake pkg-config libgtkmm-3.0-dev python3-venv`; install Python, Git, Node.js, and VS Code separately if absent. On macOS, install the Xcode command-line tools and use `brew install cmake pkg-config gtkmm3 python3 git node`; install VS Code separately.

### Runtime Dependencies

These remain necessary with the current application code, even if the C++ applications are precompiled:

- Python 3.10+ and the installed Python packages listed below, including the Connext 7.7.0 Python API. `pip` and `venv` are provisioning tools, not application requirements once the environment is prepared.
- The Connext C++ shared libraries used by the binaries, compatible OS/C++ runtime libraries, and the required runtime licensing configuration. Precompilation does not remove licensing requirements; a runtime-only Connext layout and redistribution rights must be validated with RTI.
- GTK/gtkmm runtime libraries for Arm Controller and Orchestrator, **including in web mode**: the current binaries still link them. Development headers are not needed at runtime.
- PySide6/Qt, NumPy, and pyqtgraph, **including in web mode**: the current Python applications import them even when serving browser UIs. Removing them would require code changes, not just precompilation.
- A graphical display for the separate PySide6 tutorial window (X11/Wayland or a browser-accessible remote display). The application web UIs do not need native windows. Integrating the tutorial JSON into the hosted Connext Studio panel could avoid the tutorial display requirement, but that integration is not implemented.
- For the default local VS Code tab mode: VS Code 1.100+ with the `code` CLI and the bundled extension. On macOS, the launcher also detects the CLI in the standard VS Code app bundle. `--web` and `--native` do not need VS Code or Node.js. Hosted extension loading, port forwarding, and tab opening still require platform validation; desktop CLI/URI handling is not a hosted integration.

The launcher creates a virtual environment and installs the MedTech Python requirements: `argcomplete>=3.1`, `numpy>=1.24`, `pyqtgraph>=0.13`, `PySide6>=6.5` (also used by the tutorial GUI), `pystun3>=2.0`, and `requests>=2.31`. It installs `rti.connext.activated` from the local Connext installation separately. Python transitive dependencies are resolved by `pip`.

### Dependency Sizes

The following are **installed disk footprints**, not RAM use or compressed download sizes. Measurements were taken with `du -sh` on the working macOS arm64 installation on 2026-09-30 (Python 3.14); they are reference points, **not Linux Cloud Eval image measurements**. MiB/GiB values are rounded. Rows explicitly marked as budgets are rough Linux planning allowances, not measured package sizes. Versions, architecture, shared dependencies, and existing base-image contents change the incremental cost.

| Dependency | Build/setup | Prebuilt runtime | Installed size reference |
| --- | --- | --- | --- |
| Git | Clone and CMake FetchContent | Not needed if files are bundled; still needed by `launch_all.sh` | 20-60 MiB budget with dependencies; zero added if already present |
| Bash | Setup scripts | Needed by the shell launch scripts | 1-5 MiB budget; zero added if already present |
| C++17 compiler/toolchain | Required | Not needed; retain OS/C++ runtime libraries | 1.3 GiB measured for macOS command-line tools; Linux builder budget 250-600 MiB |
| CMake >=3.17 | Required | Not needed | 74 MiB measured |
| `pkg-config` | GTK build discovery | Not needed | 0.6 MiB measured (`pkgconf`) |
| Connext Professional 7.7.0 SDK | Required, including code generator | Full SDK not intrinsically needed | 2.7 GiB measured for the complete local installation |
| Connext C++ libraries | Link libraries | Required shared-library subset | 690 MiB measured for the entire local architecture library directory, **not** a minimal runtime; subset size TBD after dependency audit |
| Connext Python API | Install for Python apps | Required | 34 MiB measured installed `rti` package; bundled wheel directory is 47 MiB and need not ship in runtime |
| Python >=3.10 | Build scripts and environment setup | Required | 88 MiB measured Homebrew Python package, excluding external shared libraries |
| GTK/gtkmm | Development headers and libraries | Runtime libraries required | 11 MiB measured `gtkmm3` alone; reserve 100-300 MiB for a Linux runtime dependency closure pending measurement; development packages add more |
| PySide6/Qt + shiboken6 | Install into environment | Required by current code | 1.1 GiB + 1.4 MiB measured, excluding external OS libraries |
| NumPy | Install into environment | Required | 34 MiB measured |
| pyqtgraph | Install into environment | Required by current imports | 9.1 MiB measured, excluding NumPy/Qt already listed |
| argcomplete | Install into environment | Keep for current launcher | 0.25 MiB measured |
| pystun3 | Install into environment | Keep for current launcher | 0.03 MiB measured `stun` package |
| requests | Install into environment | Keep for current launcher | 0.57 MiB measured, excluding transitive dependencies |
| Node.js/npm/npx | VSIX packaging | Not needed for the packaged extension itself | 79 MiB measured Node package; `vsce` downloads/cache extra |
| VS Code | Local extension installation/use | Only for VS Code tab experience | 1.4 GiB measured desktop app; hosted IDE already supplied by platform, whose incremental cost must be measured separately |
| MedTech Web Tabs VSIX | Build once | Install if using VS Code tabs | 12 KiB measured |
| Display/remote desktop stack | Not needed to compile | Needed if retaining the tutorial desktop window | 100-300 MiB Linux budget for Xvfb/VNC/noVNC and dependencies; not installed/measured here, browser excluded |

The complete local Python virtual environment is **1.3 GiB**, and the current all-module build directory is **20 MiB** (includes build intermediates, not just deliverable binaries). These overlap the table entries: do not add them again. The SDK contains the C++ library and wheel directories, and many system libraries are shared. A deployment also needs application source/assets, generated `Types.py`, and XML configuration. A Linux runtime image total cannot be inferred by summing these Mac measurements.

### Cloud Eval Packaging And Startup

The concern about expanding the optimized base workspace image is valid: the current setup is not a lightweight additional workspace. Precompilation removes build tooling and per-session compilation, but **does not make the existing GUI dependencies disappear**.

Recommended candidate: build in CI using a multi-stage container build, then copy the Linux/architecture-compatible Module 01 binaries, generated Python types, source/assets/configuration, installed Python environment, audited shared-library closure, and packaged VSIX into a versioned runtime image. Keep the compiler, SDK build tools, headers, package caches, and unrelated modules in the builder stage. Build and runtime must match the target OS, CPU architecture, ABI, Python version, and Connext version; the local Mac binaries are not Linux deliverables.

Two deployment options need platform-team agreement:

- **Dedicated runtime workspace image:** simplest co-location of apps and IDE, but still a second image to maintain, patch, distribute, and prewarm. It requires platform support and is not just a new workspace definition.
- **Application container alongside the existing workspace:** could keep build/GUI packages out of the base IDE image, but shifts their size into another image rather than eliminating it. Requires supported container orchestration, browser port routing for 8090-8093, DDS networking/discovery configuration, licensing, and process lifecycle management. Do not assume users can start Docker inside the workspace or that DDS discovery works across container networks by default.

Neither option is supplied by this repository today. `launch_all.sh` still updates the submodule, packages/installs the extension, installs Python packages, and runs the build. For a provisioned environment, `./tutorial/run_digital_or.sh --launch-only --web` skips those setup/build steps and launches the demo only, not the tutorial GUI; it still expects `.venv`, `NDDSHOME`, compatible binaries, generated types, configuration, and runtime libraries in the current layout. A runtime-only image needs a validated entrypoint and layout rather than invoking `launch_all.sh` unchanged.

Before committing to either option, measure on the actual Linux base image: dependency-by-dependency incremental installed size, compressed registry layers to pull, uncompressed image size, and cold versus warm time to the first usable tutorial and all four responsive web UIs. Compare against the base workspace and separate image pull/unpack, provisioning, and application startup. Preinstalling removes session downloads/builds; larger uncached layers can still increase cold startup significantly. Reusing cached base layers and prewarming may help, but no startup-time claim is established yet. Pin the final Python/system dependencies and image digest so size, startup, and maintenance costs are reproducible.

## Run locally

```bash
git clone --recurse-submodules ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git
cd cloud_eval_medical
./tutorial/launch_all.sh
```

The single launch command also works after a plain `git clone`: it initializes the MedTech submodule at the pinned commit if missing, installs the bundled VS Code extension, creates a virtual environment, installs the Python requirements and Connext Python wheel, builds the C++ apps and Python types, and launches the Digital OR applications in VS Code tabs alongside the guided tutorial GUI. The submodule checkout is never advanced to the latest branch tip. Existing tracked changes in a checkout at another commit block the update rather than being discarded.

Use `./tutorial/launch_all.sh --web` to open the applications in browser tabs without the VS Code extension, or `--native` for native application windows. Add `--secure` only after generating the security artifacts described in the MedTech README. Close the tutorial GUI or press Ctrl+C in the launch terminal to stop the demo. Direct demo-only startup remains available with `./tutorial/run_digital_or.sh --vscode` after the submodule is initialized.

## Verify a clean clone

From a fresh clone, run the command above. Check that `git submodule status` reports `4050cd3beba407a8cdef3ae65c0f04d995be7a25` without a leading `-` or `+`, and that the demo starts with four web UI tabs (Arm Controller, Surgical Arm Monitor, Orchestrator, Patient Monitor), a PatientSensor process, and a tutorial window showing ten steps. The first run downloads dependencies and builds binaries, so allow time for it. Re-run `./tutorial/launch_all.sh` to verify the already-present submodule path. For an intentionally incomplete clone, omit `--recurse-submodules` and run the same launch command to verify auto-initialization.

The tutorial's [content and local usage](tutorial/README.md), [cloud integration constraints](tutorial/INTEGRATION_NOTES.md), and [web extension details](medtech-reference-architecture/vscode-extension/README.md) are documented separately. The integration notes describe the current source-build workflow; the prebuilt packaging options above are proposals, not implemented deployment paths. A cloud workspace needs licensed Connext runtime support, the application's runtime dependencies, a display if retaining the PySide6 tutorial GUI, and hosted UI integration. Native build dependencies are needed only if building there. This script prepares a local or suitably provisioned workspace, not a hosted evaluation template.
