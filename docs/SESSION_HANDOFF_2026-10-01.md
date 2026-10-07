# Cloud evaluation session handoff

## Latest Deployment: SDK CMake Utilities (2026-10-06)

- CMake now uses the Connext 7.7.0 SDK's `resource/cmake` utilities, selected
  through `NDDSHOME` or the `CONNEXTDDS_DIR` CMake cache variable. The RTI
  utilities GitHub download is removed; the JSON dependency download remains.
- All 139 local tracked files were synchronized to `medical-playground` and
  verified for content, executable permissions, and `abc` ownership. Container
  Git metadata, credentials, generated files, machine settings, image, and
  runtime dependencies were preserved. SDK utilities source is published as
  `0f46d5487544f112c57a6ed5c0874a486403e482` on `web-based-tutorial-apps`;
  the parent gitlink selects that revision. Publication updates are host-only;
  the live workspace retains its pre-publication documentation and Git metadata.
- Backup: `/config/medtech-deployment-backups/sdk-utils-20261006.uEqT9S/pre-deploy.tar.gz`.
  SHA-256: `71e761ffcbda1b778c8a03670e58c50bd4cf4d1d9c1269943f7dee704f425992`.
- Deployed build, 43 Python tests including secure/nonsecure five-app acceptance,
  and 26 JavaScript tests passed. Three legacy display tests were skipped.
- Normal `launch_all.sh --cloud` startup passed. Demo left running with
  supervisor PID `28607`, log `/tmp/medtech-digital-or.7egKVm`; all four APIs
  returned HTTP 200, DDS devices reported ON, and patient data was fresh.
  Editor-tab rendering was not rechecked in the browser during this deployment.
- The launcher still requires Git metadata; removing that dependency is a
  separate, not-yet-implemented cloud integration change.

Latest source update: 2026-10-02, corrected scope: restore the device extension
and 2x2 editor grid; remove only the tutorial panel. This opening section
supersedes every historical workflow below.

## Resume Here: Device Grid, Markdown Tutorial

- User clarified that only the tutorial panel should be removed, not the device
  grid. The bundled extension now contributes only its device command, with no
  tutorial view, activity-bar container, renderer, JSON content, or desktop GUI.
- Grid: Arm Controller / Orchestrator above Arm / Patient Monitor. Cloud default
  and desktop `--vscode` modes restore editor-tab lifecycle and Orchestrator Start
  recovery; `--web` remains the ordinary browser fallback. Read
  [TUTORIAL.md](../tutorial/TUTORIAL.md) separately as Markdown.
- Device recovery is extracted into `vscode-extension/device-launcher.js` and
  is independent of tutorial visibility. `/session` initializes security and
  startup state without opening any panel. Focus the intended IDE window before
  launching when several windows are open.
- Host checks passed: 25 JavaScript tests (including no tutorial contributions,
  cloud ownership, concurrent recovery, grid slots and surviving panels), nine
  launcher tests, and shell syntax. The same 25 JavaScript tests pass in Linux;
  the normal cloud launcher completed the Linux build and opened the real grid.
- Live acceptance: all four device editor tabs occupy their intended slots, all
  devices report ON, patient data is fresh, and the activity bar has no tutorial
  entry. Closing Arm terminated its original process (PID 9019 became defunct),
  produced the DDS OFF alert, and Orchestrator Start relaunched/reopened it in
  the bottom-left slot without replacing the other tabs.
- Multi-window cleanup was corrected: full stop routes requests to the hosts
  recorded as owning device tabs, rather than whichever window is focused.
  Its regression passes; code-server was restarted so all hosts load that fix.
  Live full stop closed all four tabs and released all four device ports.
- Final demo is RUNNING after a clean restart: supervisor PID 1822, log
  `/tmp/medtech-digital-or.nXZQIg`. Shared IDE:
  `http://127.0.0.1:8080/?folder=/config/workspace/tutorial`. All devices ON,
  patient `data_stale=false`, nonblank Arm and three waveform canvases, intended
  editor groups 1/2/3/4, and zero tutorial activity-bar entries verified.
- Scoped pre-correction backup:
  `/config/medtech-deployment-backups/device-grid-20261002-223334/pre-deploy.tar.gz`.
  This is an affected-files backup, not an image/full-volume export. Source Git
  metadata and unrelated edits were preserved; dependency image unchanged.
- Device-grid source is published on `origin/web-based-tutorial-apps` at
  `898e28a0504ff9f38e0bd525e5931eed3c8bfa5a`; this parent revision pins it.
  Previous parent `dc5c6f9` and submodule `e072dfd` describe the browser-only
  detour, not the current device-grid workflow.
- Shared-workspace caveat: the extension activates in every workspace in a
  code-server instance and uses a per-user request queue. Another repo's window
  can consume MedTech launch requests. Workspace-only activation/request
  handling is recommended but has not been implemented. Separate containers
  with independent `/config` volumes do not share this installation or queue.

## Historical Browser-Only Detour

The following section records the overly broad extension removal and its
deployment, before the user clarified the intended scope. Its browser-only
startup and recovery limitations are superseded by the device-grid correction.

## Resume Here: Markdown-Only Tutorial

- [TUTORIAL.md](../tutorial/TUTORIAL.md) is the sole tutorial content. The bundled
  extension source, generated VSIX, JSON tutorial, standalone PySide6 tutorial,
  and their extension/GUI tests were removed. There is no tutorial panel.
- `./tutorial/launch_all.sh` defaults to cloud mode and prints four device URLs
  using `MEDTECH_CLOUD_URL` (default `http://127.0.0.1:8080`) plus `/proxy/8090/`
  through `/proxy/8093/`. Open those URLs in browser tabs; no container browser
  or extension installation is attempted. `--cloud` remains an explicit alias.
