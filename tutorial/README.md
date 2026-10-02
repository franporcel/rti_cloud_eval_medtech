# Digital Operating Room Tutorial

The guided tutorial lives in [TUTORIAL.md](TUTORIAL.md). Open it in a Markdown
viewer alongside the four browser-based device UIs. There is no tutorial panel or
custom editor integration. Hosted template integration is not yet validated.

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
./tutorial/launch_all.sh --web
```

The launcher initializes the pinned submodule, prepares a virtual environment,
builds C++ and Python type support, and opens Orchestrator, Arm Controller, Arm,
and Patient Monitor in browser tabs. Patient Sensor is headless. No Node.js or
desktop UI dependencies are required. Add `--secure` only after generating the
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

Cloud mode is the default; `--cloud` remains an explicit alias. It prints the
device URLs rather than opening a browser inside the container. Open those URLs
in your browser after setup:

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
tab does not stop the applications. Orchestrator `Start` resumes paused devices;
it cannot relaunch exited processes. Restart the demo to recover stopped devices:

```bash
./tutorial/stop_all.sh
./tutorial/restart_all.sh
```

Use `./tutorial/restart_all.sh --web` for local browser mode, and add `--secure`
when needed. Stop targets only this checkout's processes owned by your user and
is safe to run again when nothing is running. Browser tabs remain open; refresh
them after restarting. Do not launch a second copy while the first is running.
A ports-already-in-use error means the existing launch must first be stopped.
