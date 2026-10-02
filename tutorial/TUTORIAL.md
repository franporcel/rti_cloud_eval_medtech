# Digital Operating Room

## Overview

This example shows how RTI Connext connects the devices in a modern operating room -- patient monitors, a surgical robotic arm, and a central orchestrator -- using the same data-centric publish-subscribe model you've already learned, applied to a real medical device architecture.

### You Will Learn

- How a single data-centric architecture (defined once, in XML) connects heterogeneous devices written in different languages (C++ and Python)
- How Connext QoS policies (Deadline, Reliability, Content Filters) map directly to patient-safety requirements
- How to detect a failed or disconnected medical device in real time, without any custom heartbeat code
- How to observe and safely control a live system of interacting medical devices

## 1. Introduction

Connext lets every device in a medical system share data by publishing and subscribing to well-defined Topics -- the same pattern you saw in the Publish-Subscribe tutorial, now applied to a safety-critical environment.

In a real hospital, an operating room is a network of independent devices -- vitals monitors, surgical robots, infusion pumps -- built by different vendors, on different platforms, that must interoperate reliably. RTI Connext is designed exactly to help resolve problem.

### Background

- The MedTech Reference Architecture defines all system Data Types, QoS, Domains, and Topics once in XML, separate from application code and language.
- Applications discover each other automatically and exchange data peer-to-peer -- no broker, no single point of failure.
- The same architecture scales from a single-machine demo to devices distributed across a hospital network.

### What We'll Build

Go ahead and launch the applications:

```sh
[Button: ./tutorial/launch_all.sh]
```

You can see 4 interactive Operating Room applications:

- Patient Monitor -- subscribes to vitals and displays a live waveform
- Arm -- a simulated 5-motor surgical robot arm
- Arm Controller -- sends motor commands and shows system alerts
- Orchestrator -- monitors every device's health and can start/stop devices remotely
- Patient Sensor -- publishes simulated patient vitals. This is an application that runs in the bacground with no GUI

> **Note:** This workspace runs everything on a single machine for simplicity, but Connext works identically across a real hospital network, across operating systems, and across vendors.

## 2. Explore the System Architecture

Just like the DeviceStatus type in the Publish-Subscribe tutorial, every piece of data exchanged in the operating room is described by a structured Data Type, defined once in XML.

### Open Files

- `[Button: Open [system_arch/Types.xml](../medtech-reference-architecture/system_arch/Types.xml)]`
- `[Button: Open [system_arch/qos/Qos.xml](../medtech-reference-architecture/system_arch/qos/Qos.xml)]`
- `[Button: Open [system_arch/xml_app_creation/ParticipantLibrary.xml](../medtech-reference-architecture/system_arch/xml_app_creation/ParticipantLibrary.xml)]`

### Highlights

- Vitals -- a patient's collected vital signs (heart rate, blood pressure, SpO2, ...)
- MotorControl -- commands the direction of motion for an arm motor (Base, Shoulder, Elbow, Wrist, Hand)
- DeviceStatus / DeviceHeartbeat -- the current state and liveliness of any device in the room
- DeviceCommand -- remote commands such as `Start`, `Pause`, `Shut Down` sent to a specific device

**Key Takeaway:** Because these types, QoS, and participant configurations are defined in XML -- not hard-coded per application -- a systems architect can change system behavior (e.g. reliability, filtering) without touching a single line of C++ or Python.

## 3. Explore the Patient Vitals Data Flow

The terminal-based Patient Sensor simulates a bedside monitor publishing vitals. The Patient Monitor subscribes to the same Topic and renders a live waveform -- exactly the publish/subscribe pattern from the first tutorial, now carrying real medical telemetry.

### Open Files

- `[Button: Open [modules/01-operating-room/src/PatientSensor.cxx](../medtech-reference-architecture/modules/01-operating-room/src/PatientSensor.cxx)]`
- `[Button: Open [modules/01-operating-room/src/PatientMonitor.py](../medtech-reference-architecture/modules/01-operating-room/src/PatientMonitor.py)]`

**Highlight:** Notice that the publisher is written in C++ and the subscriber in Python -- they interoperate seamlessly because they share the same Connext data type, generated once from `[Button: Open [Types.xml](../medtech-reference-architecture/system_arch/Types.xml)]`.

## 4. Explore the Surgical Arm Control Flow

The Arm Controller sends motor-movement commands; the Arm application receives them and animates 5 simulated motors. This models the safety-critical command path between a surgeon's console and a robotic instrument.

### Open Files

- `[Button: Open [modules/01-operating-room/src/ArmController.cxx](../medtech-reference-architecture/modules/01-operating-room/src/ArmController.cxx)]`
- `[Button: Open [modules/01-operating-room/src/Arm.py](../medtech-reference-architecture/modules/01-operating-room/src/Arm.py)]`

**Highlight:** In a real surgical robot, this command path has hard real-time and reliability requirements -- exactly what Connext QoS is designed to guarantee (see Step 7).

## 5. Explore the Orchestrator

The Orchestrator is the room's system supervisor. It watches every device's DeviceHeartbeat and DeviceStatus, and can issue DeviceCommands (`Start`, `Pause`, `Shut Down`) to any device by name.

### Open Files

