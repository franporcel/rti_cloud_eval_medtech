# Digital Operating Room Tutorial

The guided tutorial lives in [TUTORIAL.md](TUTORIAL.md). Open it in a Markdown
viewer alongside the four device UIs in a 2x2 VS Code editor grid. The bundled
device-grid extension has no tutorial panel. Hosted template integration is not
yet validated.

## Files

- [TUTORIAL.md](TUTORIAL.md): the ten guided tutorial steps and source links.
- [INTEGRATION_NOTES.md](INTEGRATION_NOTES.md): hosted deployment requirements.
- [launch_all.sh](launch_all.sh): initialize the pinned submodule, set up, build,
  and start all five applications in the background.
- [run_digital_or.sh](run_digital_or.sh): setup/build and foreground launch helper.
- [stop_all.sh](stop_all.sh): stop this checkout's demo processes without stopping
  the browser IDE or container.
- [restart_all.sh](restart_all.sh): stop and relaunch; forwards launcher options.

## Local Demo

Run from the repository root with licensed Connext 7.7 installed:

```bash
git clone --recurse-submodules ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git
cd cloud_eval_medical
./tutorial/launch_all.sh --vscode
```

The launcher initializes the pinned submodule, prepares a virtual environment,
builds C++ and Python type support, and opens Orchestrator, Arm Controller, Arm,
and Patient Monitor in a 2x2 editor grid. Patient Sensor is headless. Desktop VS
Code mode packages/installs the bundled device extension using Node.js/npm and
the `code` CLI; `--web` opens ordinary browser tabs without those dependencies.
Add `--secure` only after generating the
security artifacts described in the [top-level setup guide](../README.md).

## Cloud Workspace

The [cloud image recipe](../docker/README_cloud_eval_image.md) provides web-only
device apps and sets `MEDTECH_VENV=/opt/medtech-venv` to reuse the base's licensed
Connext 7.7 Python API.

Open `http://127.0.0.1:8080/?folder=/config/workspace`, accept Workspace Trust,
open [TUTORIAL.md](TUTORIAL.md), and run in the IDE terminal:

```bash
cd /config/workspace
./tutorial/launch_all.sh
```

Cloud mode is the default; `--cloud` remains an explicit alias. It installs the
device-only extension and opens Arm Controller / Orchestrator above Arm / Patient
Monitor in the editor grid. Reload the browser IDE after installing or updating
the extension. No tutorial panel or activity-bar icon is registered. Select the
intended IDE window before launching if multiple windows are open. The printed
proxy URLs are also available for ordinary browser tabs:

- Orchestrator: `http://127.0.0.1:8080/proxy/8090/`
- Arm Controller: `http://127.0.0.1:8080/proxy/8091/`
- Arm: `http://127.0.0.1:8080/proxy/8092/`
- Patient Monitor: `http://127.0.0.1:8080/proxy/8093/`

Only the authenticated code-server port needs publishing. Set
`MEDTECH_CLOUD_URL` to the externally accessible IDE base URL, including any path
prefix, when it differs from `http://127.0.0.1:8080`. Hosted deployments must
validate matching proxy routing. Keep platform authentication in front of remote
proxy routes; the sample Docker port remains bound to localhost.

## Stop And Restart

After setup, the terminal prompt returns while the demo runs in the background.
The launcher prints the supervisor PID and log path. Closing a terminal or browser
tab does not stop the applications in `--web` mode. Closing a device editor tab
in grid mode stops its DDS process; Orchestrator `Start` resumes paused devices
or relaunches stopped devices and reopens their tabs. Use **Digital Operating
Room: Open Orchestrator** in the Command Palette to recover Orchestrator itself.
Stop or restart the complete demo with:

```bash
./tutorial/stop_all.sh
./tutorial/restart_all.sh
```

Use `./tutorial/restart_all.sh --web` for local browser mode, and add `--secure`
when needed. Stop targets only this checkout's processes owned by your user and
is safe to run again when nothing is running. Stop closes device editor tabs;
ordinary browser tabs remain open and need refreshing after restart. Do not
launch a second copy while the first is running.
A ports-already-in-use error means the existing launch must first be stopped.
