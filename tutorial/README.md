# Digital Operating Room Tutorial

This folder contains a locally runnable guided tutorial and the content proposed for a future
**Digital Operating Room** workspace on [evaluation.rti.com](https://evaluation.rti.com/workspaces), built from
[rticonnextdds-medtech-reference-architecture](https://github.com/rticommunity/rticonnextdds-medtech-reference-architecture),
Module 01. Hosted template integration is not yet validated.

It mirrors the structure, tone, and step granularity of the existing **Publish-Subscribe**
cloud eval tutorial (Introduction → explore code → build/run → configure QoS → observe/visualize →
next steps), but tells a healthcare-specific story aimed at Healthcare/MedTech prospects.

## Files

- **`digital-or-tutorial.json`** — the 10-step tutorial content, in a portable schema
  (title/body/openFiles/highlights/etc.) so RTI's cloud eval platform team can
  map it onto the same accordion-panel format used by "Connext Studio" without needing to
  re-derive the narrative. This is the primary deliverable.
- **`INTEGRATION_NOTES.md`** — gaps and decisions the platform team needs to resolve before
  this can go live in the cloud sandbox (web tabs, license/build step, tutorial UI).
- **`../medtech-reference-architecture/`** — a local clone of the source repo, confirmed to
  build and run Module 01 end-to-end (see [INTEGRATION_NOTES.md](./INTEGRATION_NOTES.md)).
- **`launch_all.sh`** — one-command local setup, build, and launch of the demo in VS Code
  tabs alongside the guided tutorial GUI.
- **`run_digital_or.sh`** — helper used by `launch_all.sh`; also supports standalone demos
  after the submodule is initialized.
- **`stop_all.sh`** — stops this checkout's demo apps and launchers from another terminal,
  including restored or orphaned devices; leaves the browser IDE and container running.
- **`tutorial_gui.py`** — a standalone PySide6 GUI that reads
  `digital-or-tutorial.json` and guides you through all 10 steps with Previous/Next
  navigation and buttons to open the referenced source files. It runs locally beside the
  web tabs; it is not the hosted "Connext Studio" panel.

## How the existing Publish-Subscribe tutorial actually works (verified by logging in)

- The right-side "Publish-Subscribe Tutorial" panel is a numbered accordion with 7 steps:
  Introduction → Explore the Data Type Definition → Explore the Publisher and Subscriber →
  Run the Applications → Configure Reliable QoS → Tools: Data Visualization & AI → Next Steps.
- Each step is plain text/lists, with inline buttons that (a) open a specific file in the editor,
  or (b) open a named terminal and paste/run an exact shell command.
- The QoS step and Visualization step both reference specific files/buttons already in the
  workspace (`USER_QOS_PROFILES.xml`, a "Visualize System" button, a "Create View with AI"
  button with a sample natural-language prompt).
- This tutorial content is **not** stored as a file in the workspace (checked `.vscode/` —
  only a `settings.json` is present). It's injected server-side by the "Connext Studio"
  VS Code extension, keyed by workspace template id. We cannot self-publish a new template;
  RTI's platform/eval team needs to wire this in.

## Local demo

```bash
git clone --recurse-submodules ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git
cd cloud_eval_medical
./tutorial/launch_all.sh
```

Run from the repository root with licensed Connext 7.7 installed. The script initializes the
pinned submodule, prepares a virtual environment, builds C++ and Python type support, and
starts the four web UIs in VS Code tabs plus a headless Patient Sensor. It opens the tutorial
GUI alongside them. Closing the tutorial GUI or pressing Ctrl+C in the launch terminal stops
the demo. In VS Code mode, closing a device tab kills its DDS process so the Orchestrator
can detect the disconnect. Closing a plain browser tab in `--web` mode does not stop the app.

To use browser tabs instead of VS Code, or native application windows, run:

```bash
./tutorial/launch_all.sh --web
./tutorial/launch_all.sh --native
```

The launcher installs the bundled [MedTech Web Tabs extension](../medtech-reference-architecture/vscode-extension/README.md)
for the default VS Code mode. Add `--secure` only after generating security artifacts; see the
[top-level setup guide](../README.md).

## Cloud image

The sibling cloud image includes the GTK build dependencies and Python packages,
and sets `MEDTECH_VENV=/opt/medtech-venv` to reuse its licensed Connext 7.7 Python
API instead of a copied macOS virtual environment.

Open `http://127.0.0.1:8080/?folder=/config/workspace`, accept Workspace Trust for
this tutorial workspace, and run once in its terminal:

```bash
cd /config/workspace
./tutorial/launch_all.sh --cloud
```

Cloud mode is also selected automatically in a headless `/app/code-server` image.
The launcher installs the bundled extension, builds all five DDS applications,
opens the tutorial in a native VS Code side panel, and opens Arm Controller, Arm,
Orchestrator, and Patient Monitor in a 2x2 editor grid. Patient Sensor is headless.
No desktop VS Code CLI or noVNC display is used. After first installing or updating
the extension, reload the browser IDE once if the Digital Operating Room activity
icon is missing. Select that icon before launching if multiple IDE windows are open.

The tutorial renders the same ten JSON steps with Open File actions and Restore
buttons. Closing a device editor tab kills its DDS process; Restore starts only
that device and reopens its tab. While the device is running or its health is
unknown, its Restore button is disabled. Only the code-server port needs publishing;
the embedded device frames use `/proxy/8090/` through `/proxy/8093/` internally.

Set `MEDTECH_CLOUD_URL` to the external IDE origin when it differs from
`http://127.0.0.1:8080` in the container environment before code-server starts,
and `MEDTECH_CODE_SERVER_EXTENSIONS` if its extension directory differs from
`/config/extensions`. Hosted deployments with a URL prefix need matching proxy
routing integration.

Press Ctrl+C in the launch terminal to stop the demo, including restored devices,
and close its device tabs. If that terminal is lost, open another IDE terminal and
run `./tutorial/stop_all.sh` from `/config/workspace`. It targets only this checkout's
processes owned by your user and is safe to run again when nothing is running.
Do not launch a second copy while the first is running. A ports-already-in-use error
means an existing launch must first be stopped.
This is a bundled tutorial view, not registration as a hosted Connext Studio template.
Keep platform authentication in front of remote proxy routes; the sample Docker port
remains bound to localhost.

## Guided tutorial GUI

`launch_all.sh` opens the tutorial automatically. Its "Open File" buttons use VS Code if
`code` is on your `PATH`, otherwise the OS default editor. The tutorial's web-demo steps
do not start a second build or launch. In the default VS Code mode, four Restore buttons
restart stopped apps individually and reopen their VS Code tabs. A button stays disabled
while its app is running or its health is unknown, and becomes available after the app stops.
Keep the Orchestrator tab open during failure exercises to see disconnect and recovery alerts. After updating
the extension, run **Developer: Reload Window** in VS Code and relaunch the demo to load
the new close handling. Closing the tutorial also stops apps restarted this way.
