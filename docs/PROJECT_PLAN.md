# VEYRA --- Project Plan and Product Requirements

**Tagline:** The Future Is in Your Hands.\
**Brand direction:** Futuristic and intelligent; minimal geometric
wordmark; angular typography; orbital-motion icon; cyan and graphite
palette.\
**Document status:** Baseline specification for implementation planning.

## 1. Product vision

VEYRA is a lightweight Windows application that lets a user control
selected laptop functions through deliberate hand gestures captured by a
webcam. The product should feel like a polished, premium interaction
utility: fast to activate, unobtrusive, predictable, privacy-preserving,
and usable on modest Windows laptops.

VEYRA is not intended to replace the keyboard and mouse. It provides a
small set of deliberate, discoverable gesture controls for selected
actions.

## 2. Goals

-   Control the mouse cursor, scroll, click/drag, Chrome tabs, and
    Windows master volume using one hand.
-   Maintain a compact always-visible floating HUD.
-   Keep the camera and all recognition processing OFF until explicitly
    enabled.
-   Keep all inference local and all user data on the local machine.
-   Minimize CPU/RAM use and avoid stale-frame latency.
-   Benchmark multiple recognition implementations before selecting the
    default engine.
-   Provide installer and portable distributions.

## 3. Non-goals for v1

-   Two-hand gestures.
-   Media playback controls (play/pause/next/previous).
-   General Windows desktop shortcuts and window management.
-   Browser support beyond Chrome.
-   Cloud inference, accounts, telemetry, remote processing, or webcam
    media storage.
-   User-defined new gesture shapes or custom ML training.
-   Arbitrary scripts or shell commands as custom actions.

Approved custom actions are limited to built-in actions, user-defined
keyboard shortcut mappings, and launching applications. This narrow
capability does not expand v1 into general desktop/window management.

## 4. Supported environment and constraints

  Requirement            Baseline
  ---------------------- ----------------------------------------------------
  OS                     Windows 10 and Windows 11
  Minimum target class   Intel Core i3 / AMD Ryzen 3 class or better
  RAM target             8 GB
  Language               English only
  UI                     Python + PySide6
  Camera                 User-selectable webcam; default camera preselected
  Tracking               One hand in v1
  Target rate            24 FPS
  Privacy                Fully local; no image/video recording
  Normal runtime         Offline
  Update check           Explicit user action only
  Launch                 Manual; no autostart
  Packaging              Per-user installer EXE and fully portable build

The hardware class is a target for testing, not a promise that all
devices in that class will meet 24 FPS. Integrated graphics, camera
drivers, thermal limits, background processes, lighting, and
model/runtime versions can materially affect results.

## 5. Confirmed application behaviour

### 5.1 Startup and camera lifecycle

-   Launch into the floating HUD only.
-   Camera starts OFF.
-   No camera capture, inference, or gesture processing occurs while
    OFF.
-   Camera ON is initiated from the HUD button or the configured
    activation hotkey.
-   Every camera-on attempt requires a small confirmation popup near the
    HUD with Confirm and Cancel.
-   The activation hotkey is initially `Ctrl+Shift+Space`; user may
    customize it.
-   If already active, activation shortcut shows a brief "already
    active" notification.
-   The pause shortcut is customizable. It turns the camera OFF and
    releases the webcam.
-   If the camera is already OFF, the pause shortcut shows "camera
    already OFF".
-   After keyboard pause, camera restart is through the HUD Camera ON
    button, with confirmation. Do not add a separate resume hotkey.
-   Fist gesture pauses gesture actions while keeping the camera ON.
    Open palm resumes.
-   Gesture Lock is controlled only through the HUD. It blocks
    gesture-triggered actions while camera/tracking may remain on for
    status.
-   Emergency Stop in the HUD immediately turns camera OFF and releases
    it. Restart is only through the HUD Camera ON button.
-   Closing VEYRA exits immediately, releases the camera, releases any
    held mouse button, stops workers, saves safely, and leaves no
    tray/background process.

### 5.2 Camera selection and recovery

-   Camera selector in Settings; default camera preselected.
-   Changing camera releases the previous device immediately. New device
    remains OFF until user enables it and confirms.
-   Default hand selection is automatic; user may lock left or right
    hand.
-   Use camera auto-exposure where supported and software adaptation
    where appropriate.
-   If camera access is denied or the device fails, show guided recovery
    with likely cause, Retry, and Camera Settings.