- For local demos, use `./tutorial/launch_all.sh --web` to open browser tabs
  automatically. `--secure` remains supported after generating security
  artifacts. The former `--vscode` mode is removed.
- Browser tab closure does not stop a DDS application. Orchestrator **Start**
  resumes paused devices but cannot relaunch exited processes. Use
  `./tutorial/restart_all.sh` (or `--web` locally) to recover stopped devices,
  then refresh their tabs. Tutorial failure exercises use a verified device PID
  rather than tab closure. The launch supervisor still handles SIGTERM cleanup.
- Setup/build, pinned submodule initialization, background launch, supervisor
  PID/log output, and scoped stop/restart remain supported. The stop helper no
  longer queues extension tab-close requests.
- Preserved browser UI regressions now live in
  `medtech-reference-architecture/modules/01-operating-room/tests/web.test.js`.
  Checks passed: seven launcher tests (including isolated, idempotent shutdown
  preserving an unrelated process), four Node UI tests, shell syntax for all
  four scripts, embedded stop-helper Python syntax, JSON parsing, Markdown
  source links, and touched-file diagnostics.
- **Deployed on 2026-10-02** into `medical-playground`'s preserved `/config`
  volume. Changed files from parent `dc5c6f9849f82fd2c011de7640b226e0608ab48e`
  and submodule `e072dfd2197e5fe8155ff06025233dd02f7c1618` were copied and
  byte-verified against Git. Retired tutorial files and the bundled extension
  source/installation were removed; other extensions were left untouched.
- The existing image is unchanged: `medical-playground:medtech-cloud-web`,
  ID `sha256:a528508d1e8f29139a4d6acb6a5c791a5b0bc3b4294e81fa33f370ef9a30cca6`.
  The recipe stores source in the workspace volume, not image layers, so no
  dependency-image rebuild was needed. The container was restarted to unload
  the removed extension. Existing Git metadata, QoS/XML edits, and build outputs
  were preserved; this deployment is a scoped source overlay, not a clean clone.
- Verified in the container: all four Node UI tests, script syntax, `abc:abc`
  ownership, full Linux build, four HTTP pages/APIs, all four authenticated
  browser proxy routes, fresh DDS vitals, Pause/Start through the browser UI
  for all four devices, and full stop/restart without reinstalling the extension.
  Final state: demo running, four devices ON, patient data not stale. Supervisor
  PID `1258`, log `/tmp/medtech-digital-or.DEMoVW` (process values are transient).
- Verified targeted pre-deployment backup:
  `/config/medtech-deployment-backups/markdown-only-20261002-222054/pre-deploy.tar.gz`.
  It preserves affected prior source and the removed extension, not the complete
  image or volume. Keep it private; approved off-machine backup remains pending.
- Publication: submodule `e072dfd2197e5fe8155ff06025233dd02f7c1618` is published
  on GitHub's `web-based-tutorial-apps` branch; its remote SHA was verified.
  The parent commit containing this handoff pins that revision and targets
  Bitbucket `origin/develop`. Machine-local `.vscode/` settings are excluded.
  Verify the parent remote SHA against the containing commit after pushing.
- Remaining platform work: fresh-volume hosted provisioning, image export and
  approved off-machine backup, cold/warm startup measurements, and a validated
  prebuilt runtime entrypoint. See the [usage guide](../tutorial/README.md) and
  [cloud runbook](../docker/README_cloud_eval_image.md).

## Historical Extension Workflow

Everything below records the previous extension-based deployment and its earlier
verification. Extension, sidebar, editor-grid, tab-close, and automatic recovery
instructions below are historical, not current setup guidance. Runtime state
must be rechecked before deployment or Docker operations.

## Resume here

- **The image is already rebuilt and deployed**, not just an updated Dockerfile.
  `medical-playground` runs `medical-playground:medtech-cloud-web`; its running
  image ID matches the local tag. The IDE health endpoint is alive on port 8080.
- Qt/PySide6/shiboken6, pyqtgraph, NumPy, GTK, Mesa/EGL/LLVM, and VNC support are
  absent from the image. Latest verification reconfirmed the removed Python
  modules are absent and all device ports 8090-8093 are free.
- The existing `/config` volume is preserved. All original/restored demo apps and
  launchers are stopped, and all four demo tabs were closed. To start once, open
  `http://127.0.0.1:8080/?folder=/config/workspace`
  and run `./tutorial/launch_all.sh` from `/config/workspace`. Cloud mode is now
  the default; `--cloud` remains an alias, `--vscode` selects desktop VS Code,
  and `--web` selects standalone browser tabs.
- The current submodule is published as `6f2f76e903d5cd0c9a9b9b4d7a5c598d1dc9af3c`.
  The parent publication containing this handoff pins it and includes the
  compact layouts, stable arm, shutdown fixes, and matching baseline/docs pins.
  A clean checkout
  of this parent publication includes the latest behavior without a source overlay.
- Recovery now lives in Orchestrator **Start**, not tutorial Restore buttons.
  Start resumes paused devices or relaunches stopped devices and reopens tabs.
  **Digital Operating Room: Open Orchestrator** restores the Orchestrator itself.
- Latest checks: 20 Node tests on host/Linux, 12 launcher tests on the host,
  Linux Orchestrator rebuild, focused heartbeat state checks, and live shutdown,
  recovery, pause/resume, manual closure, and cleanup workflows. The earlier
  98-frame no-reflow capture remains historical evidence, not a newly rerun check.
