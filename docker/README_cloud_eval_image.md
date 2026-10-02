# Clean installation: Digital Operating Room

This directory is the canonical home of the cloud image recipe. Run host commands
from this directory, normally `cloud_eval_medical/docker`. Obtain the original
`playground-20260709a.tar.gz` separately from authorized RTI storage and place it
here for the commands below. It is excluded from Git and the Docker build context.
Commands marked **IDE terminal** run inside the browser workspace. The browser IDE
always uses port **8080**.

## What is preserved here

- `Dockerfile`: base image, OS dependencies, virtual environment, and runtime defaults.
- `requirements.txt`: pinned Python versions for the web-only Module 01 apps.
- `baseline.json`: original archive checksum, image identities, source revisions,
  observed APT versions, and the working runtime/volume configuration.
- `.dockerignore`: only the Dockerfile and requirements enter the build context.
- This runbook: clean installation, acceptance checks, backups, and recovery.

The historical `../cloud_eval_image` directory is no longer the source of truth.
Keep future image changes here and commit/push them with the tutorial changes.
The current development volume is `medical-playground-cloud-test-config`; do not
remove it when performing a clean-install test.

## Prerequisites and files to share

- Docker Engine or Docker Desktop running Linux containers. On Apple Silicon,
  enable support for `linux/amd64` images; the Connext binaries are x86-64.
- Git, access to the private Bitbucket repository below, and access to its GitHub
  submodule. Authenticate through your normal Git credential setup.
- Internet access for Ubuntu packages, Python packages, and the first CMake build.
- Authorized access to the original Playground archive and a valid Connext 7.7
  license for the deployment. An SDK import check alone does not validate a license.
- Share this Git repository and the original archive through authorized storage.
  Do not put licensed SDK/image archives, credentials, or workspace backups in Git.

### Original archive versus derived image

`playground-20260709a.tar.gz` is the original base-image archive. We did not modify
or repack it, and no archive changes are needed for this tutorial. `docker load`
reads it; `docker build` creates a separate derived image from
`rti-playground:20260709a` using the updated Dockerfile.

The derived image adds Python venv support and `/opt/medtech-venv`. It reuses the
base image's licensed `rti.connext==7.7.0` via system site packages. Module 01's
device backends are web-only: neither GTK nor Qt is needed to compile or run them.
The final image inventory excludes Qt/PySide6/shiboken6, pyqtgraph, NumPy, GTK,
Mesa/EGL/LLVM, Xvfb, x11vnc, noVNC, and websockify. Module 04's separate desktop
apps remain outside this cloud image; install their own requirements to use them.

### Web-only deployment

`medical-playground` now uses `medical-playground:medtech-cloud-web`, preserving
the existing `/config` volume, environment, and port 8080. Docker reports
7,072,172,485 bytes, down from the slim image's 8,113,184,327 bytes (12.8% smaller).
Added filesystem layers over the base are only 20,504,576 bytes, down from
829,644,800 bytes (97.5% smaller). The original base dominates the remaining size;
these are storage/layer metrics, not compressed registry downloads.

A clean cloud-helper build and real five-app runtime passed, including all four
APIs/assets, fresh DDS vitals, and pause/resume commands. The deployed launcher
also passed browser verification of the tutorial sidebar, four live 2x2 editor
views, and Arm tab-close/Restore. Test apps were stopped; the IDE remains running.
This was an existing-volume test, not a fresh-volume hosted provisioning test.

The previous slim container is stopped as
`medical-playground-pre-web-2026-10-01T23-04-54-527Z`. All retained containers share
the same volume; never run them concurrently. The pre-upgrade volume was backed
up to authorized local storage; its location and checksum are in `baseline.json`.
An image rollback alone does not restore workspace source. Restore that volume
backup to a separate volume for exact pre-upgrade workspace recovery.

The parent pins published web-only submodule commit
`5ef04beefcef94cfa387704e2ebd0591d4d5da24`; no source overlay is needed for that
revision. Older desktop source pins are incompatible with this recipe. The
Dockerfile deliberately does not bundle source, executables, or extensions;
prebuilt startup remains future work. Use the web tag consistently to retain
the historical image tags.

### Historical slim-image reduction

