# Digital Operating Room Cloud Eval Handoff

This repo contains the [Digital Operating Room tutorial](tutorial/TUTORIAL.md) and a pinned checkout of the [MedTech Reference Architecture](https://github.com/rticommunity/rticonnextdds-medtech-reference-architecture) with browser-based device UIs. Use the pinned submodule commit, not the branch tip.

## Cloud Image And Recovery

The version-controlled [cloud image runbook](docker/README_cloud_eval_image.md)
contains the Dockerfile, pinned Python requirements, recorded image/archive
identities, port-8080 clean-install procedure, acceptance checks, and image plus
workspace-volume backup/restore commands. Use `docker/` as the canonical image
recipe, not the historical sibling directory. Licensed archives and volume
backups must be kept in authorized external storage; they are not included in Git.
The tutorial is a Markdown file, and the four device UIs run in a 2x2 editor grid
using the bundled device-only extension, without a tutorial panel, desktop window,
or noVNC display. Module 01 no longer needs GTK,
Qt, NumPy or pyqtgraph, even when building from source. The deployed web-only image
is 7.07 GB by Docker's storage metric; only 20.5 MB of filesystem layers are added
over the original Playground base. Historical desktop measurements and future
prebuilt packaging proposals are distinguished below.

## Dependencies

There are two different dependency sets: **building from source** and **running prebuilt applications**. The current local launcher does both. A Cloud Eval runtime image does not need to contain the compiler, CMake, development headers, or the complete Connext SDK if compatible applications and generated Python types are supplied ahead of time. It still needs the native and Python runtime libraries below.

### Build And Setup Dependencies

These belong on a developer machine or in a CI/builder image, not necessarily in the user workspace:

- Git (access to this Bitbucket repo and the public GitHub MedTech submodule), Bash, and network access to PyPI for the first run.
- Licensed RTI Connext DDS Professional 7.7.0, including its C++ libraries, build tools, and the `rti.connext.activated` Python wheel under `$NDDSHOME/resource/python_api`. Set `NDDSHOME` and source the matching `rtisetenv_<arch>` script; the launcher auto-detects `/Applications/rti_connext_dds-7.7.0` on macOS. The script cannot download or license Connext.
- Python 3.10+ with `pip` and `venv`; CMake 3.17+; and a C++17 compiler. GTK development libraries and `pkg-config` are not needed by Module 01.

On Ubuntu/Debian, install the system build packages with `sudo apt install build-essential cmake python3-venv`; install Python and Git separately if absent. On macOS, install the Xcode command-line tools and use `brew install cmake python3 git`.

### Runtime Dependencies

These remain necessary with the current application code, even if the C++ applications are precompiled:

- Python 3.10+ and the installed Python packages listed below, including the Connext 7.7.0 Python API. `pip` and `venv` are provisioning tools, not application requirements once the environment is prepared.
- The Connext C++ shared libraries used by the binaries, compatible OS/C++ runtime libraries, and the required runtime licensing configuration. Precompilation does not remove licensing requirements; a runtime-only Connext layout and redistribution rights must be validated with RTI.
- No GTK/Qt/display stack is needed for Module 01. Its C++ binaries no longer link GTK, and its Python backends no longer import desktop libraries.
- VS Code/code-server with the bundled device-grid extension, and a Markdown viewer for the tutorial. Cloud mode installs the extension files directly; desktop `--vscode` mode needs Node.js/npx and the `code` CLI for packaging/installation. `--web` opens local browser tabs without the extension. Native device windows are no longer supported. Hosted template provisioning still requires platform validation.

The local launcher creates a virtual environment and installs the MedTech Python requirements: `argcomplete>=3.1`, `pystun3>=2.0`, and `requests>=2.31`. It installs `rti.connext.activated` from the local Connext installation separately. Cloud mode checks the preinstalled environment instead. Module 04's optional desktop threat tools have their own requirements file and are not supported by this web-only image. Python transitive dependencies are resolved by `pip`.

### Historical Desktop Dependency Sizes

The following are historical **installed disk footprints**, not RAM use or compressed download sizes. Measurements were taken with `du -sh` on the original desktop macOS arm64 installation on 2026-09-30 (Python 3.14); they are reference points, **not Linux Cloud Eval image measurements**. The GTK/Qt/NumPy/display costs no longer apply to web-only Module 01. MiB/GiB values are rounded. Rows explicitly marked as budgets are rough Linux planning allowances, not measured package sizes. Versions, architecture, shared dependencies, and existing base-image contents change the incremental cost.

| Dependency | Build/setup | Prebuilt runtime | Installed size reference |
| --- | --- | --- | --- |
| Git | Clone and CMake FetchContent | Not needed if files are bundled; still needed by `launch_all.sh` | 20-60 MiB budget with dependencies; zero added if already present |
| Bash | Setup scripts | Needed by the shell launch scripts | 1-5 MiB budget; zero added if already present |
| C++17 compiler/toolchain | Required | Not needed; retain OS/C++ runtime libraries | 1.3 GiB measured for macOS command-line tools; Linux builder budget 250-600 MiB |
| CMake >=3.17 | Required | Not needed | 74 MiB measured |
| `pkg-config` | Historical GTK build discovery | Not needed | 0.6 MiB measured (`pkgconf`) |
| Connext Professional 7.7.0 SDK | Required, including code generator | Full SDK not intrinsically needed | 2.7 GiB measured for the complete local installation |
| Connext C++ libraries | Link libraries | Required shared-library subset | 690 MiB measured for the entire local architecture library directory, **not** a minimal runtime; subset size TBD after dependency audit |
| Connext Python API | Install for Python apps | Required | 34 MiB measured installed `rti` package; bundled wheel directory is 47 MiB and need not ship in runtime |
| Python >=3.10 | Build scripts and environment setup | Required | 88 MiB measured Homebrew Python package, excluding external shared libraries |
| GTK/gtkmm | Historical desktop build | Not needed by Module 01 | 11 MiB measured `gtkmm3` alone; historical Linux runtime budget 100-300 MiB |
| PySide6/Qt + shiboken6 | Optional desktop tools only | Not needed by Module 01 | 1.1 GiB + 1.4 MiB measured, excluding external OS libraries |
| NumPy | Optional desktop tools only | Not needed by Module 01 | 34 MiB measured |
| pyqtgraph | Optional desktop tools only | Not needed by Module 01 | 9.1 MiB measured, excluding NumPy/Qt already listed |
| argcomplete | Install into environment | Keep for current launcher | 0.25 MiB measured |
| pystun3 | Install into environment | Keep for current launcher | 0.03 MiB measured `stun` package |
| requests | Install into environment | Keep for current launcher | 0.57 MiB measured, excluding transitive dependencies |
| Display/remote desktop stack | Not needed to compile | Not needed by the normal tutorial | Historical 100-300 MiB Linux budget for Xvfb/VNC/noVNC, browser excluded |

The original desktop Python virtual environment measured **1.3 GiB**, and its all-module build directory measured **20 MiB** (includes build intermediates, not just deliverable binaries). These overlap the table entries: do not add them again. The SDK contains the C++ library and wheel directories, and many system libraries are shared. A deployment also needs application source/assets, generated `Types.py`, and XML configuration. A Linux runtime image total cannot be inferred by summing these Mac measurements.

### Cloud Eval Packaging And Startup

The web-only recipe adds about 20.5 MB of filesystem layers over the base. The original Playground image dominates the total footprint. Precompilation can additionally remove per-session builds; that startup optimization has not been implemented.

Recommended candidate: build in CI using a multi-stage container build, then copy the Linux/architecture-compatible Module 01 binaries, generated Python types, source/assets/configuration, installed Python environment, audited shared-library closure, and Markdown tutorial into a versioned runtime image. Keep the compiler, SDK build tools, headers, package caches, and unrelated modules in the builder stage. Build and runtime must match the target OS, CPU architecture, ABI, Python version, and Connext version; the local Mac binaries are not Linux deliverables.

Two deployment options need platform-team agreement:

- **Dedicated runtime workspace image:** simplest co-location of apps and IDE, but still a second image to maintain, patch, distribute, and prewarm. It requires platform support and is not just a new workspace definition.
- **Application container alongside the existing workspace:** could keep application build/runtime packages out of the base IDE image, but shifts their size into another image rather than eliminating it. Requires supported container orchestration, browser port routing for 8090-8093, DDS networking/discovery configuration, licensing, and process lifecycle management. Do not assume users can start Docker inside the workspace or that DDS discovery works across container networks by default.

Neither prebuilt packaging option is supplied by this repository today. `launch_all.sh` still initializes the submodule and runs the build. Local setup installs Python packages; cloud mode reuses the image environment. For a provisioned environment, `./tutorial/run_digital_or.sh --launch-only --web` skips setup/build and launches only the demo; it still expects the configured virtual environment, `NDDSHOME`, compatible binaries, generated types, configuration, and runtime libraries. A runtime-only image needs a validated entrypoint and layout rather than invoking `launch_all.sh` unchanged.

Before committing to either option, measure on the actual Linux base image: dependency-by-dependency incremental installed size, compressed registry layers to pull, uncompressed image size, and cold versus warm time to the first usable tutorial and all four responsive web UIs. Compare against the base workspace and separate image pull/unpack, provisioning, and application startup. Preinstalling removes session downloads/builds; larger uncached layers can still increase cold startup significantly. Reusing cached base layers and prewarming may help, but no startup-time claim is established yet. Pin the final Python/system dependencies and image digest so size, startup, and maintenance costs are reproducible.

## Run locally

```bash
git clone --recurse-submodules ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git
cd cloud_eval_medical
./tutorial/launch_all.sh --vscode
```

The single launch command also works after a plain `git clone`: it initializes the MedTech submodule at the pinned commit if missing, prepares Python dependencies, builds the C++ apps and Python types, installs the device-only extension, and launches the Digital OR applications in a 2x2 editor grid. Open [tutorial/TUTORIAL.md](tutorial/TUTORIAL.md) for the guided steps; there is no tutorial panel. The submodule checkout is never advanced to the latest branch tip. Existing tracked changes in a checkout at another commit block the update rather than being discarded.

Without a mode flag, `./tutorial/launch_all.sh` defaults to cloud/code-server grid mode; `--cloud` remains an explicit alias. Use `--vscode` for desktop VS Code or `--web` for ordinary browser tabs. Add `--secure` only after generating the security artifacts described in the MedTech README. After setup, the demo runs in the background and the terminal prompt returns; the launcher prints its PID and log file path. Use `./tutorial/stop_all.sh` to stop it or `./tutorial/restart_all.sh` to restart it with the same mode options. Direct foreground demo-only startup remains available with `./tutorial/run_digital_or.sh --vscode` after the submodule is initialized.

## Verify a clean clone

From a fresh clone, check that `git submodule status` reports the pinned commit without a leading `-` or `+`. Check for four responsive browser UIs, a PatientSensor process, and the ten steps in [tutorial/TUTORIAL.md](tutorial/TUTORIAL.md). The first run builds binaries, so allow time for it. Re-run `./tutorial/launch_all.sh --web` locally, or `./tutorial/launch_all.sh` in the cloud workspace, to verify the already-present submodule path. For an intentionally incomplete clone, omit `--recurse-submodules` and run the same launch command to verify auto-initialization.

The tutorial's [content and local usage](tutorial/README.md) and [cloud integration constraints](tutorial/INTEGRATION_NOTES.md) are documented separately. The prebuilt packaging options above remain proposals. A cloud workspace needs licensed Connext runtime support, the application's runtime dependencies, and authenticated browser port routing, not a display server. Native build dependencies are needed only if building there. This script prepares a local or suitably provisioned workspace, not a hosted evaluation template.
