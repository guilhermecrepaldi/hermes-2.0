# UI Re-Direction Pattern

## Context
When a new feature shares the same rendering pipeline as an existing feature, **redirect instead of reimplement**.

## The Pattern

```
Feature Tab → Generate data → Create session → Redirect to Main Tab
```

Instead of trying to render the same ExerciseField/FolhaScreen/ZoomableCanvas inside the new tab (which requires duplicating all the ViewModel wiring, callbacks, gesture configs, and lifecycle management), just:

1. **Generate the data** in the feature tab
2. **Inject it into the shared ViewModel** (session state, folha, config)
3. **Redirect** to the main tab

## Concrete Example: Simulado Tab

**Bad approach (original):** SimuladoTab tried to render ExerciseField directly inside its own composable. Required duplicating:
- `ZoomableCanvas` wrapping
- `doAdvance` / `submitFolha` logic
- `onSyncScratch` / `onSyncAnswer` callbacks
- Pen event handling
- Gesture config
- Session lifecycle
→ 4 bugs in one session: Enter didn't advance, recognition failed, fields didn't appear, infinite loop

**Good approach (fixed):**
1. SimuladoTab generates N exercises via `ProceduralEngine`
2. Calls `_setSimuladoState(folha, simConfig)` — injects folha + config into sessionViewModel
3. Calls `onGoToSprint()` — switches tab
4. SprintTab renders everything using its EXISTING, WORKING FolhaScreen/ZoomableCanvas pipeline
→ Zero rendering bugs. SprintTab already handles Enter, recognition, navigation, timer, submit.

## Rules

- **If a feature is "like X but with tweaks"** → verify it can reuse X's rendering pipeline
- **NUNCA duplicate a rendering pipeline** (FolhaScreen, ZoomableCanvas, InkCanvas) just to add a different config
- **The shared ViewModel is the bridge**: inject data + config, let the existing UI do its job
- **Pre-generated data** (exercises, folhas) works fine — the UI doesn't care where the data came from

## When NOT to use this pattern

- The feature has a fundamentally different rendering requirement (3D, video, audio)
- The data transformation is too different from the shared pipeline's expectations
- The main tab's lifecycle conflicts with the feature's requirements