- Grid: Arm Controller / Orchestrator above Arm / Patient Monitor. All four
  headers are compact and omit visible RTI branding. The arm fills about 74% of
  its quarter-pane canvas with a fixed base and manual zoom, Fit, and drag-pan.
- Per-process tab closure uses `/close-owned?closeToken=...`, never token-only
  `/close`: older extension hosts interpret the latter as closing every tab.
  Use a real **Developer: Reload Window** after extension updates.
- Images and workspace source are separate: this dependency image does not bundle
  the source, extension, or built apps. Those remain in `/config`. Publishing Git
  did not rewrite the running volume's existing Git metadata or its tested files.
- Remaining work: export/back up the new web-only image, copy backups to approved
  off-machine storage, test fresh-volume installation, and measure hosted cold
  startup. Prebuilt startup optimization has not been implemented.
- This handoff is part of the current parent publication. The earlier baseline
  handoff was included in parent commit `9d0d70b`. Unrelated
  host VS Code settings and the generated VSIX remain intentionally untracked.

## Session summary: 2026-10-02

### Latest compact UI and lifecycle verification

- Viewport-height layouts fit the four editor panes without page scrolling.
  Controller joint controls sit beside global commands and logs; Orchestrator
  has 2x2 devices, commands on the right, and full-width logs below; Patient
  Monitor keeps all four vitals visible. Compact headers omit visible RTI text.
- Logs compare complete formatted text, so rolling same-count buffers update.
  Display-only formatting removes known DDS enum prefixes and trailing web-mode
  text without changing raw API logs. Orchestrator follows each new message;
  Controller follows only when already at the bottom. Unchanged polls preserve
  manual scrolling.
- Arm uses a fixed viewport-based scale/base, not pose-dependent fitting. The
  default pose occupies 74% of the quarter-pane canvas and 73% on mobile.
  Explicit zoom, Fit, and drag-pan allow unusual poses to be reframed; normal
  joint motion never automatically recenters or rescales upstream joints.
- Reproduced the all-tab shutdown regression against the published older
  extension: token-only `/close` fell through to global closure. Launchers now
  emit `/close-owned?closeToken=...` on child exit and partial-launch cleanup.
  Current handlers reject missing, invalid, or stale tokens; older handlers
  safely ignore the new endpoint. Explicit full-demo closure remains supported.
- Rapid restart exposed a heartbeat deadline marking a recovered app OFF
  permanently. Orchestrator now consumes fresh valid heartbeats and restores
  the last reported ON/PAUSED status while preserving explicit DDS OFF reports.
- Passed 20 Node tests on host/Linux and 12 host launcher tests; touched-file
  diagnostics and whitespace checks are clean. CMake Tools could not configure
  the host project; the touched Orchestrator target built successfully in the
  working Linux container. A compiled check of the actual listener covered
  deadline OFF, ON/PAUSED recovery, explicit OFF, and invalid heartbeat data.
- Live checks covered original/restored individual shutdowns, all four devices'
  pause/resume, six rapid restart cycles across the three controlled web apps,
  two rapid sensor restart cycles, manual close/Start for those three tabs, and
  manual Orchestrator closure preserving the other three apps. Surviving iframe
  identities and bounds were unchanged; old app/launcher PIDs were verified gone.
- Arm canvas pixels, upstream positions, zoom/Fit/pan, and screenshots were
  checked. Responsive checks passed at 390x420, 520x300, and 1280x800 with no
  page scrolling or label overflow. The full grid permutation harness was not run.
- Hidden shared browser pages throttle timers and bridge messages. For automated
  checks, CDP `Emulation.setFocusEmulationEnabled` made the IDE visible; it was
  reset afterward. Browser reload alone is not proof of extension-host reload.
- Deployed source/loose extension files into the preserved volume with `abc:abc`
  ownership and performed a real IDE Reload Window. No image rebuild, container
  recreation, backup refresh, or live-volume Git metadata change was performed.
  Final scoped stop verified no original/restored app or launcher remained and
  all four tabs were closed; the IDE remains available on port 8080.

The following recovery and recorded-frame sections describe earlier checks.
The current grid, framing, protocol, and test results above supersede them.

### Recovery and lifecycle

- Replaced the tutorial's Restore controls with Orchestrator Start. The ten
  instructional steps, file actions, and navigation remain in the sidebar.
  Tutorial exercises and extension documentation now describe Start recovery.
- Start supports Arm, Arm Controller, Patient Monitor, and headless Patient
  Sensor. Running/paused devices retain the DDS START command; stopped devices
  launch through `run_digital_or.sh --launch-only <app> --vscode`.
- The Orchestrator iframe bridge validates its source/origin, device whitelist,
  and request IDs. Recovery is independent of whether the tutorial is visible.
- Health polling is 250 ms; bounded 15-second startup guards prevent duplicate
  launchers. Unknown health never authorizes a new process. Patient Sensor uses
  an owned PID record at `/tmp/medtech-web-tabs-911/PatientSensor.process`.
- Immediate Shut Down/Start remembers shutdown intent before the next OFF poll.
  Recovery waits up to two seconds for endpoint/PID exit, retrying transient
  connection resets/timeouts; tab-absent recovery also waits for the close watcher.
- The full VS Code launcher stays alive after all original apps are replaced.
  SIGTERM invokes Python cleanup, restored launchers have owned process groups,
  and the shell cleanup signals both children and the persistent supervisor.
- Live checks verified new PIDs for all four controlled apps and Orchestrator,
  pause/resume, tab-close recovery, external process kill, and normal shutdown
  after every original app was replaced. Recovered devices survived restarting
  Orchestrator, and final cleanup left no original or recovered processes.

### Recorded UX correction

