# Module 01 Cleanup Plan

Date: 2026-10-05

## Scope

Make this a Module 01-only, web-based branch, preserving its five applications,
device-grid extension, and optional DDS Security support.

At planning time, the submodule checkout is `web-based-tutorial-apps`, not
`web-apps`. Confirm the intended branch before implementation; leave upstream
`main` untouched. This document is a plan, not a record of completed changes.

## Implementation Plan

### 1. Remove Modules 02-04 and Their Dependencies

Delete their source, tests, configuration, documentation, and dedicated images.
Remove their CMake targets, scenarios, pytest paths, CI steps, recording/replay
identities, WAN profiles, teleoperation security artifacts, and unused NAT
tooling. Update the System Designer project and architecture documentation.

Preserve Module 01's operational security configuration, trusted CAs, secure-log
reader, and test identities. Remove shared helpers only when no retained code
uses them.

**Validation gate:** A clean build discovers only Module 01, generates its Python
types, and launches all five applications. Retained configuration contains no
dangling references to removed modules.

### 2. Establish Reproducible Dependencies

Pin the RTI CMake utilities to a reviewed commit. Pin extension-packaging tools
and introduce a transitive Python dependency lock with hashes for the supported
cloud platform. Identify the licensed base image immutably and document the
supported Connext, compiler, Python, and architecture combinations.

Add a maintained JSON dependency, preferably `nlohmann/json`, pinned with an
archive checksum. Distinguish reproducible dependency resolution from
byte-identical builds.

**Validation gate:** Fresh environments resolve the same dependencies; normal
startup never fetches a moving branch or an unspecified tool version.

### 3. Fix Subprocess Ownership and Cleanup

Update [module_runner.py](../medtech-reference-architecture/resource/python/scripts/module_runner.py)
so partial spawning, callback failures, interrupts, and other exceptions clean
up every successfully started child. Preserve the original exception, terminate
gracefully, escalate after a bounded timeout, and wait after killing to reap
processes. Apply the same behavior to any retained multi-launch path.

**Validation gate:** Tests cover failure on the second spawn, callback exceptions,
interruption during startup, and children that ignore termination. No owned
processes survive; unrelated processes remain untouched.

### 4. Eliminate C++ Data Races

Synchronize every shared status access in Arm Controller and Patient Sensor.
Introduce explicit stop coordination, guarantee worker-thread joining on every
exit path, and avoid holding application mutexes while publishing DDS data.
Keep signal handlers limited to signal-safe shutdown notification.

**Validation gate:** Repeated Start/Pause/Shutdown and concurrent HTTP/DDS
activity pass an instrumented ThreadSanitizer run. Document proprietary-library
limitations separately rather than broadly suppressing reports.

### 5. Replace Handwritten JSON Handling

Use the pinned parser for request decoding and response serialization. Require
a top-level object with endpoint-specific fields, exact types, permitted enum
values, and real booleans. Reject malformed input, duplicate keys, unexpected
fields, and nested substitutes.

Validate the JSON media type, allowing its standard parameters, and impose a
small command-body limit, initially 4 KiB. Return consistent `400`, `415`, and
`413` responses without publishing DDS commands.

**Validation gate:** Parser/API tests cover whitespace, escaping, malformed JSON,
wrong types, duplicate fields, unknown commands, and oversized bodies.

### 6. Make Polling Failures Visible and Recoverable

Apply consistent handling across all four frontends: treat unsuccessful HTTP
responses as failures, add request timeouts, and allow only one outstanding
poll. Use bounded retry backoff and distinguish disconnected, stale,
reconnecting, and explicitly stopped states.

Freeze patient waveforms when data becomes stale or transport fails. Resume
after fresh data returns; temporary network errors must not permanently mark a
running application as shut down.

**Validation gate:** Tests exercise repeated `503` responses, hung requests,
invalid responses, delayed/reordered results, disconnect/reconnect, and explicit
shutdown.

### 7. Verify Startup Before Reporting Success

Check C++ listen results and unwind worker threads on bind failure. Make the
supervisor detect early child exits and return meaningful errors.

After setup, make the background launcher wait for a configurable readiness
deadline: all owned children alive, four valid APIs responding, Patient Sensor
heartbeat observed, and fresh patient data received. A listening port alone is
insufficient. On failure, clean up that launch's processes and report the log
location.

**Validation gate:** Occupied ports, missing binaries/types, invalid licenses,
delayed readiness, and early exits produce nonzero results without leaving
orphan processes.

### 8. Replace Desktop Assumptions With Headless Tests

Remove obsolete GUI markers, display-based skips, GTK/Qt dependencies, and Xvfb
setup from the retained Module 01 test path. Add the regressions above to
existing suites and retain real DDS/security integration coverage.

Run parser, launcher, and frontend tests without a display or license. Run
licensed end-to-end tests separately on Linux, including grid recovery and
scoped stop/restart.

**Validation gate:** Headless execution does not silently skip web applications;
failures and prerequisite-based skips are clearly distinguished.

### 9. Repair Public Documentation and Publication Pins

Update clone commands to `https://github.com/franporcel/rti_cloud_eval_medtech`,
the public parent branch, and the confirmed submodule branch. Rewrite
instructions around Module 01 only. Remove obsolete desktop and other-module
guidance.

Make pin checks derive the expected submodule SHA from the parent gitlink
instead of copying historical SHAs into instructions. After authorized
publication, publish the submodule first, then update the parent gitlink and
validate a fresh recursive clone.

**Validation gate:** Follow the public local and cloud instructions from clean
checkouts; verify build, readiness, fresh data, pause/resume, recovery, and
complete shutdown.

## Completion Criteria

Deliver these as reviewable batches, validating each before the next. The final
acceptance run must use a fresh Linux workspace, preserve optional secure mode,
and demonstrate both successful startup and clean failure recovery.

Authentication hardening and cross-workspace extension isolation remain separate
findings outside this requested plan.