The reduced recipe was built as `medical-playground:medtech-cloud-slim`, leaving
the running `medical-playground` container and its original image tag unchanged.
Docker reported 8,901,996,245 bytes before and 8,113,184,327 bytes after: a reduction
of 788,811,918 bytes (8.9%). Added filesystem layers over the original base dropped
from 1,400,389,632 to 829,644,800 bytes (40.8% smaller). These storage/layer metrics
are not compressed archive sizes.

Validation included real Python app imports with Addons absent, a fresh CMake/C++
build via the cloud setup helper, and all five DDS apps on an isolated Docker
network. All four HTTP APIs responded, all devices reported ON, and Patient
Monitor received fresh vitals. The existing user demo was not stopped or modified.
The browser sidebar/grid was not re-tested in a fresh slim-image IDE session.

The original exported image backup contains the historical image, not the slim
or web-only images. See `baseline.json` for their separate identities.

The local `medical-playground` container was subsequently recreated on the slim
image, retaining `medical-playground-cloud-test-config`, the environment, and port
8080. Its health endpoint and full cloud launcher passed (four APIs, connected
devices, fresh vitals); test apps were stopped afterward. Reload the browser IDE
and launch once when ready. The previous container is retained, stopped, as
`medical-playground-pre-slim-2026-10-01T22-34-07-288Z`. Both containers reference
the same workspace volume: never run them simultaneously. This retained-container
upgrade is not a fresh-volume browser-UI acceptance test.

The demo source, bundled VS Code extension, Linux executables, and generated Python
types live in the container's `/config` volume, **not** in the original archive.
Do not copy a host's `.venv` or build directory into a clean Linux installation.

## 1. Load the original archive and rebuild

Verify the archive matches the supplied copy before loading it. This SHA-256 was
recorded on 2026-10-01; it identifies our copy, not an independent vendor signature:

```bash
printf '%s  %s\n' \
  70b8ecddd05e927644390f4bffd25d3302a841a02a25c14aaeacba7011debfa1 \
  playground-20260709a.tar.gz | shasum -a 256 -c -
docker load -i playground-20260709a.tar.gz
docker image inspect rti-playground:20260709a \
  --format '{{.Os}}/{{.Architecture}} {{.Id}}'
docker build --no-cache --platform linux/amd64 \
  -t medical-playground:medtech-cloud-web .
```

The base image must report `linux/amd64`, with the identity in `baseline.json`.
If the archive loads under a different tag, use its actual tag as
`--build-arg PLAYGROUND_BASE=<loaded-tag>` when building; do not replace it with an
unrelated image. On Linux hosts without `shasum`, use `sha256sum -c -` for the same
checksum check.

Python versions are pinned, but Ubuntu repositories, transitive system packages,
and package availability can change. The observed APT versions are an audit record,
not a frozen repository. Rebuilding also produces a different image ID than the
historical image in `baseline.json`. For exact binary recovery, keep an exported
derived image and its checksum in authorized storage, as described below.

## 2. Create a fresh container and volume

Check for existing containers and anything using port 8080:

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

If an old `medical-playground` exists, stop it and rename it before continuing.
Its workspace volume is preserved. Choose a backup name not already in use:

```bash
docker stop medical-playground
docker rename medical-playground medical-playground-backup
```

Skip those two commands on a new machine. If another service owns port 8080, stop
that service first; do not move this tutorial to port 8081.

Use a **new** volume name each time you test a clean installation. Reusing a
volume carries over source, extensions, settings, and build outputs. Run the
following block in the same host shell:

```bash
MEDTECH_CONFIG_VOLUME="medical-playground-clean-$(date +%Y%m%d-%H%M%S)"
docker volume create "$MEDTECH_CONFIG_VOLUME"
docker run -d --name medical-playground \
  --platform linux/amd64 \
  -p 127.0.0.1:8080:8443 \
  --mount "type=volume,source=$MEDTECH_CONFIG_VOLUME,target=/config" \
  --tmpfs /run:rw,exec,uid=911,gid=1001,mode=0755 \
  --tmpfs /tmp:rw,mode=1777 \
  medical-playground:medtech-cloud-web
docker logs --tail 80 medical-playground
```

Keep the printed volume name for later recovery. The `exec` option on `/run` is
required by the image's s6 startup. Publish only the IDE port; device ports
8090-8093 are reached through code-server's authenticated proxy routes.

## 3. Install a fresh, pinned source checkout