- Preserving iframe objects alone did not remove the visible glitch. Before/after
  frame captures showed that closing a tab collapsed its editor group and Start
  rebuilt the grid, making the other visible panes resize and repaint.
- The final fix reserves empty demo slots with a temporary workspace setting:
  `workbench.editor.closeEmptyGroups=false`. Recovery now performs **no layout
  commands or survivor reveals**; it fills only the missing panel's slot.
- The previous workspace setting is restored on full demo closure and awaited
  extension deactivation, without overwriting a setting changed by the user.
  The real container setting returned to unset after verification cleanup.
- Duplicate healthy opens do not reload HTML. An existing tab for a restarted
  process reloads only its own iframe when its process ownership token changes.
  The grid uses row-major slots: Arm Controller/Arm above Orchestrator/Patient
  Monitor. Orchestrator selection and surviving iframe state are preserved.
- Post-fix rendered checks captured 40 Arm, 29 Arm Controller, and 29 Patient
  Monitor frames: zero blank survivor frames, zero bounds changes including tab
  closure, and unchanged survivor iframe identities. The existing-tab reconnect
  path also passed. Do not substitute final coordinates/iframe identity for a
  visual transition check when investigating future UX regressions.
- Compositor screencasting stalled on the hidden shared browser; direct
  `Page.captureScreenshot` sequences worked at roughly eight frames per second.
  Filmstrip screenshots are in this session's chat artifacts; no permanent MP4
  was saved, and browser-memory recordings were cleared by reload.

### Launcher default and deployment

- `./tutorial/launch_all.sh` now defaults to cloud/code-server mode regardless of
  DISPLAY or environment auto-detection. `--cloud` is an explicit alias;
  `--vscode` and `--web` opt into desktop VS Code and standalone browsers.
  `MEDTECH_CLOUD` is explicitly exported as 0 or 1 to avoid inherited-mode leaks.
- Root/tutorial README examples were updated. Six actual argument-parser cases
  passed, covering default/cloud/desktop/browser/secure modes with DISPLAY set;
  shell syntax passed on macOS and Linux. No fresh-volume installation was run.
- Changed source and loose extension files were copied into `medical-playground`
  and the IDE reloaded. Cloud installs copy loose files into
  `/config/extensions/rti.medtech-web-tabs-0.1.0`; desktop mode packages/installs
  a VSIX. The existing generated VSIX was not rebuilt by this session's cloud work.
- `docker cp` preserved host ownership and initially caused extension-copy
  permission errors. After each deployment, copied files were restored to
  `abc:abc` (UID 911/GID 1001). Keep doing this for future source copies.
- Earlier focused validation: 18 Node tests on host and Linux; 11 launcher pytest
  tests on host; relevant Python syntax, JavaScript diagnostics, shell routing,
  real DDS workflows, and visual captures. Linux pytest is not installed. The
  grid integration harness expectation was updated, but its complete permutation
  suite was not executed during this session.
- During implementation, no image rebuild, container recreation, Git commit/push,
  licensed-artifact export, or backup refresh was performed. The subsequent
  authorized Git publication is recorded below. Host and live-volume Git metadata
  remain separate. The user grants standing permission to restart the demo and
  reload the IDE for future verification; leave temporary demos stopped afterward.

### Authorized publication

The user authorized publishing the compact UI and lifecycle fixes plus the
updated handoff. Submodule commit
`6f2f76e903d5cd0c9a9b9b4d7a5c598d1dc9af3c`, titled
`Fit operating-room panes and isolate device shutdown recovery`, was pushed to
GitHub `web-based-tutorial-apps`; its remote SHA was verified before parent
publication. The parent commit titled
`Update handoff and pin compact operating-room fixes` contains its matching
gitlink and updated handoff, README, baseline, and clean-install runbook pins.
Publish the parent to Bitbucket `develop` with `HEAD:develop` because the local
branch is named `main`. Final pre-publication checks passed 20 Node tests and
12 host launcher tests, plus documentation assertions and whitespace checks.
Machine-local `.vscode/` and the generated VSIX are excluded. No image rebuild
or live-volume Git metadata change is part of this publication.

#### Earlier recovery publication

The user authorized publishing the outstanding changes. Submodule commit
`5ef04beefcef94cfa387704e2ebd0591d4d5da24` was pushed to GitHub
`web-based-tutorial-apps` and its remote SHA verified before parent publication.
The parent commit titled `Default to cloud mode and publish recovery handoff`
contains the matching gitlink, launcher/tutorial/docs, baseline/runbook pins,
and this handoff; publish it to Bitbucket `develop` with `HEAD:develop` because
the local branch is named `main`. No image or volume Git metadata was changed.

Immediately before publication, 18 Node tests, 11 host launcher tests, and shell
syntax checks passed again. Machine-local `.vscode/` and the generated VSIX were
intentionally excluded. Image export, off-machine backup, fresh-volume acceptance,
and cold-start measurement remain outstanding.

## Goals and non-negotiable constraints

- Run the Digital Operating Room tutorial in RTI's Playground Docker image using
  code-server, with a native VS Code tutorial sidebar and four live device UIs in
  a 2x2 editor grid. Separate browser tabs and a noVNC tutorial are not the requested
  experience.
- Use browser IDE port **8080**, always. Bind it to localhost for this local setup.
- Preserve the original licensed archive, development workspace, and reproducible
  image recipe. Do not delete/prune volumes or overwrite backups.
- Prepare a reproducible clean installation for another engineer. The existing
  system works, but a complete fresh-volume installation of the newly pinned
  Dockerfile has not yet been performed.

## Repository and Git state

