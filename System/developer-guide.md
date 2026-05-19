# Developer Guide

This is the short contributor note for Obsidian Fitness. The public vault should feel simple; this file exists only for people changing the system.

## Product Shape

- `Home.md` is the front door.
- `Progress/` contains load, running, strength, calisthenics, swimming, and history.
- `Reference/` contains short human-facing training references.
- `System/` contains settings, importers, the workout template, the Templater setup script, and per-workout UI modules.
- `Workouts/` contains personal logs and is ignored by git by default.

## Required Plugins

- Templater creates workout notes.
- Dataview renders app and progress pages.
- Meta Bind provides editable workout inputs.
- Homepage opens `Home.md` on startup.

## Data Contract

Workout notes store analytics data in YAML frontmatter. The core fields are:

- `schema_version`
- `date`
- `day`
- `block`
- `block_name`
- `week`
- `workout_type`
- type-specific metrics
- `notes`

The `date` field is the source of truth for progress pages. File names can differ from workout dates when logging retroactively.

## Core Files

| File | Purpose |
|---|---|
| `Home.md` | Daily surface, weekly snapshot, recommendation, recent workouts |
| `Progress/history.md` | Chronological workout list |
| `Progress/load.md` | Weekly volume, load, recovery pressure |
| `Progress/running.md` | Running distance, 5K, heart rate trends |
| `Progress/strength.md` | Top sets, estimated maxes, training maxes |
| `Progress/calisthenics.md` | Rep volume, records, progressions |
| `Progress/swimming.md` | Swim volume, time, 1km benchmarks |
| `System/settings.md` | Program start, block, training maxes, progressions |
| `System/importers/import_workouts.py` | Apple Health and Garmin import script |
| `System/workout-template.md` | Workout note template |
| `System/workoutEngine.js` | Templater setup and derived values |

## Extending Workout Types

To add or change a workout type:

1. Update `System/workoutEngine.js` if derived frontmatter or defaults change.
2. Update `System/workout-template.md` if the generated note needs new fields.
3. Update the matching `System/ui-modules/ui-*.md` form.
4. Update progress pages only when the new field should be analysed.

## Importing External Data

- Put private Apple Health and Garmin files in `Imports/`.
- Use `System/importers/import_workouts.py` to write normal workout notes.
- Imported notes must include `import_source`, `import_external_id`, `imported_at`, and `source_activity_type`.
- Never overwrite hand-written workout notes during import.

## UI Rules

- Use DataviewJS `createEl` and event listeners. Avoid inline `onclick`.
- Keep mobile cards narrow, skimmable, and touch-friendly.
- Do not expose long explanatory text on app pages.
- Keep `Reference/` short. Put implementation notes here instead.

## Publishing Rules

- Do not commit real workout notes.
- Keep `Workouts/*.md` ignored.
- Keep `Imports/*` ignored.
- Use `Examples/demo-workouts/` for public screenshots.
- Keep personal metrics out of the public-facing guide unless they are anonymized examples.
- The project is licensed under the MIT License.
