# VEYRA --- Gesture, Safety and State Specification

This document is the behavioural contract for the gesture engine and
action dispatcher. Codex must implement these rules as explicit state
machines, not scattered boolean checks.

## 1. Core principles

1.  A gesture is an input proposal, not an action. It must pass tracking
    quality, confidence, stability, state, neutral-gate, and cooldown
    checks.
2.  At most one action is emitted for one deliberate gesture, except
    continuous cursor movement and continuous scroll while their
    corresponding gesture remains active.
3.  Every discrete action requires a return to neutral before it can
    fire again.
4.  If the classifier is uncertain or two gestures conflict, execute
    nothing.
5.  Camera OFF is a hard boundary: no capture, inference, or gesture
    action.
6.  Gesture Pause, Gesture Lock, Camera OFF, and application exit are
    distinct states.

## 2. State model

Model application lifecycle and gesture mode separately.

### 2.1 Application/camera states

-   `APP_STARTING`
-   `CAMERA_OFF`
-   `CAMERA_START_CONFIRMATION`
-   `CAMERA_STARTING`
-   `CAMERA_ON`
-   `CAMERA_STOPPING`
-   `APP_EXITING`
-   `APP_ERROR_RECOVERY`

### 2.2 Gesture controller states (valid only while camera is ON)

-   `CONTROLLER_ACTIVE`
-   `GESTURE_PAUSED` --- entered by fist; camera remains ON; open palm
    resumes.
-   `GESTURE_LOCKED` --- HUD-only lock; blocks all action dispatch.
    Tracking may continue for status.
-   `HAND_LOST` --- no usable hand; actions suspended; cursor freezes.
-   `CALIBRATION_REQUIRED`
-   `CALIBRATION_RUNNING`
-   `TEST_MODE`

### 2.3 State precedence

Safety precedence from strongest to weakest:

1.  `APP_EXITING`
2.  `CAMERA_OFF` / `CAMERA_STOPPING`
3.  `APP_ERROR_RECOVERY`
4.  `CAMERA_START_CONFIRMATION` / `CAMERA_STARTING`
5.  `GESTURE_LOCKED`
6.  `GESTURE_PAUSED`
7.  `HAND_LOST`
8.  `CALIBRATION_REQUIRED` / `CALIBRATION_RUNNING`
9.  `CONTROLLER_ACTIVE`

A higher-precedence state blocks lower-precedence behaviour. Do not let
a stale recognition callback dispatch an action after the camera has
been turned OFF or the app has begun exiting. Every recognition result
should carry a camera-session generation/token; discard results from
older sessions.

## 3. State transitions

  --------------------------------------------------------------------------------------
  Current state               Event         Next state                  Required
                                                                        behaviour
  --------------------------- ------------- --------------------------- ----------------
  App launch                  UI            CAMERA_OFF                  Show HUD; do not
                              initialized                               open webcam

  CAMERA_OFF                  HUD Camera ON CAMERA_START_CONFIRMATION   Show
                              / activation                              Confirm/Cancel
                              hotkey                                    popup

  CAMERA_START_CONFIRMATION   Cancel        CAMERA_OFF                  Do not open
                                                                        camera

  CAMERA_START_CONFIRMATION   Confirm       CAMERA_STARTING             Initialize
                                                                        selected camera

  CAMERA_STARTING             Success       CAMERA_ON +                 Start capture
                                            CONTROLLER_ACTIVE           and recognition

  CAMERA_STARTING             Failure       APP_ERROR_RECOVERY then     Show guided
                                            CAMERA_OFF                  recovery;
                                                                        release partial
                                                                        resources

  CAMERA_ON                   Fist stable   GESTURE_PAUSED              Camera stays ON;
                                                                        block actions

  GESTURE_PAUSED              Open palm     CONTROLLER_ACTIVE           Require
                              stable                                    neutral/new
                                                                        deliberate
                                                                        gesture after
                                                                        resume

  CAMERA_ON                   HUD Gesture   GESTURE_LOCKED              Block all action
                              Lock                                      dispatch

  GESTURE_LOCKED              HUD Unlock    CONTROLLER_ACTIVE or        Restore previous
                                            GESTURE_PAUSED              non-locked
                                                                        gesture state
                                                                        safely

  CAMERA_ON                   Hand lost     HAND_LOST                   Freeze cursor;
                                                                        suspend actions

  HAND_LOST                   Hand returns  CONTROLLER_ACTIVE           Reacquire;
                                                                        neutral gate
                                                                        before any
                                                                        action

  Any camera-on state         Pause hotkey  CAMERA_STOPPING             Block actions
                              / HUD Stop                                immediately;
                                                                        stop workers;
                                                                        release webcam

  CAMERA_STOPPING             Release       CAMERA_OFF                  Show camera OFF
                              complete                                  

  Any state                   App close     APP_EXITING                 Release mouse
                                                                        buttons; stop
                                                                        workers; release
                                                                        webcam; exit
  --------------------------------------------------------------------------------------

