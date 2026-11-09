# VEYRA --- Technical Research and Architecture Decisions

**Research date:** 5 November 2026\
**Purpose:** Select a practical Windows/Python implementation path
without making unverified performance claims.

## 1. Executive recommendation

Build the first engineering spike around:

-   Python 3.12 or another explicitly tested Python version supported by
    the selected wheels.
-   PySide6 for UI and HUD.
-   OpenCV for initial webcam capture abstraction, with Windows backend
    testing and a clear camera-adapter boundary.
-   MediaPipe Tasks Hand Landmarker as the first recognition candidate.
-   ONNX Runtime CPU with a separately selected, licensed hand-landmark
    model as the second candidate.
-   A native C++ prototype (OpenCV C++ plus ONNX Runtime C++ or
    MediaPipe C++ graph) as a third comparison only if the first two do
    not satisfy measured targets.
-   Windows `SendInput` for mouse/keyboard injection.
-   Windows `RegisterHotKey` for system-wide shortcuts.
-   Windows Core Audio `IAudioEndpointVolume` for master volume.
-   PyInstaller onedir as the initial packaging baseline; installer and
    portable packaging built from the same onedir application payload.

This is a research recommendation, not a final engine selection. The
user's confirmed choice is to benchmark and automatically select the
best overall engine subject to minimum accuracy and responsiveness
gates.

## 2. Recognition engine candidates

### 2.1 Candidate A --- MediaPipe Tasks Hand Landmarker (Python)

Official documentation: - Python guide:
https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python -
Overview:
https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker -
Python setup:
https://developers.google.com/edge/mediapipe/solutions/setup_python -
PyPI: https://pypi.org/project/mediapipe/

Why it is the first candidate: - Designed specifically for hand landmark
detection. - Produces hand landmarks in image and world coordinates and
handedness. - Configurable maximum hand count; v1 should set one hand. -
Supports IMAGE, VIDEO and LIVE_STREAM modes. - In video/live-stream
modes it uses tracking to avoid invoking palm detection on every
frame. - LIVE_STREAM is asynchronous. If the task is busy, an incoming
frame may be ignored rather than creating an unbounded backlog; this
aligns with VEYRA's latest-frame-only requirement. - Official Python
setup documentation lists Windows x86_64 and arm64 and Python 3.9+
(current setup page lists 3.9--3.14).

Cautions: - The current PyPI metadata at research time labels the
package Alpha. Pin and test an exact release; do not blindly float to
latest in a production build. - The wheel is a meaningful
distribution-size dependency; measure final installed size and startup
cost. - Model assets are distributed separately in many workflows.
Verify the exact `.task` model asset's license and redistribution rights
independently from the Python package license. - The official demo
benchmark shown for Pixel 6 is not evidence of performance on a Windows
i3/Ryzen 3 laptop. - Do not run inference in the UI thread.

Implementation notes: - Use LIVE_STREAM where its asynchronous callback
semantics fit the adapter. - Keep `num_hands=1`. - Set detection,
presence and tracking confidence thresholds from a tested config. - Use
monotonic timestamps in milliseconds. - Convert/prepare camera frames
once; avoid repeated color conversion and image copies. - Do not render
landmarks during normal operation. Landmark overlay is Developer
Mode/Test Mode only.

### 2.2 Candidate B --- ONNX Runtime CPU with a hand-landmark model

Official documentation: - Windows overview:
https://onnxruntime.ai/docs/get-started/with-windows.html - Install
matrix: https://onnxruntime.ai/docs/install/ - Execution providers:
https://onnxruntime.ai/docs/execution-providers/

Why test it: - CPU execution provider can provide a consistent CPU
baseline. - Runtime is model-agnostic and allows comparison of different
compatible ONNX hand detection/landmark models. - C/C++ APIs are
available if Python overhead becomes a bottleneck. - Execution provider
selection can be kept behind the engine adapter.

Cautions: - ONNX Runtime is an inference engine, not a hand detector by
itself. VEYRA must select and validate an actual model pipeline
(palm/hand detector plus landmark model, or an equivalent single
model). - Model input/output preprocessing, tensor layouts,
normalization and coordinate conversion must be implemented correctly. -
Verify model license, training-data terms, model card and redistribution
permission before bundling. - Do not compare an incomplete single-stage
model with a complete MediaPipe pipeline and call the result
equivalent. - ONNX Runtime CPU may use multiple threads; tune thread
count and CPU affinity only after measurement.

