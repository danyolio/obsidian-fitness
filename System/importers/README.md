# Apple Health and Garmin Imports

This importer converts Apple Health and Garmin activity exports into normal `Workouts/*.md` notes. Real workout notes and import payloads are ignored by git by default.

## Historical Import

Put source files under `Imports/`, then run from the vault root:

```sh
python3 System/importers/import_workouts.py Imports/apple/export.zip --dry-run
python3 System/importers/import_workouts.py Imports/apple/export.zip
```

Garmin examples:

```sh
python3 System/importers/import_workouts.py Imports/garmin/activities.csv --dry-run
python3 System/importers/import_workouts.py Imports/garmin/activities.csv Imports/garmin/*.tcx Imports/garmin/*.gpx
```

Supported inputs:

- Apple Health `export.zip`
- Apple Health `export.xml`
- Garmin Connect activity CSV
- Garmin TCX files
- Garmin GPX files

The importer writes reports to `Imports/reports/` unless `--report` is supplied.

## Duplicate Rules

The importer never overwrites existing notes.

It skips a workout when:

- an existing note has the same `import_external_id`
- an older manual note looks like the same session:
  - Run: same date, distance within `0.05km`, time within `60s`
  - Swim: same date, distance within `25m`, duration within `2min`
  - Cardio: same date, activity type, duration within `2min`

## 11pm iPhone Shortcut

For future workouts, use a personal automation:

1. Open Shortcuts on iPhone.
2. Go to Automation.
3. Create a Time of Day automation.
4. Set it to `11:00 PM`, daily, and run immediately.
5. Add `Find Health Samples`.
6. Find workouts where the start date is today.
7. Repeat with each workout.
8. If the activity is running, swimming, cycling, HIIT, soccer, basketball, tennis, rowing, elliptical, hiking, or another cardio session, build a Markdown note.
9. Save the file to the vault's `Workouts/` folder in iCloud Drive.
10. Use a file name like `2026-05-17-run-1953.md`.
11. Use the skeletons in `shortcut-note-templates.md` for the Text action.

Shortcut field mapping:

| Health workout | Vault field |
|---|---|
| Activity type is running | `workout_type: "Run"` |
| Activity type is swimming | `workout_type: "Swim"` |
| Activity type is cycling, HIIT, sport, or other cardio | `workout_type: "Cardio"` |
| Distance | `run_distance_km` or `swim_distance_m` |
| Duration | `run_time`, `swim_duration_min`, or `cardio_duration_min` |
| Average heart rate, when available | `run_avg_hr`, `swim_avg_hr`, or `cardio_avg_hr` |

If Shortcuts does not expose a field cleanly, leave it blank. The progress pages already handle missing optional values.