If Gesture Lock is activated while gesture-paused, remember the prior
gesture mode and restore it on unlock. Never let unlock unexpectedly
resume a paused controller.

## 4. Recognition pipeline

1.  Capture newest frame.
2.  Validate frame timestamp and camera-session token.
3.  Run hand landmark inference (one hand).
4.  Select hand according to Auto / Left / Right setting.
5.  Validate landmark confidence and tracking continuity.
6.  Normalize landmark coordinates for image dimensions and mirroring.
7.  Derive geometric features.
8.  Classify candidate gesture(s).
9.  Resolve conflicts: highest-confidence candidate only, and only if it
    passes all gates; otherwise no gesture.
10. Apply stability duration (user-adjustable 100--1000 ms).
11. Apply neutral/release gate.
12. Apply fixed 300 ms cooldown for discrete actions.
13. Check controller state and foreground-app conditions.
14. Dispatch action.
15. Record local history entry and update HUD text.

Use a monotonic clock for durations/cooldowns. Do not use wall-clock
time for gesture timing.

## 5. Gesture definitions and mappings

Gesture classification should be based on landmark geometry and temporal
features, not brittle raw pixel coordinates. Exact thresholds must be
calibrated and tested.

### 5.1 Pointing --- cursor movement

-   Index finger extended; other fingers folded.
-   Cursor movement only while pointing is stable.
-   Relative mapping: hand moves right → cursor moves right.
-   Use cursor speed slider, balanced smoothing, low latency, and small
    dead zone.
-   Support all connected monitors.
-   When pointing ends or hand is lost, stop moving cursor.
-   Cursor position freezes at last valid point when hand leaves frame.
-   Cursor movement is continuous; it does not require a discrete
    click-style cooldown.

### 5.2 Pinch --- click and drag

-   Pinch location synchronizes cursor to the pinch location, then click
    is emitted on release if the pinch did not enter drag mode.
-   Single left-click only. No double-click and no right-click.
-   A quick deliberate pinch/release produces exactly one left-click.
-   Pinch held for 400 ms enters dedicated drag mode.
-   During drag, hand movement controls cursor while left mouse button
    remains held.
-   Releasing pinch ends drag and releases left mouse button.
-   If hand disappears during drag: freeze cursor temporarily; after 500
    ms release the held button.
-   If tracking is interrupted, cancel drag permanently. Even if hand
    returns before 500 ms, do not resume the old drag; require a new
    pinch.
-   On camera OFF, app exit, or fatal input error, release any held
    mouse button immediately.
-   Use an explicit `mouse_button_held` safety guard and idempotent
    release operation.

### 5.3 Two-finger scroll

-   Two fingers raised.
-   Hold the gesture and move hand vertically for continuous scroll.
-   Up/down mapping must be consistent and documented in settings.
-   Base scroll speed is adjustable.
-   Hand movement controls acceleration.
-   Stop scroll immediately when gesture is lost, controller pauses,
    lock activates, hand disappears, or camera turns OFF.
-   Do not also classify this as cursor pointing or three-finger volume.

### 5.4 Horizontal swipe --- Chrome tabs

