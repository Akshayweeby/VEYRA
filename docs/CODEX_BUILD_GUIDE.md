# VEYRA --- Codex Build Guide

This file tells Codex how to build VEYRA in controlled, testable stages.
Do not ask Codex to generate the entire product in one pass.

## 1. Instructions for Codex

You are implementing VEYRA, a Windows hand-gesture laptop controller.
Treat `PROJECT_PLAN.md`, `GESTURE_AND_STATE_SPEC.md`, and
`TECHNICAL_RESEARCH.md` as the source of truth.

### Mandatory engineering rules

-   Do not change confirmed product requirements without asking.
-   Do not silently expand v1 scope.
-   Do not claim performance targets are met without measured results
    from real hardware.
-   Do not implement the final engine choice before benchmark results
    exist.
-   Do not store webcam images/video or send camera data over a network.
-   Camera must be OFF at startup.
-   Every camera-on attempt requires confirmation.
-   Camera OFF must stop capture/inference and release the webcam.
-   Never block the Qt UI thread with camera reads or inference.
-   Use a latest-frame-only buffer; no unbounded queues.
-   Use explicit state machines and session tokens to reject stale
    callbacks.
-   All discrete gesture actions require confidence, stability,
    neutral-release and cooldown checks.
-   Always release mouse buttons on drag timeout, camera stop, exception
    and app exit.
-   Add unit tests and integration tests at every stage.
-   Keep dependencies pinned after compatibility testing.
-   Include a license/notice inventory before distribution.

## 2. Suggested repository layout

``` text
veyra/
├── README.md
├── pyproject.toml
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── benchmark.txt
├── assets/
│   ├── branding/
│   │   ├── wordmark.svg
│   │   └── orbital_icon.svg
│   └── models/
│       └── README.md
├── src/
│   └── veyra/
│       ├── __init__.py
│       ├── main.py
│       ├── app/
│       │   ├── state_controller.py
│       │   ├── camera_lifecycle.py
│       │   └── action_dispatcher.py
│       ├── ui/
│       │   ├── hud/
│       │   ├── settings/
│       │   ├── setup/
│       │   └── diagnostics/
│       ├── capture/
│       │   ├── camera_adapter.py
│       │   ├── camera_enumerator.py
│       │   └── latest_frame_buffer.py
│       ├── recognition/
│       │   ├── engine_interface.py
│       │   ├── mediapipe_engine.py
│       │   ├── onnx_engine.py
│       │   └── performance_monitor.py
│       ├── gestures/
│       │   ├── geometry.py
│       │   ├── classifier.py
│       │   ├── stability.py
│       │   ├── neutral_gate.py
│       │   └── state_machine.py
│       ├── actions/
│       │   ├── windows_input.py
│       │   ├── cursor.py
│       │   ├── scroll.py
│       │   ├── chrome_tabs.py
│       │   ├── volume.py
│       │   └── custom_actions.py
│       ├── data/
│       │   ├── settings.py
│       │   ├── history.py
│       │   └── diagnostics.py
│       └── platform/
│           ├── hotkeys.py
│           └── windows_camera.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── hardware/
│   └── fixtures/
├── benchmarks/
│   ├── README.md
│   ├── run_benchmark.py
│   └── results/
├── packaging/
│   ├── pyinstaller/
│   └── installer/
└── docs/
    ├── PROJECT_PLAN.md
    ├── GESTURE_AND_STATE_SPEC.md
    ├── TECHNICAL_RESEARCH.md
    └── CODEX_BUILD_GUIDE.md
```

## 3. Development phases

### Phase 0 --- Repository and environment

Deliver: - Python project scaffold and virtual environment
instructions. - Pinned dependency strategy. - Logging setup with
local-only sinks. - CI/unit test baseline. - `THIRD_PARTY_NOTICES.md`
template. - No camera opening and no input injection yet.

Exit gate: - App imports and starts a placeholder Qt window. - Tests run
on supported Windows environment. - No network activity from app
runtime.

### Phase 1 --- UI shell and branding

Deliver: - VEYRA orbital icon and angular wordmark. - Cyan/graphite
theme. - Floating HUD, always-on-top, draggable, transparency slider. -
Collapse/expand behaviour and remembered position. - Small/Medium/Large
size presets. - Minimal/Detailed layouts. - Settings window with left
sidebar. - HUD only on startup; camera OFF. - First-launch setup wizard
shell, skippable.

Exit gate: - UI remains responsive. - No camera is opened. - No worker
thread leaks. - UI state is testable without hardware.

### Phase 2 --- Camera adapter and privacy lifecycle

