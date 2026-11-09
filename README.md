# VEYRA

The Future Is in Your Hands.

VEYRA is a local-first Windows hand-gesture controller. This repository is
currently at **Phase 2 — Camera Lifecycle**. The application provides a
local-only floating HUD, appearance settings, a skippable first-launch setup
wizard, and explicit OpenCV camera start/stop lifecycle management. It does
not recognize gestures, inject mouse/keyboard input, or make network requests.

## Requirements

- Windows 10 or Windows 11
- Python 3.12 or 3.13
- PowerShell

## Windows setup

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements\dev.txt
```

If PowerShell blocks activation for the current user, use the documented
Python executable directly instead, or ask an administrator to review the
execution policy. Do not commit `.venv`.

## Run the Phase 2 app

```powershell
.\.venv\Scripts\Activate.ps1
python -m veyra.main
```

The first launch opens the skippable setup wizard. Later launches open the
floating HUD directly. The camera remains OFF until the user clicks Camera ON
and confirms the prompt.

## Manual camera test

From Command Prompt, with the virtual environment activated:

```cmd
python -m veyra.main
```

1. Confirm that the HUD starts with `CAMERA OFF` and no camera indicator.
2. Open Settings → Camera and click `Refresh available cameras`.
3. Select a listed camera, close Settings, click `Camera ON`, and confirm.
4. Verify the HUD reports `CAMERA ON • CAPTURING LOCALLY`.
5. Click `Emergency Stop` and verify the status returns to `CAMERA OFF`.
6. Repeat with the camera unavailable or occupied and verify a recovery warning.
7. Close VEYRA and verify the camera indicator turns off and the device is released.

No frame preview or image/video file is created by Phase 2.

## Test and lint

```powershell
python -m pytest
ruff check .
```

## Project layout

- `src\veyra\` — installable application package.
- `requirements\` — separate pinned runtime, development, and future benchmark definitions.
- `tests\unit`, `tests\integration` — unit, UI, and mocked camera lifecycle tests.
- `assets\branding` — Phase 1 SVG identity assets.
- `assets\models` — future model documentation only; no model is included.
- `THIRD_PARTY_NOTICES.md` — dependency and licensing inventory template.
- `docs\` — planning and technical documentation.

## Development boundaries

Phase 2 intentionally excludes hand recognition, mouse/keyboard injection,
model assets, and network activity. Do not add those until the corresponding
phase is approved.