-   Provide a camera diagnostic report: availability, chosen device,
    requested/actual resolution, measured FPS, lighting estimate, hand
    detection and tracking stability.
-   Respect Windows camera privacy settings. Never bypass denied access.

### 5.3 HUD and visual identity

-   VEYRA name and tagline: "The Future Is in Your Hands."
-   Angular futuristic wordmark; minimal geometric identity.
-   Icon concept: orbital motion symbol.
-   Palette: cyan and graphite.
-   HUD concept: orbital interface.
-   Gesture recognition feedback is text-only; no recognition animation.
-   Always-on-top, draggable, transparent/adjustable opacity.
-   Initial location: top-right of primary monitor. Remember last
    manually selected position.
-   Size presets: Small, Medium, Large. No manual edge resizing.
-   Collapse into a tiny indicator; clicking restores the full HUD.
-   Collapsed HUD shows camera/controller status and quick Camera ON/OFF
    control; no FPS.
-   Expanded HUD supports Minimal and Detailed layouts.
-   Detailed HUD includes camera state, controller state, recognized
    gesture, last action, FPS and key live statistics.
-   HUD status on fist pause changes to PAUSED text only; do not change
    the whole appearance.
-   HUD remains visible until app exits.
-   Settings has a modern left sidebar: General, Camera, Gestures,
    Performance, Appearance, Developer.
-   Settings changes: ordinary values auto-save; camera/engine changes
    require Apply. Show restart-required state where relevant.
-   First launch goes directly into setup wizard; wizard is skippable.
-   Initial setup is performance-first: compatibility check → 30-second
    benchmark → engine selection → camera configuration → calibration →
    gesture practice → final performance verification.
-   If benchmark candidates fail: recommend against normal use but allow
    Advanced Developer Mode override with a clear warning.

### 5.4 Performance behaviour

-   Benchmark at least MediaPipe Tasks, ONNX Runtime CPU with a suitable
    hand-landmark model, and a native C++ alternative/prototype where
    feasible.
-   Select default using a weighted overall score, subject to minimum
    accuracy and responsiveness gates.
-   Metrics: steady-state FPS, frame-to-result latency, CPU, process
    RAM, startup/warm-up time, hand/gesture accuracy, dropped frames,
    and thermal/long-run stability.
-   Target 24 FPS.
-   Start with a low capture resolution (320×240 candidate) and increase
    only when quality requires it. The exact default must be measured;
    320×240 is a starting hypothesis, not a fixed guarantee.
-   Latest-frame-only queue; do not accumulate stale frames.
-   If FPS drops below target, reduce resolution and increase frame
    skipping; notify if still poor.
-   Restore resolution and processing frequency gradually after
    sustained stability.
-   Separate UI, capture, and tracking/inference work. Never block the
    Qt UI thread with capture or inference.
-   Use one hand only and avoid camera preview outside setup/test mode.
-   No inference when camera OFF, gesture-paused, or in states where
    processing is not required. Gesture Lock may retain minimal tracking
    only if needed for HUD status; do not execute actions.
-   Detailed benchmark mode for developers; basic performance statistics
    for normal users.

### 5.5 Privacy and data

-   All camera frames and landmarks remain in memory.
-   Do not save or upload images/video.
-   No cloud inference, accounts, telemetry, analytics, or background
    network calls.
-   Runtime works offline after installation.
-   Manual update check is the only planned normal network action;
    downloading/installing requires user approval.
-   Settings stored as local JSON.
-   Installed build stores settings/logs/history in the user's AppData.
-   Portable build stores settings/logs/history beside its executable.
-   Diagnostic logs retained for 30 days.
-   Local activity history stores last 50 recognized gestures/actions
    with timestamps only; no images/video. Automatically cap at 50;
    provide Clear History with confirmation.
-   Diagnostic export: ZIP logs and a complete diagnostic report
    including hardware, benchmark, configuration and logs. Exclude
    webcam media and personal content.
-   Detailed bug report attaches diagnostics only after user approval.
-   On crash: stop workers and release camera, save local crash report,
    offer restart; do not auto-restart.

