# Plan: Web-Based Orchestrator (Digital OR Module)

## Goal
Convert the *Orchestrator* app (currently C++/GTK) into a web-accessible UI as a
proof of concept, while keeping the existing native GTK app fully working
(dual support). If successful, apply the same pattern to the other GUI apps
(PatientMonitor, Arm, ArmController) later.

## Scope (this iteration)
- **App**: Orchestrator only.
- **Out of scope for now**: PatientMonitor, Arm, ArmController remain native
  GUI apps, untouched. PatientSensor stays headless, untouched.

## Architecture

### Single process, dual mode
- Modify `Orchestrator.cxx` to support two run modes, selected by a CLI flag
  (e.g. `--web`):
  - **Default (current behavior)**: native GTK window, unchanged.
  - **`--web` mode**: no GTK window. Same DDS participant, same
    `DeviceHeartbeat` / `DeviceStatus` / `DeviceCommand` subscription and
    state-tracking logic, but instead of rendering to GTK widgets, it:
    1. Embeds a lightweight HTTP + WebSocket server (e.g.
       [`cpp-httplib`](https://github.com/yhirose/cpp-httplib) with its
       WebSocket-via-`ws` add-on, or a small vendored single-header WS
       library) directly in the same process.
    2. Serves a static HTML/JS/CSS page (device status grid, command buttons,
       alerts panel) from an `Orchestrator/web/` asset folder.
    3. Pushes state updates (status changes, new alerts) to connected
       browsers over WebSocket as JSON messages.
    4. Accepts command requests from the browser (Start/Shut Down per
       device) over the same WebSocket (or a POST endpoint), and forwards
       them into the existing internal command-publishing code path
       (same DDS writer already used by the GTK version) — no separate DDS
       participant needed.
  - Both modes share the same underlying `OrchestratorLogic`/state class;
    only the presentation layer differs. This requires a small refactor to
    extract the current GTK-coupled state/business logic into a
    UI-agnostic class if it isn't already separated (needs a read of
    `Orchestrator.cxx` before implementation to confirm current structure).

### Why single-process (per your answer)
Avoids an extra IPC hop (sockets/shared memory) between a bridge process and
a headless C++ app — the same binary just swaps its front-end. Simpler to
build, ship, and reason about; still isolated from GTK when compiled/run in
`--web` mode.

### Frontend
- Plain HTML/CSS/JS, no build step, no framework — served as static assets
  next to the C++ source (matches "keep dependencies minimal" spirit and
  avoids adding a JS toolchain to a C++ module).
- Layout closely mirrors current GTK window: device status list/grid,
  per-device command buttons, "Alerts" scrolling panel.
- WebSocket client reconnects automatically on drop; initial state fetched
  via a `GET /api/state` on load, then live-patched via WebSocket.

## launch.py integration
- Add a `--web` flag (or per-app override) to `launch.py` that, when
  launching Orchestrator, passes `--web` to the executable instead of the
  default native-GTK invocation.
- On launch in web mode, the script auto-opens the default browser to
  `http://localhost:<port>` (port fixed/configurable, e.g. `8090`).
- Native GTK Orchestrator remains the default when `--web` is not passed —
  no behavior change for existing usage.

## Cloud eval (evaluation.rti.com) hosting

**Researched finding**: evaluation.rti.com workspaces run **code-server**
(confirmed from prior session — VS Code web IDE). code-server has built-in
port-forwarding for arbitrary local ports via:
- Subpath proxy: `https://<workspace-host>/proxy/<port>/...`
- Or the VS Code web "Ports" panel, which auto-detects a listening port and
  offers an "Open in Browser" link.

This is a strong signal that a local HTTP/WebSocket server on a fixed port
inside the workspace container *should* be reachable from the browser via
`/proxy/<port>/`, the same mechanism used to preview any local web app in
VS Code for the Web / code-server. **However**, this is not yet verified
against the specific evaluation.rti.com deployment** (it may have custom
proxy/ingress restrictions, and we don't control the platform config).

**Open risk / action item**: before relying on this for the tutorial, we
need someone with evaluation.rti.com access to:
1. Start any trivial local HTTP server on a workspace terminal
   (`python3 -m http.server 8090`).
2. Confirm it's reachable via the Ports panel / `/proxy/8090/` from the
   browser tab.
3. Confirm WebSocket upgrade requests are proxied correctly (not just plain
   HTTP), since our live-update mechanism depends on it.

If this doesn't work, fallback options (in order of preference):
- SSE (Server-Sent Events) instead of WebSocket — many proxies handle
  plain HTTP streaming more reliably than WS upgrades.
- Short-poll `GET /api/state` every 1–2s from the browser (simplest,
  least elegant, guaranteed to work through any HTTP proxy).

## Files to add/change
- `medtech-reference-architecture/modules/01-operating-room/src/Orchestrator.cxx`
  — add `--web` mode branching, extract shared state logic if needed.
- `medtech-reference-architecture/modules/01-operating-room/src/web/`
  (new) — `index.html`, `app.js`, `style.css` (RTI-branded).
  Also a small embedded HTTP/WS server helper, e.g.
  `OrchestratorWebServer.h/.cxx`, and vendored single-header dependency
  (e.g. `cpp-httplib`) under `modules/01-operating-room/src/third_party/`.
- `medtech-reference-architecture/modules/01-operating-room/CMakeLists.txt`
  — add new source files / vendored header include path.
- `medtech-reference-architecture/launch.py` — add `--web` flag handling.
- `medtech-reference-architecture/modules/01-operating-room/README.md` —
  document the new `--web` flag and cloud-eval-style flow.
- No changes to `requirements.txt` needed for this app (it's C++); only the
  vendored C++ header lib is new.

## Testing plan
- Manual smoke test: `python3 launch.py 01-operating-room --web Orchestrator`
  (or similar), confirm browser opens, device statuses populate, Start/Shut
  Down buttons produce the same DDS effects as the GTK version (verified via
  the other native apps still reacting correctly).
- Automated: add a Playwright test that starts Orchestrator in `--web` mode,
  loads the page, waits for at least one device status to render, clicks a
  command button, and asserts the resulting alert/status text appears.
- Regression: confirm default (no `--web`) invocation still opens the
  native GTK window unchanged.

## Tutorial step impact
- The eventual cloud-eval "Run the Applications" step would, for
  Orchestrator, link a browser tab (via `/proxy/<port>/`) instead of
  describing a native window — better fit for a browser-only sandboxed
  environment.
- Other 4 apps stay as-is (native/no-UI) until/unless this pattern is
  extended to them in a future iteration.

## Open questions / follow-ups for later iterations
- If PoC succeeds, decide whether to convert PatientMonitor/Arm (Python) and
  ArmController (C++) using the same single-process dual-mode pattern.
- Decide fixed port allocation scheme if multiple apps eventually run their
  own embedded web servers simultaneously (port collisions).
- Confirm whether evaluation.rti.com's ingress imposes any request size/
  connection-count limits relevant to WebSocket keep-alives.
