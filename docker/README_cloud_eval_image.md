# Clean installation: Digital Operating Room

This directory is the canonical home of the cloud image recipe. Run host commands
from this directory, normally `cloud_eval_medical/docker`. Obtain the original
`playground-20260709a.tar.gz` separately from authorized RTI storage and place it
here for the commands below. It is excluded from Git and the Docker build context.
Commands marked **IDE terminal** run inside the browser workspace. The browser IDE
always uses port **8080**.

## What is preserved here

- `Dockerfile`: base image, OS dependencies, virtual environment, and runtime defaults.
- `requirements.txt`: Python versions measured in the working Linux environment.
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

The derived image adds GTK build dependencies, Qt/Python dependencies, and
`/opt/medtech-venv`. It reuses the base image's licensed `rti.connext==7.7.0` via
system site packages. The Dockerfile retains Xvfb/noVNC dependencies from an
earlier approach, but the current tutorial does not use them. They have not been
removed as part of preserving the working setup.

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
  -t medical-playground:medtech-cloud .
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
  medical-playground:medtech-cloud
docker logs --tail 80 medical-playground
```

Keep the printed volume name for later recovery. The `exec` option on `/run` is
required by the image's s6 startup. Publish only the IDE port; device ports
8090-8093 are reached through code-server's authenticated proxy routes.

## 3. Install a fresh, pinned source checkout

Use a directory that does not already exist. This revision is the published
cloud-tutorial baseline; its submodule includes the native sidebar and grid:

```bash
git clone --branch develop \
  https://bitbucket.rti.com/scm/~fporcel/cloud_eval_medical.git \
  cloud_eval_medical-clean
git -C cloud_eval_medical-clean checkout --detach \
  6700ae02953c5b931fef39df2b9b1dc49a61cb41
git -C cloud_eval_medical-clean submodule update --init --recursive
git -C cloud_eval_medical-clean submodule status

docker exec --user root medical-playground mkdir -p /config/workspace
docker cp cloud_eval_medical-clean/. medical-playground:/config/workspace/
docker exec --user root medical-playground chown -R 911:1001 /config/workspace
```

The `medtech-reference-architecture` submodule revision should be
`4050cd3beba407a8cdef3ae65c0f04d995be7a25`, without a leading `+` or `-`.
The historical parent commit predates this `docker/` directory; retain your current
recipe checkout separately. To test a future tutorial revision, replace the parent
commit above with the reviewed commit and let it select its submodule revision.

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
  'import rti.connextdds, PySide6, pyqtgraph; print("Python dependencies OK")'
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
docker image inspect medical-playground:medtech-cloud --format '{{.Id}}' \
  > "$BACKUP_DIR/image-id.txt"
docker save medical-playground:medtech-cloud | gzip \
  > "$BACKUP_DIR/medical-playground-medtech-cloud.tar.gz"
docker stop medical-playground
docker run --rm --platform linux/amd64 --network none --user root \
  --entrypoint tar \
  --mount "type=volume,source=$CONFIG_VOLUME,target=/config,readonly" \
  --mount "type=bind,source=$BACKUP_DIR,target=/backup" \
  medical-playground:medtech-cloud -C /config -czf /backup/config.tar.gz .
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
docker load -i "$BACKUP_DIR/medical-playground-medtech-cloud.tar.gz"
RESTORED_VOLUME="medical-playground-restored-$(date +%Y%m%d-%H%M%S)"
docker volume create "$RESTORED_VOLUME"
docker run --rm --platform linux/amd64 --network none --user root \
  --entrypoint tar \
  --mount "type=volume,source=$RESTORED_VOLUME,target=/config" \
  --mount "type=bind,source=$BACKUP_DIR,target=/backup,readonly" \
  medical-playground:medtech-cloud -C /config -xzf /backup/config.tar.gz
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