Windows acceleration notes: - Microsoft currently recommends WinML for
new Windows deployments. - WinML offers dynamic execution-provider
selection and is available in Windows 11 24H2+ with the newer
integration; older supported Windows 10/11 releases require more manual
selection/management. - DirectML remains supported but is in sustained
engineering; Microsoft says new feature development has moved to
WinML. - Because VEYRA targets Windows 10 and Windows 11 broadly and the
application UI/runtime is Python, do not make WinML/DirectML a mandatory
v1 dependency. Treat them as optional experiments after CPU baseline. -
Keep ONNX Runtime CPU as the portable benchmark baseline.

### 2.3 Candidate C --- Native C++ prototype

Possible prototypes: - OpenCV C++ capture + ONNX Runtime C++
inference. - MediaPipe C++ graph if the build and dependency burden is
justified. - Native C++ gesture geometry and action pipeline with
Python/PySide6 UI only if profiling proves Python overhead is material.

Why test it: - Can reduce interpreter and object-allocation overhead in
hot paths. - Can integrate native camera and input APIs more directly. -
Provides a route if Python capture/inference scheduling cannot meet
target latency.

Cautions: - C++ does not automatically make inference faster; the model
and backend often dominate. - Build, packaging, debugging and
cross-version maintenance become more complex. - A mixed Python/C++
boundary can introduce copying and synchronization overhead. - Do not
rewrite the application in C++ before profiling identifies a real
bottleneck.

Recommendation: build a narrow benchmark executable, not a full second
product implementation.

## 3. Benchmark protocol

### 3.1 Benchmark duration and conditions

-   Initial setup benchmark: 30 seconds (user-confirmed).
-   Development comparison: repeat multiple runs after warm-up; record
    median and tail values.
-   Test on physical reference devices spanning low-end target hardware,
    not only the developer's laptop.
-   Keep camera, lighting, distance, hand, resolution and test clip/live
    input conditions identical across candidates.
-   Record exact CPU model, RAM, Windows build, camera model/driver,
    Python/runtime/model versions, power mode and thermal conditions.
-   Run both recorded test clips and live webcam trials. Clips provide
    repeatability; live trials expose camera and scheduling issues.

### 3.2 Required metrics

-   Mean and percentile FPS (especially 1% low / lower percentile).
-   Capture-to-result latency and result age at dispatch.
-   CPU utilization over time.
-   VEYRA process working set/private bytes.
-   Startup and model warm-up time.
-   Dropped/skipped frames and stale-frame count.
-   Hand detection rate and landmark stability.
-   Gesture-level precision/recall and false action rate.
-   Long-run stability and thermal throttling.
-   Distribution size and cold start time.

### 3.3 Accuracy dataset

Create a local, consent-based test set with: - left/right hands; -
different skin tones and hand sizes; - different camera distances and
angles; - bright, dim and backlit environments; - backgrounds with
clutter and motion; - all supported gestures plus ordinary non-gesture
hand movement; - transitions between gestures and neutral pose; - hand
entering/leaving the frame.

Do not store webcam data in normal product operation. Test clips used
for development must be explicitly collected, locally stored,
access-controlled, and excluded from user diagnostic exports.

### 3.4 Selection logic

-   Establish hard minimums for gesture precision, false-positive rate,
    latency and stable FPS before scoring.
-   Reject candidates that fail any hard minimum.
-   Score passing candidates across accuracy, FPS, CPU, RAM, startup
    time, latency and stability.
-   The user selected best overall balance, not lowest CPU at any cost.
-   Save benchmark result metadata and selected engine version locally.
-   Allow manual engine override in Advanced Settings; changing engine
    requires restart.
-   If no engine passes, recommend against normal use but permit
    Developer Mode override with warning.

## 4. Camera capture on Windows

References: - OpenCV video I/O backend flags:
https://docs.opencv.org/4.x/d4/d15/group\_\_videoio\_\_flags\_\_base.html
(older version result also documents backend identifiers) - Microsoft
DirectShow capture overview:
https://learn.microsoft.com/en-us/windows/win32/directshow/about-video-capture-devices -
Windows camera privacy:
https://learn.microsoft.com/en-us/windows/apps/develop/camera/camera-privacy-setting

