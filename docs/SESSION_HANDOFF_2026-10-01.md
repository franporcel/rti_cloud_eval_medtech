# Cloud evaluation session handoff

Snapshot: 2026-10-01. Read this before rebuilding, cleaning Docker, or changing the
cloud tutorial. Runtime state can change after this snapshot; verify it first.

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
| Parent | Local `main` tracks Bitbucket `origin/develop` | `68ca7b5604cab35b7de04645ebf0960b546f2cc8` |
| MedTech submodule | `web-based-tutorial-apps`, GitHub origin | `4050cd3beba407a8cdef3ae65c0f04d995be7a25` |

Parent origin: `ssh://git@bitbucket.rti.com:7999/~fporcel/cloud_eval_medical.git`.
Submodule origin:
`https://github.com/rticommunity/rticonnextdds-medtech-reference-architecture.git`.

Published commits from this session:

- Submodule `4050cd3`: cloud URI bridge, native tutorial sidebar, proxy-compatible
  device UIs, editor-grid ownership and restore lifecycle, regression tests.
- Parent `6700ae0`: cloud launcher/environment support, process cleanup, emergency
  stop script, tests, tutorial documentation, updated submodule gitlink.
- Parent `68ca7b5`: versioned image recipe, pinned Python versions, baseline,
  clean-install/backup runbook, Git/build-context exclusions, root README links.

Because the parent local branch name differs from its upstream, publication used
`git push origin HEAD:develop`, not an assumed `main` remote branch. Push submodule
changes before publishing the parent gitlink. Do not commit generated archives,
credentials, or unrelated editor settings. This handoff itself was added after
`68ca7b5`; it is not part of that published revision.

## Canonical files in this workspace

| Path | Purpose |
| --- | --- |
| `docker/Dockerfile` | Canonical derived-image recipe, explicitly `linux/amd64` |
| `docker/requirements.txt` | Eleven Python pins matching the working Linux environment |
| `docker/baseline.json` | Archive checksum, image IDs, source revisions, observed APT versions, runtime settings |
| `docker/README_cloud_eval_image.md` | Clean-install instructions, acceptance checks, image and volume backup/restore |
| `docker/.dockerignore` | Only Dockerfile and requirements enter the build context |
| `.gitignore` | Excludes caches, archives, VSIX, `.env`, and `rti_license.dat` |
| `tutorial/launch_all.sh` | Full tutorial launch; cloud selection, setup, extension installation, duplicate-launch guard |
| `tutorial/run_digital_or.sh` | Setup/build/demo helper; uses `MEDTECH_VENV` when supplied |
| `tutorial/stop_all.sh` | Executable emergency stop for this checkout's apps and restored/orphaned devices |
| `tutorial/digital-or-tutorial.json` | Shared ten-step tutorial content |
| `tutorial/tutorial_gui.py` | Separate local PySide6 tutorial; not used by cloud mode |
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
| `medical-playground-medtech-cloud.tar.gz` | Exported working derived Docker image | 1.519 GB |
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

- Container: `medical-playground`; running after backup, demo left stopped.
- Image: `medical-playground:medtech-cloud`.
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

The working image was built from the historical sibling recipe, **not rebuilt
from the new pinned recipe**. Both recipes retain the earlier GUI/noVNC packages.
The new requirements' eleven versions match the running environment, but this
does not establish a full clean-install acceptance result. Exact image identities
are in `docker/baseline.json` and the external backup manifest.

Run in the IDE terminal, once:

```bash
cd /config/workspace
./tutorial/launch_all.sh --cloud
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

- Cloud mode is explicit via `--cloud`, or detected in a headless code-server
  image. It uses `--vscode` device mode, not the superseded noVNC tutorial.
- Device ports: Orchestrator 8090, Arm Controller 8091, Arm 8092, Patient Monitor
  8093. Patient Sensor is headless. Only IDE port 8080 is published.
- Device frames use `/proxy/8090/` through `/proxy/8093/`. Frontend API fetches are
  relative `api/...`, so they stay inside the code-server proxy prefix.
- Cloud URI dispatch uses atomic JSON files in
  `/tmp/medtech-web-tabs-<uid>/requests`. A focused/sidebar-visible extension-host
  owner prevents multiple code-server sessions from splitting the device grid.
- The native sidebar renders the same ten JSON steps. Open File uses the editor.
  Restore is disabled before a full launch, during a startup guard, and when device
  health is healthy or unknown. Closing a device editor terminates that device.
- Restored app launchers have detached process groups. Shutdown signals the whole
  group; signaling only the Python parent previously orphaned the Arm child.
- The stop script matches same-user processes by this checkout's real script or
  executable path, supports relative launchers and both build architectures, uses
  bounded TERM/KILL cleanup, and queues cloud panel closure. macOS can report the
  interpreter as capitalized `Python`; matching is case-insensitive.
- GTK headers were absent from the original base and are needed to build the two
  C++ apps. The cloud venv must not be replaced with the copied macOS venv.
- Old shared browser pages for noVNC on 8094 and standalone device tabs may still
  appear as attachments. They are leftovers, not the intended current interface.

## Web versus desktop dependencies and size

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

## Verification completed

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

### Subsequent web-only conversion and deployment

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
