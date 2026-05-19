# Shortcut Note Templates

Use these as starting points for Shortcuts `Text` actions. Replace bracketed values with Shortcut variables. If a value is unavailable, use `""`.

## Run

```md
---
schema_version: 1
date: "[Workout Date]"
day: "[Workout Day]"
block: ""
block_name: "Imported"
week: ""
workout_type: "Run"
import_source: "apple_shortcuts"
import_external_id: "apple_shortcuts:[Workout Start ISO]:[Workout Type]"
imported_at: "[Current Date ISO]"
source_activity_type: "[Workout Type]"
run_type: "Imported"
run_distance_km: [Distance KM]
run_time: "[MM:SS]"
run_avg_hr: [Average HR]
run_zone2_time_min: ""
run_zone4_time_min: ""
run_perceived_effort: ""
notes: ""
---

# Imported Run
```

## Swim

```md
---
schema_version: 1
date: "[Workout Date]"
day: "[Workout Day]"
block: ""
block_name: "Imported"
week: ""
workout_type: "Swim"
import_source: "apple_shortcuts"
import_external_id: "apple_shortcuts:[Workout Start ISO]:[Workout Type]"
imported_at: "[Current Date ISO]"
source_activity_type: "[Workout Type]"
swim_distance_m: [Distance M]
swim_duration_min: [Duration Min]
swim_stroke: "Mixed"
swim_1km_time: ""
swim_avg_hr: [Average HR]
notes: ""
---

# Imported Swim
```

## Cardio

```md
---
schema_version: 1
date: "[Workout Date]"
day: "[Workout Day]"
block: ""
block_name: "Imported"
week: ""
workout_type: "Cardio"
import_source: "apple_shortcuts"
import_external_id: "apple_shortcuts:[Workout Start ISO]:[Workout Type]"
imported_at: "[Current Date ISO]"
source_activity_type: "[Workout Type]"
cardio_activity: "[Cycling, HIIT, Soccer, Basketball, Tennis, Rowing, Elliptical, Hiking, Other]"
cardio_duration_min: [Duration Min]
cardio_avg_hr: [Average HR]
cardio_perceived_effort: ""
notes: ""
---

# Imported Cardio
```