Deliver: - Camera enumeration prototype. - Test MSMF and DSHOW backends
on target webcams. - Camera selection and device persistence. - Explicit
open/close lifecycle. - Camera confirmation popup every time camera
turns ON. - Camera OFF releases device. - Guided errors and diagnostics.

Exit gate: - Repeated ON/OFF cycles release webcam every time. - App
exit releases webcam. - Camera denial and unplug tests show actionable
recovery. - Camera OFF means zero capture/inference calls.

### Phase 3 --- Recognition benchmark harness

Deliver: - Common engine interface. - MediaPipe Tasks adapter. - ONNX
Runtime CPU adapter with an explicitly licensed model. - Native C++
benchmark prototype only if practical. - Same input/test protocol for
every candidate. - 30-second setup benchmark. - Detailed benchmark
report with accuracy, FPS, latency, CPU, RAM, startup, dropped frames
and stability. - Engine selection score with hard gates.

Exit gate: - Reproducible results on target hardware. - No engine chosen
based only on external benchmark claims. - Manual override and
restart-required behaviour work. - If no engine passes, show warning and
developer override.

### Phase 4 --- Landmark geometry and gesture classifier

Deliver: - One-hand selection, handedness/override support. - Landmark
normalization. - Gesture geometry and candidate classifier. - Stability
filter, neutral gate, cooldown. - Conflict resolution and confidence
rejection. - Test Mode with optional landmark debug overlay.

Exit gate: - Offline recorded test clips classify supported gestures
with documented metrics. - False positives measured on ordinary hand
movement. - No action injection yet.

### Phase 5 --- State machine and action safety

Deliver: - Camera/controller state model. - Fist pause/open-palm
resume. - Gesture Lock. - Hand-lost behaviour. - Session token to reject
stale callbacks. - Drag safety timeout and button-release guard. - Unit
tests for every state transition.

Exit gate: - State transitions match `GESTURE_AND_STATE_SPEC.md`. - No
action can dispatch when camera OFF, paused, locked, hand lost, or
exiting. - Interrupted drag always releases within 500 ms.

### Phase 6 --- Windows actions

Deliver in this order: 1. Cursor relative movement and smoothing. 2.
Left click via pinch. 3. Drag via 400 ms pinch hold. 4. Scroll. 5.
Chrome tab switching with foreground check. 6. Master volume via Core
Audio. 7. Custom keyboard shortcut mappings and application launch.

Exit gate: - Test on non-elevated and elevated windows; document UIPI
limitations. - Chrome actions never fire when Chrome is not
foreground. - All held inputs are released on every error/stop/exit
path. - Volume changes by exactly two normalized control points per
gesture.

### Phase 7 --- Settings, diagnostics and recovery

Deliver: - Local JSON settings and one backup. - Corrupt-settings
recovery. - Auto-save ordinary settings; Apply for camera/engine
changes. - Gesture enable/disable and sensitivity controls. - 50-entry
history and clear confirmation. - 30-day diagnostic log retention. -
Diagnostic ZIP/report export. - Feedback and bug-report flow with
explicit diagnostic approval. - Calibration suggestions after repeated
quality degradation.

Exit gate: - Data remains local. - No media files are created. -
Logs/history obey retention caps. - Export contains no webcam
images/video.

### Phase 8 --- Performance adaptation and compatibility

Deliver: - Adaptive resolution and frame skipping. - Gradual recovery
when stable. - Camera diagnostics and compatibility report. -
Performance-first setup wizard. - 30-second benchmark. - Basic user
benchmark and advanced developer benchmark.

Exit gate: - Test on low-end reference hardware. - Report measured
CPU/RAM/FPS/latency. - Do not label a device compatible unless it passes
defined thresholds.

### Phase 9 --- Packaging and alpha

Deliver: - PyInstaller onedir application. - Per-user installer EXE. -
Portable folder/ZIP. - AppData vs portable-local data paths. -
Uninstaller preserve/delete prompt. - Crash report and safe restart
offer. - Unsigned development build first; signing before public
release.

Exit gate: - Clean-machine tests without Python installed. - Camera
works after install and portable launch. - Uninstall data choice
works. - No admin permission required for per-user installation.

### Phase 10 --- Private alpha → public beta → v1.0

Private alpha: - Internal users only. - Focus on false positives, camera
lifecycle, drag safety, and resource use.

Public beta: - Controlled external testers. - Feedback and diagnostics
are opt-in. - Fix reliability and compatibility defects.

v1.0: - Release only after performance, privacy, packaging, licensing
and safety gates pass. - Code-sign installer and executable. - Publish
release notes and supported-hardware caveats.

## 4. Codex prompt sequence