Use a directory that does not already exist. Pin the clean clone to the parent
revision of this reviewed recipe checkout; its submodule includes the web-only
apps, native sidebar, and grid. Run from this runbook's `docker/` directory:

```bash
REVIEWED_PARENT_REVISION=$(git -C .. rev-parse HEAD)
git clone --branch develop \
  https://bitbucket.rti.com/scm/~fporcel/cloud_eval_medical.git \
  cloud_eval_medical-clean
git -C cloud_eval_medical-clean checkout --detach \
  "$REVIEWED_PARENT_REVISION"
git -C cloud_eval_medical-clean submodule update --init --recursive
git -C cloud_eval_medical-clean submodule status

docker exec --user root medical-playground mkdir -p /config/workspace
docker cp cloud_eval_medical-clean/. medical-playground:/config/workspace/
docker exec --user root medical-playground chown -R 911:1001 /config/workspace
```

The `medtech-reference-architecture` submodule revision should be
`5ef04beefcef94cfa387704e2ebd0591d4d5da24`, without a leading `+` or `-`.
Record `REVIEWED_PARENT_REVISION` with the image build so later clones reproduce
the same source rather than following a moving branch tip. A future reviewed
parent revision may intentionally select a different submodule commit.

Preinstall the bundled extension **before opening the browser IDE for the first
time**:

```bash
docker exec --user abc medical-playground /bin/bash -c '
  src=/config/workspace/medtech-reference-architecture/vscode-extension
  dst=/config/extensions/rti.medtech-web-tabs-0.1.0
  mkdir -p "$dst"
  cp "$src"/{package.json,extension.js,tutorial-view.js,tutorial.svg} "$dst"/
'

docker exec --user abc medical-playground /opt/medtech-venv/bin/python -c \
  'import rti.connextdds, argcomplete, stun, requests; print("Python dependencies OK")'
```

## 4. Open the IDE and launch once

Open <http://127.0.0.1:8080/?folder=/config/workspace> and accept Workspace Trust
for this known project. Use the base image's configured login if prompted; do not
disable authentication. If you opened the IDE before installing the extension,
run **Developer: Reload Window** before launching.

**IDE terminal:**

```bash
cd /config/workspace
./tutorial/launch_all.sh --cloud
```

The first launch builds Linux C++ applications and generated Python types. Leave
its terminal open. The launcher automatically uses `/opt/medtech-venv`; do not
create a replacement virtual environment or install another Connext wheel.
The Digital Operating Room activity icon opens the native tutorial side panel.
If it is missing, reload the window. Use one IDE window for the initial test;
select the tutorial icon in the intended window if multiple windows are open.

No desktop `code` CLI, Node package installation, noVNC display, or additional
published port is needed. This is a bundled tutorial view, not a registered hosted
Connext Studio template.

## 5. Clean-install acceptance checks

- The tutorial contains ten steps in the native VS Code side panel.
- Arm Controller, Arm, Orchestrator, and Patient Monitor occupy a 2x2 editor grid.
  Patient Sensor is headless; all five DDS applications should be running.
- The Orchestrator reports connected devices, and patient vitals update.
- A tutorial **Open File** action opens the file in the editor, not an external tab.
- Closing the Arm device editor stops that app and the Orchestrator reports the
  disconnect. **Restore** restarts only Arm and restores the four-panel grid.
- Ctrl+C in the launch terminal stops the demo, including restored devices, and
  closes its device panels. Run the launcher again to verify a second clean start.

If the original terminal is lost, use a new **IDE terminal**:

```bash
cd /config/workspace
./tutorial/stop_all.sh
```

The stop script targets only this checkout's processes owned by your user and
leaves Docker and the browser IDE running. It is safe to run when already stopped.
Do not start a second demo while the first is running. For a ports-in-use error,
stop the existing demo before retrying; do not kill unrelated services by port.

## Preserve changes during iteration

- Commit and push source edits from `/config/workspace`, including submodule changes
  in the submodule first and then its updated parent gitlink.
- Put dependency changes in this Dockerfile and requirements file, not just in a
  running container. Rebuild and recreate the container to use a changed image.
- Reuse the same named `/config` volume for development. Use a new volume for
  clean-install tests. Do not delete old volumes or run volume pruning.