Host workspace: `/Users/fran/code/repos/cloud_eval_medical` on macOS.

| Repository | Branch and remote | Published revision |
| --- | --- | --- |
| Parent | Local `main` tracks Bitbucket `origin/develop` | Commit containing this handoff, titled `Update handoff and pin compact operating-room fixes` |
| MedTech submodule | `web-based-tutorial-apps`, GitHub origin | `6f2f76e903d5cd0c9a9b9b4d7a5c598d1dc9af3c` |

The parent revision is identified by its commit/title rather than embedding its
own SHA in itself. The earlier web-only baseline parent was
`9d0d70b89c091d4da8d3bd8b5dc9604ae45a45b2`. This publication includes launcher/
supervisor lifecycle, Orchestrator frontend, extension recovery/grid/command
registration, tutorial content, documentation, and tests. `.vscode/` and the
generated VSIX remain untracked and unrelated to publication.

Parent origin: `ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git`.
Submodule origin:
`https://github.com/rticommunity/rticonnextdds-medtech-reference-architecture.git`.

Published commits from the earlier web-only sessions:

- Submodule `4050cd3`: cloud URI bridge, native tutorial sidebar, proxy-compatible
  device UIs, editor-grid ownership and restore lifecycle, regression tests.
- Parent `6700ae0`: cloud launcher/environment support, process cleanup, emergency
  stop script, tests, tutorial documentation, updated submodule gitlink.
- Parent `68ca7b5`: versioned image recipe, pinned Python versions, baseline,
  clean-install/backup runbook, Git/build-context exclusions, root README links.
- Submodule `1e18c2f`: web-only device backends and GTK-free build targets,
  desktop-import regression tests, separate Module 04 desktop requirements.
- Parent `9d0d70b`: published web-only image recipe and submodule pin, sidebar-only
  normal tutorial launch, deployment/rollback runbook, baseline, and this handoff.

Because the parent local branch name differs from its upstream, publication used
`git push origin HEAD:develop`, not an assumed `main` remote branch. Push submodule
changes before publishing the parent gitlink. Do not commit generated archives,
credentials, or unrelated editor settings. This handoff was first published in
`9d0d70b`; the latest current-state refresh is included in this publication.

## Canonical files in this workspace

| Path | Purpose |
| --- | --- |
| `docker/Dockerfile` | Canonical derived-image recipe, explicitly `linux/amd64` |
| `docker/requirements.txt` | Five web-only Python pins; licensed Connext inherited from base |
| `docker/baseline.json` | Archive checksum, image IDs, source revisions, observed APT versions, runtime settings |
| `docker/README_cloud_eval_image.md` | Clean-install instructions, acceptance checks, image and volume backup/restore |
| `docker/.dockerignore` | Only Dockerfile and requirements enter the build context |
| `.gitignore` | Excludes caches, archives, VSIX, `.env`, and `rti_license.dat` |
| `tutorial/launch_all.sh` | Full tutorial launch; cloud selection, setup, extension installation, duplicate-launch guard |
| `tutorial/run_digital_or.sh` | Setup/build/demo helper; uses `MEDTECH_VENV` when supplied |
| `tutorial/stop_all.sh` | Executable emergency stop for this checkout's apps and restored/orphaned devices |
| `tutorial/digital-or-tutorial.json` | Shared ten-step tutorial content |
| `tutorial/tutorial_gui.py` | Legacy optional PySide6 tutorial; not installed or started by the normal workflow |
| `tutorial/test_tutorial_gui.py` | Tutorial, signal cleanup, and real-subprocess stop-script tests |
| `medtech-reference-architecture/launch.py` | App launch/close lifecycle and cloud URI request dispatch |
| `medtech-reference-architecture/vscode-extension/extension.js` | Four-panel grid, cloud proxy mapping, URI bridge ownership |
| `medtech-reference-architecture/vscode-extension/tutorial-view.js` | Native tutorial sidebar, file actions, health checks, device restore |
| `medtech-reference-architecture/vscode-extension/tutorial.svg` | Activity Bar icon |

Detailed procedures: [image runbook](../docker/README_cloud_eval_image.md),
[runtime baseline](../docker/baseline.json), and [tutorial guide](../tutorial/README.md).

## External files not visible in this workspace

### Historical image directory

`/Users/fran/code/repos/cloud_eval_image` (sibling `../cloud_eval_image`) is **not a
Git repository**. It contains the historical Dockerfile, image README, and original
`playground-20260709a.tar.gz`. The canonical recipe/runbook are now in this repo's
`docker/`; do not continue editing only the sibling copies.

The original archive was not modified or repacked. No modifications to it are
needed: load the original base and build a separate derived image. Its measured
identity is:

- Size: `1067094537` bytes.
- SHA-256: `70b8ecddd05e927644390f4bffd25d3302a841a02a25c14aaeacba7011debfa1`.

This is a checksum of our supplied copy, not an independent vendor signature.
Keep licensed artifacts in authorized storage, not Git. Native host development
also requires a licensed Connext installation outside the repo; previous local
setup used `/Applications/rti_connext_dds-7.7.0`.

### Completed manual backup

Absolute directory:
`/Users/fran/code/repos/cloud_eval_backup/backup-2026-10-01T22-09-40-321Z`.
Relative to this repo: `../cloud_eval_backup/backup-2026-10-01T22-09-40-321Z/`.