-   Horizontal swipe left = next tab.
-   Horizontal swipe right = previous tab.
-   Must pass both minimum horizontal displacement and minimum speed.
-   One tab action per swipe; neutral state required before another.
-   Execute only if Chrome is the foreground application.
-   Default shortcut mapping should use the Chrome-compatible tab-switch
    shortcuts (Ctrl+Tab / Ctrl+Shift+Tab), configurable by user.
-   If Chrome is not foreground, ignore action and do not queue it for
    later.
-   Do not trigger tab switching from ordinary slow hand movement.

### 5.5 Three-finger volume

-   Three fingers raised.
-   Move up = master volume +2 percentage points.
-   Move down = master volume −2 percentage points.
-   Exactly one adjustment per deliberate gesture.
-   Return to neutral before another adjustment.
-   Clamp volume to supported 0--100 range.
-   Interpret "2%" as a two-point increment in the normalized Windows
    volume control, not a promise of linear perceived loudness.

### 5.6 Open palm and fist

-   Fist: pause gesture actions temporarily; camera remains ON.
-   Open palm: resume from fist pause.
-   These are state-control gestures and take precedence over action
    gestures.
-   After resume, require neutral/new deliberate gesture before any
    other action.
-   In Gesture Lock, gestures cannot unlock the controller; unlock is
    HUD-only.

## 6. Conflict resolution and neutral gate

-   Fist/open-palm state controls take precedence over action gestures.
-   Three-finger volume must not be confused with two-finger scroll or
    pointing.
-   Pinch and pointing may share index landmarks; use explicit pinch
    detection and state gating to prevent cursor movement from
    triggering a click.
-   Swipe detection must not also emit continuous cursor or scroll
    actions during the swipe.
-   If two candidates are within an unresolved confidence margin, emit
    no action.
-   A discrete gesture remains latched until a neutral pose is detected.
-   Neutral pose thresholds must be validated empirically; do not
    hard-code untested values as final.
-   A gesture that begins while the hand is already partially formed
    should not fire immediately; require a neutral baseline first after
    camera start, hand return, controller resume, or calibration.

## 7. Stability, sensitivity and cooldown

-   Gesture stability duration: adjustable 100--1000 ms.
-   Sensitivity: Low / Medium / High presets plus advanced 0--100
    slider.
-   Cooldown: fixed 300 ms.
-   The 300 ms cooldown is an additional guard, not a replacement for
    neutral release.
-   Stability timer resets when classification changes, confidence drops
    below threshold, hand identity changes, or hand is lost.
-   Sensitivity changes must not bypass the minimum confidence floor.
-   Persist settings locally.

## 8. Hand tracking loss

-   On hand loss, suspend all gesture actions immediately.
-   Freeze cursor at last known location.
-   If dragging, freeze cursor and start 500 ms release timer; then
    release held button and permanently cancel the drag.
-   When hand returns, reacquire and require neutral pose followed by a
    fresh deliberate gesture.
-   Do not replay missed gestures or queued actions.

## 9. Hotkeys and emergency controls

-   Default activation: `Ctrl+Shift+Space`.
-   Activation when camera OFF requests camera-on confirmation; after
    confirmation, camera starts and controller becomes active.
-   Activation while already active shows brief "already active".
-   Configurable pause hotkey turns camera OFF and releases device.
-   Pause hotkey while camera OFF shows "camera already OFF".
-   No separate resume hotkey. After keyboard pause, use HUD Camera ON
    button.
-   Gesture Lock only through HUD.
-   Emergency Stop button on HUD immediately turns camera OFF and
    releases webcam.
-   Detect hotkey registration failure. Explain that Windows or another
    application may own the combination; suggest alternatives. Do not
    claim perfect detection of all app-level shortcut conflicts.

## 10. Action dispatch safety

Before dispatching any action, verify: - camera session token is
current; - app is not exiting; - camera is ON; - controller is active
and not locked/paused/hand-lost; - candidate confidence is above
threshold; - stability duration has passed; - neutral gate permits the
action; - cooldown permits the action; - required foreground application
is active; - action mapping is enabled.

If any check fails, do nothing.

## 11. Logging and user history

Record only: - timestamp; - gesture label; - action label; -
success/ignored/failure status; - optional compact reason code.

Never record image frames, video, or raw webcam data. Keep last 50
activity entries. Logs expire after 30 days.
