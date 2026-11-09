# VEYRA Agent Instructions

Read the relevant documents in `docs/` before changing the project:

1. `README_FIRST.md`
2. `PROJECT_PLAN.md`
3. `GESTURE_AND_STATE_SPEC.md`
4. `TECHNICAL_RESEARCH.md`
5. `CODEX_BUILD_GUIDE.md`

Implement only the phase explicitly requested. Preserve confirmed product
requirements and existing user changes.

## Safety boundaries

- Keep processing local; do not add telemetry or background network activity.
- Camera access requires an explicit user confirmation and must remain OFF at startup.
- Do not implement hand recognition, OS mouse/keyboard injection, or Windows
  control integrations before their assigned phases.
- Do not claim that placeholder UI controls perform future functionality.
- Keep the UI responsive and testable without hardware.

## Validation

Run from the repository root:

```powershell
python -m pytest --basetemp .pytest-tmp
ruff check .
```

Report files changed, tests and exact results, known limitations, and whether
camera, network, or OS input functionality was introduced.