Important findings: - OpenCV exposes Windows capture backends including
DirectShow (`CAP_DSHOW`) and Media Foundation (`CAP_MSMF`) depending on
build. - Microsoft describes DirectShow capture as legacy and recommends
Media Foundation capture APIs for new Windows code where possible. -
Windows camera access may be denied at device, desktop-app, or
packaged-app level. VEYRA must handle denied access and provide a path
to Windows Camera privacy settings. - A camera index alone is not a
durable identity. Enumerate devices by a stable device identifier/name
where possible; store preferred identifier, then gracefully fall back if
it disappears. - Camera enumeration in OpenCV Python is limited and
backend-dependent. Prototype the actual enumeration method; if reliable
named enumeration is required, consider a small native Media
Foundation/Windows Runtime helper. - Test MSMF and DSHOW per device. Do
not assume one backend is universally best. Prefer the tested backend
for that camera, with fallback. - Camera release must be explicit and
verified. Test whether the webcam indicator/lock is released after
Camera OFF and after application exit. - Do not open a second camera
handle during settings preview or diagnostics.

Proposed camera adapter: - `enumerate_devices()` -
`open(device_id, width, height, fps, backend)` - `read_latest()` -
`get_actual_format()` - `close()` - `health_snapshot()`

## 5. Frame pipeline and performance architecture

-   Capture worker continuously reads frames only while camera ON.
-   Publish into a capacity-one latest-frame buffer.
-   Inference worker consumes the newest available frame; stale frames
    are overwritten.
-   Do not use an unbounded `queue.Queue`.
-   Track timestamps: capture timestamp, inference start/end, result
    timestamp, dispatch timestamp.
-   Reject callbacks from stale camera-session generations.
-   Start with 320×240 as an experiment; compare 320×240, 640×360 and
    640×480. Choose the lowest resolution that passes gesture accuracy.
-   Increase frame skipping before dropping below acceptable
    responsiveness; if FPS falls, reduce resolution and increase skip.
    Restore gradually after stable intervals.
-   Avoid full camera preview in normal use.
-   Convert BGR/RGB once per frame as needed.
-   Keep gesture geometry lightweight and separate from neural
    inference.
-   Avoid per-frame logging and UI repaint storms.

## 6. UI and HUD --- PySide6

References: - QWidget / translucency:
https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html - Qt
licensing: https://doc.qt.io/qt-6/licensing.html

Fit: - PySide6 supports translucent top-level widgets on Windows when
using a frameless window and translucent background attribute. - Use
Qt's always-on-top window flag and test focus behaviour carefully. - UI
thread owns all widgets. Workers communicate via signals/slots. - Use a
custom-painted orbital icon and restrained cyan/graphite palette. - The
user's Q183 choice is no recognition animation: only update
gesture/action text. Do not add orbital animation on every gesture. -
Use a small number of controlled repaints; do not animate constantly
when idle.

Licensing: - Qt licensing options include LGPLv3/GPLv3 and commercial.
Some modules are GPL-only. - Review PySide6/Qt and bundled dependency
licenses before public distribution. If the project is proprietary,
obtain legal review of LGPL compliance or evaluate a commercial
license. - Keep an attribution/license inventory for every bundled
dependency and model.

## 7. Windows input, hotkeys and system volume

### 7.1 Mouse and keyboard

Reference:
https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput

Use `SendInput` for: - relative/absolute cursor input; - left mouse
down/up; - wheel events; - Chrome shortcut keystrokes; - user-mapped
keyboard shortcuts.

Important: - Check returned event count; do not assume success. - Always
pair mouse-down with mouse-up and use a cleanup guard. - Windows UIPI
can block input injection into higher-integrity applications. The API
does not reliably identify UIPI as the cause from return values. Do not
elevate VEYRA by default; document that elevated targets may not be
controllable. - Do not hold keys/buttons across state transitions or
exit.

### 7.2 Global hotkeys

Reference:
https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey

Use `RegisterHotKey` for system-wide activation and pause shortcuts. -
Registration can fail if a combination is already registered or
reserved. - Handle registration failure and offer alternatives. - Do not
claim that VEYRA can detect every app-level shortcut conflict; Windows
registration detects conflicts at the OS registration layer, not all
semantic shortcut uses inside every app. - Unregister on shutdown and
when changing shortcut settings.

