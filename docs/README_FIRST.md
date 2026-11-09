# VEYRA --- Codex Planning Pack

**Tagline:** The Future Is in Your Hands.\
**Product:** Windows hand-gesture laptop controller\
**Status:** Requirements complete; technical design and implementation
planning\
**Release path:** Private alpha → public beta → v1.0

## Read these files in order

1.  `PROJECT_PLAN.md` --- product scope, confirmed requirements,
    architecture, milestones and acceptance criteria.
2.  `GESTURE_AND_STATE_SPEC.md` --- exact gesture definitions, mappings,
    safety rules and state transitions.
3.  `TECHNICAL_RESEARCH.md` --- technology candidates, evidence,
    trade-offs, licensing and recommended decisions.
4.  `CODEX_BUILD_GUIDE.md` --- repository layout, staged Codex prompts,
    development rules and test gates.

## Non-negotiable project principles

-   Windows 10 and Windows 11 support.
-   Local processing; no cloud inference, telemetry, webcam upload, or
    image/video recording.
-   Camera is OFF at launch and only starts after an explicit user
    action and confirmation.
-   Camera OFF means capture is stopped, the device is released, and
    tracking work stops.
-   Target hardware: 8 GB RAM, Intel Core i3 / AMD Ryzen 3 class or
    better. This is a target, not a performance guarantee.
-   Target tracking rate: 24 FPS, validated on physical target machines.
-   One hand in v1; second-hand support is deferred.
-   Prefer the lowest practical CPU and RAM use while meeting minimum
    recognition reliability.
-   Do not choose a recognition engine based on reputation or synthetic
    benchmark claims. Run the same benchmark protocol on target
    hardware.
-   A failed or uncertain gesture must not trigger an action.
-   Do not begin full implementation until the engine benchmark and
    architecture spikes have been completed.

## Important scope interpretation

Version 1 includes mouse control, Chrome tab switching, system
master-volume gestures, and the approved custom-action capability
(existing gesture mappings, keyboard shortcuts, and launching
applications). General Windows desktop/window-management controls and
media playback controls are deferred to v2. Treat application launching
as a narrowly scoped custom action, not as permission to add broad
desktop/window management.

## Current planning status

The questionnaire has been completed through Q199. This pack translates
the decisions into an implementation-ready specification. It does not
claim that the application has already been built, benchmarked, or
validated.