- Keep the original archive, tested derived-image exports, and workspace-volume
  backups in authorized, backed-up storage outside this Git repository. Git alone
  cannot restore these artifacts. Record their checksums and storage location in
  your team's handoff record without including credentials or signed access URLs.

### Back up both image and workspace

The image export does **not** include `/config`. This host-shell procedure exports
the image and makes a consistent volume backup by briefly stopping the container.
Run `./tutorial/stop_all.sh` in the IDE terminal first. These archives may contain
licensed software, credentials, and private source; restrict access and copy them
to approved storage. The commands below are a manual procedure, not automatically
run by installation:

```bash
set -euo pipefail
BACKUP_DIR="$HOME/medical-playground-backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
CONFIG_VOLUME=$(docker inspect medical-playground --format \
  '{{range .Mounts}}{{if eq .Destination "/config"}}{{.Name}}{{end}}{{end}}')
test -n "$CONFIG_VOLUME"
printf '%s\n' "$CONFIG_VOLUME" > "$BACKUP_DIR/volume-name.txt"
docker image inspect medical-playground:medtech-cloud-web --format '{{.Id}}' \
  > "$BACKUP_DIR/image-id.txt"
docker save medical-playground:medtech-cloud-web | gzip \
  > "$BACKUP_DIR/medical-playground-medtech-cloud-web.tar.gz"
docker stop medical-playground
docker run --rm --platform linux/amd64 --network none --user root \
  --entrypoint tar \
  --mount "type=volume,source=$CONFIG_VOLUME,target=/config,readonly" \
  --mount "type=bind,source=$BACKUP_DIR,target=/backup" \
  medical-playground:medtech-cloud-web -C /config -czf /backup/config.tar.gz .
docker start medical-playground
(cd "$BACKUP_DIR" && shasum -a 256 *.tar.gz > SHA256SUMS)
printf 'Backup directory: %s\n' "$BACKUP_DIR"
```

If backup fails after stopping the container, fix the failure and restart it;
do not remove the original volume. The backup helper overrides the image entrypoint
and publishes no ports. On Linux, `sha256sum` can replace `shasum -a 256`.

To restore on a new machine, obtain the backup directory, verify the checksums, load
the derived image, and extract the workspace into a **new** volume:

```bash
set -euo pipefail
BACKUP_DIR=/absolute/path/to/the/backup-directory
(cd "$BACKUP_DIR" && shasum -a 256 -c SHA256SUMS)
docker load -i "$BACKUP_DIR/medical-playground-medtech-cloud-web.tar.gz"
RESTORED_VOLUME="medical-playground-restored-$(date +%Y%m%d-%H%M%S)"
docker volume create "$RESTORED_VOLUME"
docker run --rm --platform linux/amd64 --network none --user root \
  --entrypoint tar \
  --mount "type=volume,source=$RESTORED_VOLUME,target=/config" \
  --mount "type=bind,source=$BACKUP_DIR,target=/backup,readonly" \
  medical-playground:medtech-cloud-web -C /config -xzf /backup/config.tar.gz
printf 'Restored volume: %s\n' "$RESTORED_VOLUME"
```

Use the step 2 `docker run` command with that restored volume name instead of
creating another clean volume. Restored code-server data may contain old session
state; reload the IDE if needed. Do not publish the backup directory in Git.

## Rebuilds and recovery

Rebuilding an image does not change an existing container. Recreate the container
to use a new image. For an upgrade, retain the existing `/config` volume; for a
clean-install test, create a new one. Do not delete volumes or use `docker system
prune` as a prerequisite for this procedure.

To return to the saved container, stop and remove only the new container, then
restore the backup name. This keeps both containers' named volumes intact:

```bash
docker stop medical-playground
docker rm medical-playground
docker rename medical-playground-backup medical-playground
docker start medical-playground
```

Use the backup name chosen in step 2 if it differs. After acceptance checks, export
the tested derived image and record the recipe Git revision, both tutorial Git
revisions, checksums, and results. Never overwrite the original archive. A derived
image recipient can skip rebuilding, but must copy source/install the extension
or restore the workspace volume; neither is included in a plain image export.

Keep the Docker port bound to localhost. A hosted deployment must retain the
platform's authentication in front of every proxy route; set `MEDTECH_CLOUD_URL`
in the container environment **before code-server starts** if its external origin
is not `http://127.0.0.1:8080`.
