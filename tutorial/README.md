# Digital Operating Room — Cloud Eval Tutorial (Draft)

This folder contains a draft "guided tutorial" for a future **Digital Operating Room**
workspace on [evaluation.rti.com](https://evaluation.rti.com/workspaces), built from
[rticonnextdds-medtech-reference-architecture](https://github.com/rticommunity/rticonnextdds-medtech-reference-architecture),
Module 01.

It mirrors the structure, tone, and step granularity of the existing **Publish-Subscribe**
cloud eval tutorial (Introduction → explore code → build/run → configure QoS → observe/visualize →
next steps), but tells a healthcare-specific story aimed at Healthcare/MedTech prospects.

## Files

- **`digital-or-tutorial.json`** — the 10-step tutorial content, in a portable schema
  (title/body/openFiles/terminals/highlights/etc.) so RTI's cloud eval platform team can
  map it onto the same accordion-panel format used by "Connext Studio" without needing to
  re-derive the narrative. This is the primary deliverable.
- **`INTEGRATION_NOTES.md`** — gaps and decisions the platform team needs to resolve before
  this can go live in the cloud sandbox (GUI apps, license/build step).
- **`../medtech-reference-architecture/`** — a local clone of the source repo, confirmed to
  build and run Module 01 end-to-end (see [INTEGRATION_NOTES.md](./INTEGRATION_NOTES.md)).
- **`run_digital_or.sh`** — one-command helper to set up, build, and launch the demo locally
  for showing this to stakeholders before any cloud integration work happens.
- **`tutorial_gui.py`** — a super-simple standalone PySide6 GUI that reads
  `digital-or-tutorial.json` and guides you through all 10 steps with Previous/Next
  navigation, buttons to open the referenced source files, and buttons to run each step's
  terminal commands in a new Terminal window. Stand-in for the real "Connext Studio" panel
  until this is wired into the cloud eval platform.

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
./run_digital_or.sh
```

This sources your local Connext 7.7 environment, creates/activates a venv, builds the C++ and
Python type support, and launches all 5 Digital Operating Room applications as native windows.

To open the four visual applications in VS Code editor tabs instead, install the bundled
[MedTech Web Tabs extension](../medtech-reference-architecture/vscode-extension/README.md)
and run:

```bash
./run_digital_or.sh --vscode
```

PatientSensor remains a background process. Add `--secure` to either command to enable Security.

## Guided tutorial GUI

```bash
pip install PySide6   # one-time, if not already installed
python3 tutorial_gui.py
```

Opens a window with a step list on the left (all 10 steps) and the step content on the right,
including "Open File" buttons (opens in VS Code if `code` is on your `PATH`, else your OS
default editor) and "Run in New Terminal" buttons for each step's build/run commands. Use it
side-by-side with `run_digital_or.sh` while walking through the tutorial.