- `[Button: Open [modules/01-operating-room/src/Orchestrator.cxx](../medtech-reference-architecture/modules/01-operating-room/src/Orchestrator.cxx)]`

**Highlight:** This is the pattern behind hospital-wide device management: one application can supervise many independent, vendor-built devices without any of them needing custom integration code.

## 6. Explore the Running Digital Operating Room

The launch command has already set up, built, and started all five applications. Explore the four GUIs; Patient Sensor runs headless.

### Expected Result

4 device editor tabs in a 2x2 grid show Arm Controller and Orchestrator above Arm and Patient Monitor. The tutorial remains this Markdown file; there is no tutorial panel. For desktop VS Code, launch with `[Button: ./tutorial/launch_all.sh --vscode]`; `--web` is the ordinary browser-tab fallback. Patient Sensor runs headless in the background.

### Try This

- From the Orchestrator, send a `Pause` command to the Patient Sensor. Watch the Patient Monitor pause, then resume it with `Start`.
- From the Arm Controller, stop all motors, then resume just the Elbow motor and nudge the Wrist with the +/- buttons.
- From the Orchestrator, send `Start` to the Arm, then `Start` to resume it.
- Close the Arm device editor tab to stop its process. Notice how the Orchestrator reports it as `OFF` when its heartbeats stop. Closing an ordinary browser tab in `--web` mode does not stop its application.
- Select Arm in Orchestrator and click `Start` to relaunch it and reopen its editor tab. To restart the entire demo, run:

```sh
[Button: ./tutorial/restart_all.sh]
```

## 7. Configure Patient-Safety QoS

Just like the Reliable QoS step in the Publish-Subscribe tutorial, this system relies on QoS policies -- not application code -- to guarantee safety-critical behavior.

### Open Files

- `[Button: Open [system_arch/qos/Qos.xml](../medtech-reference-architecture/system_arch/qos/Qos.xml)]`

### Highlights

- Deadline QoS on `t/DeviceHeartbeat` (200 ms) -- the Orchestrator is notified the instant a device stops responding, with zero custom timeout code.
- StrictReliable QoS -- no vitals or motor commands are ever silently dropped.
- Content-Filtered Topics on `t/DeviceCommand` -- each device only receives commands addressed to it, using a single shared Topic.

### Try This

- Increase the Heartbeat Deadline period to 5 seconds on both the `<datawriter_qos>` and the `<datareader_qos>` and restart the demo to apply the change.

    ```sh
    [Button: ./tutorial/restart_all.sh]
    ```

    - Close the Patient Monitor device editor tab to stop its process. Observe the Orchestrator's offline alert after the new deadline, then select Patient Monitor and click `Start` to recover it. In `--web` mode, terminate its verified PID instead and restart the demo afterward.
- Comment out the `<content_filter>` for `dr/DeviceCommand` under `dp/PatientMonitor` in `[Button: Open [ParticipantLibrary.xml](../medtech-reference-architecture/system_arch/xml_app_creation/ParticipantLibrary.xml)]`, restart, and send a `Shut Down` command to only the Arm Controller -- notice the Patient Monitor also shuts down, because it's no longer filtering commands meant for other devices. Content-Filter Topics allow you to filter out data based on its content!

**Key Takeaway:** These are the exact QoS levers a systems engineer tunes to move from a lab prototype to a certifiable, patient-safe deployment -- without changing application code.

## 8. Observe the System with RTI Tools

Because Connext is data-centric, tools can introspect your running system without any custom code.

### Actions

- Open RTI Admin Console or System Designer and connect to the running Domain to see every DomainParticipant, Topic, DataWriter, and DataReader in the Digital Operating Room.
- Open `[Button: Open [system_arch/RefArch.rtisdproj](../medtech-reference-architecture/system_arch/RefArch.rtisdproj)]` in RTI System Designer to see the full architecture (all 4 modules) as a single diagram.

> **Cloud Eval Note:** In the cloud eval workspace, this step should reuse the same 'Visualize System' and 'Create View with AI' actions from the Publish-Subscribe tutorial, pointed at the DeviceStatus/Vitals/MotorControl topics (e.g. an AI-generated Operating Room Dashboard card per device).

## 9. Simulate a Real-World Failure

While watching the Orchestrator's Alerts panel, close the Arm device editor tab. This stops its process and heartbeats. Wait for the disconnect alert, then select Arm and click `Start` to restart that device and reopen its tab. Keep Orchestrator open to observe the failure and recovery. In `--web` mode, terminate the verified Arm PID instead and restart the demo afterward.

To compare with a graceful stop, send `Shut Down` to the Arm Controller from Orchestrator and observe its status change. Select Arm Controller and click `Start` to bring it back without restarting the other devices.

**Key Takeaway:** This is one of the key selling points of Connext for healthcare buyers: Connext turns device failure detection and safe shutdown into a QoS-and-architecture concern, not bespoke integration code per device vendor.

## 10. Next Steps

Congratulations! You've seen how the fundamentals from the Publish-Subscribe tutorial -- Topics, data types, QoS -- scale up to a real, safety-critical medical device architecture.

Ready to build your own connected medical device? Install Connext to get the SDK, design & debug tools, and infrastructure services for recording, bridging, and securing your data.