## 6. Version 1 action inventory

  -----------------------------------------------------------------------
  Gesture                 Default action          Guard / condition
  ----------------------- ----------------------- -----------------------
  Pointing (index up,     Relative cursor         Cursor movement
  other fingers folded)   movement                enabled; hand tracked

  Pinch                   Left click              Cursor synchronized to
                                                  pinch location; one
                                                  click per deliberate
                                                  pinch

  Pinch held              Drag                    Enter drag after 400
                                                  ms; movement controls
                                                  cursor; release pinch
                                                  ends drag

  Two fingers             Continuous vertical     Hand movement controls
                          scroll                  direction/speed;
                                                  adjustable base speed
                                                  and movement
                                                  acceleration

  Horizontal swipe left   Next Chrome tab         Chrome must be
                                                  foreground; minimum
                                                  distance and speed

  Horizontal swipe right  Previous Chrome tab     Chrome must be
                                                  foreground; minimum
                                                  distance and speed

  Three fingers raised,   Master volume +2        One change per
  move up                 percentage points       deliberate gesture

  Three fingers raised,   Master volume −2        One change per
  move down               percentage points       deliberate gesture

  Open palm               Resume after fist       Only when in
                          gesture pause           gesture-paused state

  Fist                    Temporarily pause       Camera remains ON
                          gesture actions         
  -----------------------------------------------------------------------

The gesture set contains more than five action families because volume,
pause/resume, cursor, click/drag, scroll and swipe are all explicitly
approved. Do not silently remove approved controls to force a
five-gesture limit.

### 6.1 Cursor and multi-monitor behaviour

-   Relative cursor movement: hand moves right → cursor moves right.
-   Movement active only while pointing gesture is stable.
-   Cursor speed adjustable.
-   Balanced smoothing with low latency and a small dead zone.
-   Cursor may move across all connected monitors.
-   If hand disappears, freeze cursor at last position and suspend
    gesture actions.
-   On hand return, require neutral/new deliberate gesture before
    resuming actions.

### 6.2 Browser and system actions

-   Chrome only in v1.
-   Chrome gestures execute only when Chrome is foreground; otherwise
    ignore.
-   Tab mapping customizable; default left = next tab, right = previous
    tab.
-   Use standard Chrome keyboard shortcuts where reliable.
-   System master volume uses Windows native audio endpoint controls.
-   Volume gesture applies one 2-percentage-point adjustment per
    deliberate gesture. Define the percentage as a normalized 0--100
    control step, not a claim of linear perceived loudness.
-   Media controls and general window management are v2.

## 7. Customization

-   Users may independently enable/disable each built-in gesture.
-   Users may reassign existing gestures to built-in actions, custom
    keyboard shortcuts, or launching applications.
-   No user-defined new gesture shapes in v1.
-   Visual settings interface with dropdowns and controls; no JSON
    editor UI.
-   Gesture sensitivity presets Low/Medium/High plus advanced 0--100
    slider.
-   Gesture stability duration adjustable 100--1000 ms.
-   Cooldown fixed at 300 ms.
-   Scroll base speed slider plus movement acceleration.
-   Cursor speed slider.
-   Separate configurable activation and pause hotkeys. No separate
    resume hotkey.
-   Restore Defaults with confirmation.
-   Corrupt settings: preserve damaged file, create defaults, warn user.
-   Keep one previous configuration backup on each save; replace the
    previous backup.
-   No settings import/export in v1.

## 8. Setup, calibration and recovery

-   First-launch sequence is performance-first.
-   Benchmark duration: 30 seconds.
-   Engine selection: best overall balance; accuracy and responsiveness
    are hard gates.
-   If no candidate passes, warn and allow Developer Mode override.
-   Calibration occurs on first launch, can be run manually, and can be
    suggested automatically when tracking quality drops.
-   Do not interrupt an active gesture unexpectedly to calibrate.
-   Setup includes live practice feedback and Test Mode.
-   Test Mode is available in Settings.
-   If recognition repeatedly fails, offer Retry Calibration or
    Continue.
-   Uncertain gestures are ignored.
-   Repeated errors trigger combined recovery: reject uncertain
    gestures, monitor error pattern, offer recalibration or sensitivity
    adjustment.

## 9. Diagnostics, updates and release

-   Detailed Developer Mode toggled in Settings.
-   Developer Mode includes engine selection, camera parameters, debug
    landmarks, benchmark controls, logs and tracking diagnostics.
-   Engine changes require restart.
-   Basic benchmark for users; advanced engine/configuration benchmark
    for developers.
-   Feedback form and detailed bug reporting.
-   Diagnostic export requires user initiation; attach diagnostics to
    bug report only with approval.
-   Manual update check only. Offer download; installation requires
    approval.
-   Development builds unsigned; code signing before public release.
-   Per-user installer; no administrator requirement.
-   Uninstaller asks whether to delete all app data or preserve
    settings/logs/history.