| Artifact | Contents | Approximate compressed size |
| --- | --- | --- |
| `host-untracked.tar.gz` | 9,103 untracked/ignored host files from parent and submodule | 0.476 GB |
| `cloud-eval-image-originals.tar.gz` | Entire historical sibling image directory, including original archive | 1.058 GB |
| `medical-playground-medtech-cloud.tar.gz` | Exported original large derived image, not the new web-only image | 1.519 GB |
| `docker-config.tar.gz` | Consistent backup of the actual `/config` named volume | 0.012 GB |
| `manifest.json` | File inventory, source revisions, image/volume identities, recovery notes | About 1.1 MB |
| `SHA256SUMS` | Checksums of all four archives and the manifest | Small text file |

Total approximately **3.06 GB decimal / 2.9 GiB**. Archive listings and all five
checksums were verified. The demo was already stopped; the container was stopped
for the volume copy and then restarted. The backup directory has private access
permissions. Backups can contain licensed software, credentials, and private code.
They remain on this Mac; an off-machine copy in approved storage is still needed.

Verify before restoring:

```bash
cd /Users/fran/code/repos/cloud_eval_backup/backup-2026-10-01T22-09-40-321Z
shasum -a 256 -c SHA256SUMS
```

The host archive is not a full Git checkout: restore it over the recorded parent
and submodule revisions. Its macOS `.venv` and build artifacts are machine-specific;
do not copy them into Linux. Load the exported image with `docker load -i`.
Restore `docker-config.tar.gz` into a new named volume using the tar helper in the
runbook, substituting this filename for the runbook's `config.tar.gz`. Never
extract a backup over the live development volume. The backup manifest and these
instructions supersede earlier session notes saying no real volume backup exists.

## Current Docker runtime

- Container: `medical-playground`; running and healthy, demo left stopped.
- Image: `medical-playground:medtech-cloud-web`.
- Running image ID: `sha256:a528508d1e8f29139a4d6acb6a5c791a5b0bc3b4294e81fa33f370ef9a30cca6`.
- Docker-reported size: `7072172485` bytes (7.07 GB), down from slim's 8.11 GB.
  Added filesystem layers over the original base: `20504576` bytes (20.5 MB).
  These are storage/layer metrics, not compressed image download sizes.
- IDE: `http://127.0.0.1:8080/?folder=/config/workspace`.
- Port mapping: `127.0.0.1:8080 -> 8443/tcp`.
- Named volume: **`medical-playground-cloud-test-config`**, mounted at `/config`.
- Workspace inside container: `/config/workspace`.
- Docker Desktop stores this volume in its Linux VM, not a normal Finder folder.
- The original `medical-playground-config` volume was retained; do not confuse it
  with the currently mounted volume. Old test containers using 8081 were removed.
- Required tmpfs: `/run:rw,exec,uid=911,gid=1001,mode=0755` and
  `/tmp:rw,mode=1777`. Without `exec` on `/run`, s6 startup fails.
- Container user: `abc`, UID 911; configured group ID 1001.
- `NDDSHOME=/opt/rti.com/rti_connext_dds-current`.
- `CONNEXTDDS_ARCH=x64Linux4gcc8.5.0`; Connext Professional/Python 7.7.0.
- `MEDTECH_VENV=/opt/medtech-venv`, with system site packages reusing licensed RTI API.
- code-server CLI: `/app/code-server/bin/code-server`; data `/config/data`;
  extensions `/config/extensions`.
- Installed extension: `/config/extensions/rti.medtech-web-tabs-0.1.0`.

Host source and the source copied to `/config/workspace` are separate checkouts.
Host edits do not automatically appear in the container; IDE edits do not
automatically appear on the host. Compare/copy/commit deliberately. In particular,
the newly versioned `docker/` recipe was not automatically synchronized there.

The current image was rebuilt from the canonical `docker/` recipe and deployed
after a clean Linux application build and real DDS runtime validation. It does
not contain the old GUI/noVNC dependency stack. The Dockerfile provisions the
environment; application source/builds and extensions remain in `/config`.
This existing-volume deployment does not establish fresh-volume hosted acceptance.
Exact image identities are in `docker/baseline.json`; historical exported-image
identities remain in the external backup manifest.

Run in the IDE terminal, once:

```bash
cd /config/workspace
./tutorial/launch_all.sh
```

For emergency shutdown from a new IDE terminal:

```bash
cd /config/workspace
./tutorial/stop_all.sh
```

Accept Workspace Trust. Preinstall the bundled extension before opening a fresh
IDE session, as documented in the runbook, or reload the window after installation.
When multiple IDE windows exist, select the tutorial sidebar in the intended
window so it owns the URI bridge. Do not launch duplicate demos.

## Implementation details and resolved failures

- Cloud mode is the default; `--cloud` remains an alias. It uses `--vscode`
  device mode, not the superseded noVNC tutorial. Desktop VS Code requires the
  launcher flag `--vscode`; standalone browsers use `--web`.
- Device ports: Orchestrator 8090, Arm Controller 8091, Arm 8092, Patient Monitor
  8093. Patient Sensor is headless. Only IDE port 8080 is published.
- Device frames use `/proxy/8090/` through `/proxy/8093/`. Frontend API fetches are
  relative `api/...`, so they stay inside the code-server proxy prefix.
- Cloud URI dispatch uses atomic JSON files in
  `/tmp/medtech-web-tabs-<uid>/requests`. A focused/sidebar-visible extension-host
  owner prevents multiple code-server sessions from splitting the device grid.
- The native sidebar renders the same ten JSON steps. Open File uses the editor;
  it has no Restore controls. Orchestrator Start owns recovery, protected by
  health/startup guards. Closing a device editor terminates that device but keeps
  its empty grid slot reserved during the demo.
- Restored app launchers have detached process groups. Shutdown signals the whole
  group; signaling only the Python parent previously orphaned the Arm child.