### 7.3 Chrome tabs

Reference: https://www.chromium.org/user-experience/tabs/

Use: - Ctrl+Tab = next tab. - Ctrl+Shift+Tab = previous tab. - Check
foreground window before dispatch. - Do not queue tab actions while
Chrome is inactive. - Keep mappings customizable.

### 7.4 Windows master volume

References: -
https://learn.microsoft.com/en-us/windows/win32/api/endpointvolume/nf-endpointvolume-iaudioendpointvolume-setmastervolumelevelscalar -
https://learn.microsoft.com/en-us/windows/win32/api/endpointvolume/nn-endpointvolume-iaudioendpointvolume

Use Windows Core Audio `IAudioEndpointVolume` for master endpoint
volume. `SetMasterVolumeLevelScalar` accepts normalized values 0.0--1.0
and uses an audio-tapered scale. The requested gesture increment is 2
points on that normalized control range; it is not necessarily a 2%
change in perceived loudness.

## 8. Packaging strategy

Reference: https://pyinstaller.org/en/stable/operating-mode.html

Recommended baseline: - Use PyInstaller onedir for development and first
release candidate. - Build installer EXE around the onedir application
payload. - Build portable ZIP/folder from the same onedir payload. -
Installed version stores data in AppData. - Portable version stores data
beside the executable. - Keep runtime/model assets external to the
executable where that simplifies updates and licensing, but include them
in the distribution folder. - Validate that the webcam native
dependencies, Qt plugins, model assets and runtime DLLs are collected. -
Onefile may be explored later, but it extracts to a temporary directory
and starts more slowly; it is not the preferred first packaging
target. - Test on clean Windows machines without Python installed. -
Per-user installer must not require admin elevation. - Code sign before
public release.

## 9. Dependency and license review

Before release, maintain `THIRD_PARTY_NOTICES.md` with: - package name
and pinned version; - license identifier and license text; - source
URL; - model asset name/version/hash; - model license and redistribution
terms; - any notices/attribution required; - bundled native DLLs and
their licenses.

At research time, PyPI lists MediaPipe as Apache 2.0, but the exact
model asset must be checked independently. PySide6/Qt licensing needs
separate review. Do not assume package license covers all assets.

## 10. Open-source references

-   MediaPipe Hand Landmarker Python guide:
    https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python
-   MediaPipe Hand Landmarker overview:
    https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker
-   MediaPipe Python setup:
    https://developers.google.com/edge/mediapipe/solutions/setup_python
-   MediaPipe PyPI package: https://pypi.org/project/mediapipe/
-   ONNX Runtime Windows:
    https://onnxruntime.ai/docs/get-started/with-windows.html
-   ONNX Runtime install: https://onnxruntime.ai/docs/install/
-   ONNX Runtime DirectML:
    https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html
-   OpenCV video I/O flags:
    https://docs.opencv.org/4.x/d4/d15/group\_\_videoio\_\_flags\_\_base.html
-   Windows camera privacy:
    https://learn.microsoft.com/en-us/windows/apps/develop/camera/camera-privacy-setting
-   Windows DirectShow capture overview:
    https://learn.microsoft.com/en-us/windows/win32/directshow/about-video-capture-devices
-   Qt for Python QWidget:
    https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html
-   Qt licensing: https://doc.qt.io/qt-6/licensing.html
-   Windows SendInput:
    https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
-   Windows RegisterHotKey:
    https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey
-   Windows Core Audio endpoint volume:
    https://learn.microsoft.com/en-us/windows/win32/api/endpointvolume/nn-endpointvolume-iaudioendpointvolume
-   Chrome/Chromium tab switching:
    https://www.chromium.org/user-experience/tabs/
-   PyInstaller operating modes:
    https://pyinstaller.org/en/stable/operating-mode.html

## 11. Research caveats

-   Documentation confirms APIs and features, not VEYRA's measured
    performance.
-   A MediaPipe demo benchmark on a mobile device is not comparable to
    an entry-level Windows laptop.
-   OpenCV backend availability depends on the installed build and
    camera driver.
-   WinML is attractive on newer Windows 11, but broad Windows 10
    compatibility and Python integration require separate validation.
-   C++ should be introduced only if profiling proves a bottleneck.
-   The engine benchmark must be repeated after dependency/model
    updates.