-   Portable build is fully portable.
-   Release path: private alpha → public beta → v1.0.

## 10. Architecture proposal

Use a modular architecture with explicit interfaces so engine
implementations can be swapped without rewriting gesture logic.

``` text
VEYRA Application
├── UI Layer (PySide6)
│   ├── Floating HUD
│   ├── Settings Window
│   ├── Setup Wizard
│   ├── Calibration / Test Mode
│   └── Diagnostics Views
├── Application / State Layer
│   ├── AppStateController
│   ├── CameraLifecycleController
│   ├── GestureLockController
│   ├── HotkeyManager
│   ├── ActionDispatcher
│   └── NotificationManager
├── Capture Layer
│   ├── CameraEnumerator
│   ├── CameraAdapter
│   └── LatestFrameBuffer (capacity 1)
├── Recognition Layer
│   ├── HandLandmarker Interface
│   ├── MediaPipe Adapter
│   ├── ONNX Runtime Adapter
│   ├── Native C++ Adapter (benchmark/prototype)
│   └── PerformanceMonitor
├── Gesture Layer
│   ├── LandmarkGeometry
│   ├── GestureClassifier
│   ├── StabilityFilter
│   ├── NeutralGate
│   └── GestureStateMachine
├── Actions Layer
│   ├── CursorController
│   ├── MouseButtonController
│   ├── ScrollController
│   ├── ChromeTabController
│   ├── WindowsVolumeController
│   └── CustomActionController
├── Data Layer
│   ├── SettingsRepository
│   ├── HistoryRepository
│   ├── DiagnosticLogger
│   └── ExportService
└── Packaging / Platform
    ├── Windows API adapter
    ├── Installer build
    └── Portable build
```

## 11. Concurrency and lifecycle rules

-   UI runs on the Qt main thread only.
-   Camera capture runs in a dedicated worker.
-   Inference/tracking runs in a separate worker or asynchronous engine
    callback.
-   Capture publishes only the newest frame to a capacity-one buffer;
    old frames are overwritten.
-   Do not let the tracking worker build an unbounded queue.
-   Every worker has a cooperative stop signal and bounded shutdown
    timeout.
-   Camera OFF sequence: disable action dispatch → stop inference
    scheduling → signal capture stop → release camera handle → clear
    frame buffer → publish OFF state.
-   On app exit, release any held mouse buttons before stopping input
    services.
-   No worker may update Qt widgets directly; communicate through Qt
    signals/slots.
-   Avoid multiple concurrent camera owners.
-   Engine adapter must expose initialize, process/submit frame,
    retrieve result, metrics, and close semantics.

## 12. Acceptance criteria (initial targets; validate and tune)

  ---------------------------------------------------------------------
  Area                               Acceptance test
  ---------------------------------- ----------------------------------
  Camera privacy                     Camera is not opened at app launch

  Camera ON                          Requires confirmation every time

  Camera OFF                         Device handle released; no new
                                     inference or actions

  Local processing                   Network disconnected; core
                                     features still work

  Frame freshness                    No unbounded frame queue; result
                                     uses current/latest frame

  UI responsiveness                  UI remains interactive during
                                     inference and camera failures

  FPS                                24 FPS target on designated
                                     reference hardware; report actual
                                     result

  Resource use                       CPU/RAM measured over a sustained
                                     run; publish measured baselines

  Gesture safety                     Low-confidence/unstable gestures
                                     never execute

  Repeat protection                  One action per deliberate gesture;
                                     neutral release required

  Chrome                             Tab actions only when Chrome
                                     foreground

  Drag safety                        Interrupted tracking releases held
                                     button after 500 ms and cancels
                                     old drag

  History                            Max 50 entries; no media stored

  Logs                               Auto-expire after 30 days

  Exit                               No camera handle or background
                                     worker remains

  Packaging                          Installed and portable builds both
                                     run on clean Windows test machines
  ---------------------------------------------------------------------

## 13. Open implementation questions (do not ask the user again unless necessary)

-   Exact capture backend and camera enumeration implementation must be
    selected by compatibility testing.
-   Exact model asset and its license must be reviewed before
    distribution.
-   Exact sensitivity thresholds must be tuned using representative
    hands, lighting, skin tones, distances, and webcams.
-   Exact minimum acceptable accuracy and latency thresholds must be
    defined in benchmark protocol before engine selection.
-   Qt/PySide6 licensing obligations must be reviewed for the chosen
    distribution model.
-   Installer technology and code-signing provider are implementation
    choices, not user requirements.