Use one prompt at a time. Require Codex to summarize changes, list files
changed, run tests, and state any unverified assumptions.

### Prompt 1 --- Scaffold

> Read all VEYRA planning documents. Create only the Phase 0 repository
> scaffold, project metadata, pinned-dependency placeholders, logging,
> and test structure. Do not implement webcam access, gesture
> recognition, or input injection. Add a README with Windows setup
> instructions. Run tests and report exact results.

### Prompt 2 --- UI shell

> Implement Phase 1 only. Build the VEYRA cyan/graphite PySide6 HUD and
> settings shell according to the product plan. The app must launch
> HUD-only with camera OFF and no camera imports that initialize a
> device. Add UI tests where feasible. Do not implement camera capture
> or gesture actions.

### Prompt 3 --- Camera lifecycle

> Implement Phase 2 only. Prototype camera enumeration and MSMF/DSHOW
> backend compatibility, implement a single-owner camera adapter and
> explicit ON/OFF lifecycle, confirmation popup, guided errors and
> deterministic release. Add repeated open/close, unplug, denied-access
> and shutdown tests. Do not implement gesture actions.

### Prompt 4 --- Benchmark harness

> Implement Phase 3 only. Add the common recognition-engine interface
> and benchmark harness. Implement MediaPipe Tasks first, then ONNX
> Runtime CPU using a model whose license and model card are documented.
> Do not hard-code a winner. Use identical test inputs and report
> accuracy, FPS, latency, CPU, RAM, warm-up, dropped frames and
> stability. Only prototype native C++ if the first candidates need
> comparison.

### Prompt 5 --- Gesture classifier

> Implement Phase 4 only. Use the chosen engine adapter to generate
> landmarks, then implement geometric gesture classification,
> confidence, stability, neutral gating, cooldown and conflict
> rejection. Build offline tests and a Test Mode. Do not inject OS input
> yet.

### Prompt 6 --- State and safety

> Implement Phase 5 only. Follow the exact state machine in
> GESTURE_AND_STATE_SPEC.md. Add session-generation checks, hand-loss
> behaviour, fist pause/open-palm resume, HUD Gesture Lock, drag timeout
> and idempotent mouse-button release. Add comprehensive transition
> tests. No real OS action injection yet.

### Prompt 7 --- Windows actions

> Implement Phase 6 only. Add SendInput-based cursor, click, drag,
> scroll and Chrome tab actions, plus Core Audio master volume. Enforce
> foreground checks, state guards, error checking and guaranteed input
> release. Add safe test mode and document UIPI limitations.

### Prompt 8 --- Settings and diagnostics

> Implement Phase 7 only. Add local JSON settings, backups, history, log
> retention, diagnostic exports and user-approved bug-report
> attachments. Confirm no webcam media is persisted or exported.

### Prompt 9 --- Performance and setup

> Implement Phase 8 only. Add adaptive resolution/frame skipping,
> gradual restoration, compatibility report, 30-second performance-first
> setup wizard and developer benchmark. Do not claim 24 FPS unless
> measured on designated hardware.

### Prompt 10 --- Packaging

> Implement Phase 9 only. Create PyInstaller onedir build, per-user
> installer EXE and portable distribution. Implement AppData and
> portable-local storage rules, uninstaller preserve/delete choice,
> crash report and clean-machine tests. Keep the development build
> unsigned; document code-signing requirements for public release.

## 5. Required test matrix

-   Windows 10 supported build(s) and Windows 11.
-   8 GB RAM low-end CPU reference device.
-   Integrated webcam and at least one external USB webcam.
-   Camera permission allowed/denied.
-   Camera unplug/replug.
-   Camera ON/OFF repeated cycles.
-   Low light, backlight, bright light and cluttered background.
-   Left and right hand.
-   Hand lost and reacquired.
-   Fist pause and open-palm resume.
-   Gesture Lock while active and while paused.
-   Pinch click, drag, drag interrupted, camera OFF during drag, app
    exit during drag.
-   Chrome foreground/background.
-   Multi-monitor cursor movement.
-   Volume near 0 and 100.
-   Hotkey conflict and registration failure.
-   Settings corruption and backup recovery.
-   Installed and portable storage paths.
-   Clean machine without Python.

## 6. Definition of done for each Codex task

Codex must report: 1. What changed and why. 2. Files created/modified.
3. Tests added. 4. Exact test commands and results. 5. Performance
measurements if relevant. 6. Known limitations. 7. Any requirements that
remain unimplemented. 8. Whether webcam access, network access, or OS
input injection was introduced.

Never accept "works perfectly" without reproducible evidence.