- The stop script matches same-user processes by this checkout's real script or
  executable path, supports relative launchers and both build architectures, uses
  bounded TERM/KILL cleanup, and queues cloud panel closure. macOS can report the
  interpreter as capitalized `Python`; matching is case-insensitive.
- GTK headers were required by the superseded desktop builds, not the current
  web-only C++ apps. The cloud venv must not be replaced with the copied macOS venv.
- Old shared browser pages for noVNC on 8094 and standalone device tabs may still
  appear as attachments. They are leftovers, not the intended current interface.

## Historical dependency snapshot before web-only conversion

The following dependency/size discussion describes the original image, not the
current web-only runtime. The current image inventory and later conversion/
publication records supersede it; native device GUIs are no longer supported.

The current cloud experience consists of four headless HTTP servers/browser UIs,
plus Patient Sensor and the native VS Code tutorial view. It does not use X11
windows. Native mode still supports Qt/GTK desktop windows.

PySide6 is nevertheless required by current unconditional imports/class definitions
in `Arm.py` and `PatientMonitor.py`; Patient Monitor also imports pyqtgraph. The
C++ desktop and web implementations share binaries linked against GTK. Do not
simply uninstall GUI libraries and assume the web path will keep working.

`libllvm20` is a shared graphics-runtime dependency, not an explicitly installed
compiler requirement. The observed package chain is:
`libegl1 -> libegl-mesa0 -> mesa-libgallium -> libllvm20`.

Docker reported 7.05 GB for the base and 8.90 GB for the derived image. These
inspect/storage figures are not a clean accounting of added filesystem payload.
The two new filesystem layers total **1.400 GB**: APT approximately 692 MB and
Python approximately 709 MB. Largest Python file footprints are PySide6 Addons
438 MB and Essentials 237 MB. Largest added APT packages include LLVM 144 MB,
ICU development files 49 MB, Node shared library 48 MB, and Mesa Gallium 43 MB.
Do not claim the reported 1.86 GB image-size delta is all dependency payload.

Optimization was discussed but **not implemented**: separate desktop imports from
web backends, remove unused Xvfb/noVNC dependencies, and audit GTK/graphics linkage.
Preserve the known-working image and test web/native behavior before removing
dependencies. The recipe pins Python versions but does not freeze Ubuntu mirrors
or all transitive system packages; the image export is the exact binary fallback.

## Historical verification before web-only conversion

These counts belong to the original snapshot. For this session's focused checks
and their limitations, use the 2026-10-02 summary above.

- Live Linux build and generated Python types; all five DDS apps launched.
- Native sidebar, ten tutorial steps, four live UIs in the 2x2 grid, connected
  device status and updating patient vitals.
- Open File in the browser editor; Arm tab close/disconnect and Restore/reconnect.
- Restored process-group termination and duplicate-launch protection.
- Node extension tests: 9 passing.
- Launcher pytest tests: 8 passing.
- Tutorial unittest suite: 10 passing, including isolated stop-script subprocess
  behavior. Stop-script test also passed in Linux; unrelated apps remain running.
- Dockerfile static checks: no warnings; eleven Python pins match working image.
- Isolated volume backup/restore: matching file content and UID/GID.
- Actual backup: archive readability and SHA-256 verification passed.

Focused host test commands, from the repo root:

```bash
node --test medtech-reference-architecture/vscode-extension/extension.test.js
medtech-reference-architecture/.venv/bin/python -m pytest \
  medtech-reference-architecture/tests/test_launch.py -q
PYTHONPATH=tutorial medtech-reference-architecture/.venv/bin/python \
  -m unittest test_tutorial_gui
docker build --check --platform linux/amd64 -f docker/Dockerfile docker
```

The host test venv used Homebrew Python 3.14.5; the image uses Linux Python 3.12.
`rg` was unavailable in the host terminal; use workspace search or a fallback.

## Next session checklist

### Update after the original snapshot: image dependency reduction

On 2026-10-01, the canonical Dockerfile and requirements were reduced and a new
image built as **`medical-playground:medtech-cloud-slim`**. The original
`medical-playground:medtech-cloud` image, running container, live user demo, and
earlier verified backup were left intact. The earlier discussion above saying
optimization had not been implemented is superseded by this update.

- Removed explicit installs of Xvfb, x11vnc, noVNC, websockify, and associated
  desktop support packages. Some graphics libraries still arrive transitively.
- Removed the full `PySide6` metapackage and `PySide6_Addons`; retained
  `PySide6_Essentials`, shiboken6, and pyqtgraph because the current app imports
  still require them. No app source or native-mode branching was changed.
- GTK development dependencies remain for building the C++ binaries. LLVM 20
  remains in their Mesa/EGL dependency closure; it was not blindly uninstalled.
- Docker-reported size: **8.902 GB -> 8.113 GB**, saving **789 MB / 8.9%**.
- Added filesystem layers over base: **1.400 GB -> 0.830 GB**, saving **40.8%**.
- New image ID: `sha256:85b8527823f59261f16377241808950e8890b727077f03adb4dc3c62bcbb29f0`.
- Passed real Python imports with Addons absent, a fresh CMake/C++ build in a
  disposable copied workspace, and all five DDS apps on an isolated network:
  four HTTP APIs responded, all Orchestrator devices ON, fresh patient vitals.
- No fresh slim-image browser-IDE/sidebar/grid acceptance test yet. The active
  development container still uses the original image. New recipe/documentation
  changes were not automatically committed or pushed. The external backup does
  not contain the new slim image; export it separately after accepting it.

The refreshed runbook and baseline record these changes. Confirm current Git and
Docker state before assuming either image tag has subsequently been replaced.

### Subsequent deployment of the slim image

