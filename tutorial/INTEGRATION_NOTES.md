# Integration Notes: Digital Operating Room Cloud Eval

Open requirements before this demo becomes an `evaluation.rti.com` workspace
template. The tutorial is [TUTORIAL.md](TUTORIAL.md), not an injected tutorial panel.

## Browser Routing

The demo has four HTTP UIs on ports 8090-8093 and a headless Patient Sensor.
Cloud mode uses the bundled device-only extension to embed authenticated
code-server proxy URLs in a 2x2 editor grid. Desktop `--vscode` mode uses the
same grid; `--web` opens ordinary browser tabs. Validate extension activation,
those proxy routes, authentication, and any deployment URL prefix in the hosted
workspace. No desktop display or tutorial panel is needed. Device editor tab
closure stops its DDS process; ordinary browser tab closure does not.

## Build And Licensing

The workspace needs licensed Connext Professional 7.7 with `NDDSHOME` set,
Python runtime dependencies, CMake >=3.17, and a C++17 compiler if building there.
Module 01 needs no GTK or Qt dependencies. A full `python3 build.py` generates
both C++ binaries and Python type support; building only `module-01` skips
`refArchTypesPy` and leaves the Python apps without their generated types.

The [image runbook](../docker/README_cloud_eval_image.md) describes the current
source-build setup. Prebuilt Linux applications could eliminate per-session
builds, but a compatible runtime layout, licensing, redistribution rights, and
cold/warm startup measurements still need validation. Do not copy macOS build
outputs or virtual environments into a Linux workspace.

## Template Rollout

1. Include the Markdown tutorial and pinned source in the workspace.
2. Validate provisioning, licensed runtime, all four proxy routes, live DDS data,
   pause/resume, and scoped stop/restart on a fresh hosted workspace.
3. Register the workspace template through RTI's platform team. Existing Connext
   Studio visualization tools may be offered separately; they are not required
   to render this tutorial.