With user authorization, the live demo was stopped and `medical-playground` was
recreated using `medical-playground:medtech-cloud-slim`. The existing
`medical-playground-cloud-test-config` volume, environment, port 8080, and tmpfs
settings were preserved. The previous container remains stopped under the name
`medical-playground-pre-slim-2026-10-01T22-34-07-288Z`; it shares that volume, so
do not start it while the replacement is running.

The replacement's code-server health endpoint and dependency imports passed. The
full `launch_all.sh --cloud` workflow was started and verified: all four APIs
responded, all devices reported ON, and fresh patient data arrived. The smoke-test
apps were then stopped with `stop_all.sh`. The IDE remains running; reload the
browser page and launch once when ready. This supersedes earlier snapshot text
saying the active container still uses the original image. A fresh-volume
browser-sidebar/grid acceptance test and an export of the new slim image remain
separate follow-up work. Host recipe/runbook/handoff edits are not automatically
synchronized into the container's workspace or published to Git.

1. Read this handoff, the image runbook, and baseline; verify Git/Docker state.
2. See the publication update below for the committed web-only submodule and
  parent branch; older snapshot sections retain their historical Git state.
3. Copy the verified external backup to approved off-machine storage. Record its
   destination without committing credentials or private download URLs.
4. If testing a clean install, retain/rename the existing container and retain
   its named volume. Use a new volume, the original archive, and the canonical
   recipe; keep port 8080. Run the full acceptance checklist in the runbook.
5. Use the published web-only submodule pin in the current runbook. Older desktop
  source pins do not work with the web-only image.
6. Do not start a full demo merely to inspect source, or leave a test demo running
   before asking the user to launch another. Recheck state rather than trusting
   this snapshot indefinitely.

### Web-only conversion and deployment (pre-publication record)

The user authorized removing Module 01 desktop components. ArmController and
Orchestrator now compile and run only their existing HTTP/DDS classes, without
GTK or AppKit linkage. Arm and PatientMonitor retain their plain Python DDS/web
classes, without Qt widgets/timers, pyqtgraph, or NumPy. Servers start by default;
`--web` remains compatible, and `--port` remains supported. The tutorial launcher
uses the VS Code sidebar locally and in the cloud; `--native` fails explicitly.
The standalone Qt tutorial is retained as a legacy optional tool, not launched
or installed by the normal workflow. Module 04's unrelated desktop threat apps
remain supported through their own requirements file, outside the cloud image.

- Current image: `medical-playground:medtech-cloud-web`.
- ID: `sha256:a528508d1e8f29139a4d6acb6a5c791a5b0bc3b4294e81fa33f370ef9a30cca6`.
- Docker reported size: 7,072,172,485 bytes; 12.8% smaller than slim, 20.6% smaller
  than the original large derived image. Base alone remains 7.046 GB reported.
- Filesystem layers: 3,679,260,672 bytes; only 20,504,576 bytes added over base,
  97.5% less than slim's additions. These are not compressed download sizes.
- Final package inventory excludes Qt/PySide6/shiboken6, pyqtgraph, NumPy, GTK,
  Mesa/EGL/LLVM and VNC support.
- Fresh Linux cloud-helper build and GUI-free linkage passed. The real five-app
  default launch passed four APIs/assets, fresh DDS vitals, and pause/resume for
  sensor, arm and monitor on an isolated network.
- Deployed full cloud launcher passed browser checks: tutorial sidebar, four live
  2x2 editor views, devices ON, fresh patient data, and Arm close/OFF/Restore/ON.
- Apps and restored Arm were stopped afterward. IDE remains running on 8080.
- Previous slim container retained, stopped:
  `medical-playground-pre-web-2026-10-01T23-04-54-527Z`. All retained containers
  share the same volume; never run them concurrently.
- Pre-upgrade volume backup:
  `/Users/fran/code/repos/cloud_eval_backup/pre-web-2026-10-01T23-04-54-527Z/docker-config.tar.gz`.
  Archive listing verified; SHA-256
  `66067a12abf46c6092455f6b71eab5be24c390bc3f763c04471d0a3e41ee34c4`.
  Directory is private (0700). Image rollback alone does not restore volume files;
  restore this archive to a separate volume for exact pre-upgrade workspace state.
- The live volume selects its own existing submodule gitlink
  `8847f517bdcebff8ccecc908fdbcd0da851fff22`; it was preserved, with the web-only
  source/build overlaid. Do not assume it matches the host's published 4050cd3 pin.
- Source, recipe, and handoff changes are uncommitted/unpushed. The old published
  source needs Qt and is incompatible with this recipe without the documented
  overlay. Publish the submodule first, then its parent gitlink, when authorized.
- No fresh-volume hosted provisioning/cold-start measurement or exported backup
  of this new image yet. No prebuilt-startup redesign was added; the Dockerfile
  still provisions dependencies, while source and builds live in `/config`.

### Publication of the web-only changes

The user subsequently authorized committing and pushing these changes. The
MedTech submodule is published on GitHub `web-based-tutorial-apps` as
`1e18c2f94883f04c8be03b04b2e3758af3f2ec9f`. The parent commit containing this
update pins that revision and publishes the web-only image recipe, launcher,
runbook, baseline and this handoff to Bitbucket `develop`. The temporary source
overlay instructions have been removed; a clean pinned checkout now contains
the required web-only code. This supersedes the unpublished-source warnings above.

Unrelated host VS Code settings and the generated VSIX are intentionally not
committed. Docker images, licensed archives, and volume backups remain in local
authorized storage, not Git. Publication does not change the running container
or its existing-volume Git metadata; retain the deployment/rollback notes above.
