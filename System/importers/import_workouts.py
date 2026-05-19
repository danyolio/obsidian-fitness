#!/usr/bin/env python3
"""Import Apple Health and Garmin workouts into Obsidian Fitness notes."""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import math
import re
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Iterable
from xml.etree import ElementTree as ET


BLOCK_NAMES = {1: "Endurance", 2: "Strength", 3: "Muscle", 4: "Resilience"}

APPLE_CARDIO = {
    "HKWorkoutActivityTypeCycling": "Cycling",
    "HKWorkoutActivityTypeHighIntensityIntervalTraining": "HIIT",
    "HKWorkoutActivityTypeSoccer": "Soccer",
    "HKWorkoutActivityTypeBasketball": "Basketball",
    "HKWorkoutActivityTypeTennis": "Tennis",
    "HKWorkoutActivityTypeRowing": "Rowing",
    "HKWorkoutActivityTypeElliptical": "Elliptical",
    "HKWorkoutActivityTypeHiking": "Hiking",
    "HKWorkoutActivityTypeMixedCardio": "Other",
    "HKWorkoutActivityTypeStairClimbing": "Other",
    "HKWorkoutActivityTypeCrossTraining": "Other",
}

GARMIN_CARDIO_KEYWORDS = {
    "cycling": "Cycling",
    "biking": "Cycling",
    "bike": "Cycling",
    "hiit": "HIIT",
    "cardio": "Other",
    "soccer": "Soccer",
    "basketball": "Basketball",
    "tennis": "Tennis",
    "rowing": "Rowing",
    "elliptical": "Elliptical",
    "hiking": "Hiking",
}


@dataclass
class ImportedWorkout:
    source: str
    external_id: str
    source_activity_type: str
    workout_type: str
    start: datetime
    end: datetime | None
    metrics: dict[str, Any] = field(default_factory=dict)
    note: str = ""

    @property
    def date_key(self) -> str:
        return local_dt(self.start).date().isoformat()

    @property
    def day_name(self) -> str:
        return local_dt(self.start).strftime("%A")

    @property
    def start_time_key(self) -> str:
        return local_dt(self.start).strftime("%H%M")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Apple Health and Garmin workouts into Workouts/*.md.")
    parser.add_argument("inputs", nargs="+", help="Apple Health export.zip/export.xml, Garmin CSV, TCX, GPX, or folders containing them.")
    parser.add_argument("--vault", default=".", help="Vault root. Defaults to the current directory.")
    parser.add_argument("--output", default="Workouts", help="Workout output folder, relative to the vault root unless absolute.")
    parser.add_argument("--report", default="", help="Import report path. Defaults to Imports/reports/import-<timestamp>.md.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and deduplicate, but do not write workout notes.")
    parser.add_argument("--include-walking", action="store_true", help="Import Apple/Garmin walking and walking-like workouts as Cardio.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    output_dir = Path(args.output).expanduser()
    if not output_dir.is_absolute():
        output_dir = vault / output_dir

    inputs = expand_inputs([Path(p).expanduser() for p in args.inputs])
    if not inputs:
        print("No supported import files found.", file=sys.stderr)
        return 2

    workouts: list[ImportedWorkout] = []
    errors: list[str] = []
    for path in inputs:
        try:
            workouts.extend(parse_input(path, args.include_walking))
        except Exception as exc:  # noqa: BLE001 - CLI should keep importing other files.
            errors.append(f"{path}: {exc}")

    workouts = sorted(workouts, key=lambda w: (w.start, w.source, w.external_id))
    existing = load_existing_notes(output_dir)
    settings = load_settings(vault / "System" / "settings.md")
    result = write_workouts(workouts, output_dir, existing, settings, dry_run=args.dry_run)

    report_path = Path(args.report).expanduser() if args.report else default_report_path(vault)
    write_report(report_path, result, errors, dry_run=args.dry_run)

    print(f"Parsed: {len(workouts)}")
    print(f"{'Would create' if args.dry_run else 'Created'}: {len(result['created'])}")
    print(f"Skipped: {len(result['skipped'])}")
    print(f"Report: {report_path}")
    if args.dry_run:
        print("Dry run: no workout notes were written.")
    return 1 if errors else 0


def expand_inputs(paths: list[Path]) -> list[Path]:
    supported = {".xml", ".zip", ".csv", ".tcx", ".gpx"}
    found: list[Path] = []
    for path in paths:
        if path.is_dir():
            found.extend(p for p in sorted(path.rglob("*")) if p.suffix.lower() in supported)
        elif path.exists() and path.suffix.lower() in supported:
            found.append(path)
    return found


def parse_input(path: Path, include_walking: bool) -> list[ImportedWorkout]:
    suffix = path.suffix.lower()
    if suffix == ".zip":
        return parse_zip(path, include_walking)
    if suffix == ".xml":
        with path.open("rb") as handle:
            kind = sniff_xml_kind(handle)
            handle.seek(0)
            if kind == "apple":
                return parse_apple_health(handle, "apple_health", include_walking)
            if kind == "tcx":
                return parse_tcx(handle, f"garmin_tcx:{path.stem}")
        return []
    if suffix == ".csv":
        return parse_garmin_csv(path)
    if suffix == ".tcx":
        with path.open("rb") as handle:
            return parse_tcx(handle, f"garmin_tcx:{path.stem}")
    if suffix == ".gpx":
        with path.open("rb") as handle:
            return parse_gpx(handle, f"garmin_gpx:{path.stem}", path.stem)
    return []


def parse_zip(path: Path, include_walking: bool) -> list[ImportedWorkout]:
    workouts: list[ImportedWorkout] = []
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        apple = next((name for name in names if name.endswith("export.xml")), "")
        if apple:
            with zf.open(apple) as handle:
                workouts.extend(parse_apple_health(handle, "apple_health", include_walking))
            return workouts
        for name in names:
            lower = name.lower()
            if lower.endswith(".tcx"):
                with zf.open(name) as handle:
                    workouts.extend(parse_tcx(handle, f"garmin_tcx:{Path(name).stem}"))
            elif lower.endswith(".gpx"):
                with zf.open(name) as handle:
                    workouts.extend(parse_gpx(handle, f"garmin_gpx:{Path(name).stem}", Path(name).stem))
    return workouts


def sniff_xml_kind(handle: BinaryIO) -> str:
    sample = handle.read(4096).decode("utf-8", errors="ignore")
    if "<HealthData" in sample:
        return "apple"
    if "TrainingCenterDatabase" in sample:
        return "tcx"
    if "<gpx" in sample:
        return "gpx"
    return ""


def parse_apple_health(handle: BinaryIO, source: str, include_walking: bool) -> list[ImportedWorkout]:
    workouts: list[ImportedWorkout] = []
    heart_rates: list[tuple[float, float]] = []

    for _, elem in ET.iterparse(handle, events=("end",)):
        tag = strip_ns(elem.tag)
        if tag == "Record":
            if elem.attrib.get("type") == "HKQuantityTypeIdentifierHeartRate":
                start = parse_datetime(elem.attrib.get("startDate", ""))
                value = to_float(elem.attrib.get("value"))
                if start and value:
                    heart_rates.append((start.timestamp(), value))
            elem.clear()
            continue

        if tag != "Workout":
            continue

        workout = apple_workout_from_element(elem, source, include_walking)
        if workout:
            workouts.append(workout)
        elem.clear()

    heart_rates.sort(key=lambda row: row[0])
    fill_heart_rates(workouts, heart_rates)
    return workouts


def apple_workout_from_element(elem: ET.Element, source: str, include_walking: bool) -> ImportedWorkout | None:
    attrs = elem.attrib
    activity = attrs.get("workoutActivityType", "")
    start = parse_datetime(attrs.get("startDate", ""))
    end = parse_datetime(attrs.get("endDate", ""))
    if not activity or not start:
        return None

    duration_seconds = duration_to_seconds(attrs.get("duration"), attrs.get("durationUnit"))
    if duration_seconds is None and end:
        duration_seconds = max(0, int((end - start).total_seconds()))

    metadata: dict[str, str] = {}
    stats: dict[str, dict[str, str]] = {}
    for child in elem:
        child_tag = strip_ns(child.tag)
        if child_tag == "MetadataEntry":
            key = child.attrib.get("key", "")
            value = child.attrib.get("value", "")
            if key:
                metadata[key] = value
        elif child_tag == "WorkoutStatistics":
            stat_type = child.attrib.get("type", "")
            if stat_type:
                stats[stat_type] = dict(child.attrib)

    distance_km = distance_to_km(attrs.get("totalDistance"), attrs.get("totalDistanceUnit"))
    if distance_km is None:
        distance_km = apple_stat_distance_km(stats)
    distance_m = distance_km * 1000 if distance_km is not None else None
    avg_hr = apple_stat_heart_rate(stats)

    workout_type, cardio_activity = map_apple_activity(activity, include_walking)
    if not workout_type:
        return None

    sync_id = metadata.get("HKMetadataKeySyncIdentifier") or metadata.get("HKMetadataKeyExternalUUID")
    if sync_id:
        external_id = f"{source}:{sync_id}"
    else:
        stable = f"{activity}:{start.isoformat()}:{end.isoformat() if end else ''}:{distance_km or ''}:{duration_seconds or ''}"
        external_id = f"{source}:{sha1(stable)}"

    metrics: dict[str, Any] = {}
    if workout_type == "Run":
        metrics.update(
            run_type="Imported",
            run_distance_km=distance_km,
            run_time=format_seconds(duration_seconds),
            run_avg_hr=round_int(avg_hr),
            run_zone2_time_min="",
            run_zone4_time_min="",
            run_perceived_effort="",
        )
    elif workout_type == "Swim":
        metrics.update(
            swim_distance_m=round_int(distance_m),
            swim_duration_min=round_minutes(duration_seconds),
            swim_stroke="Mixed",
            swim_1km_time="",
            swim_avg_hr=round_int(avg_hr),
        )
    else:
        metrics.update(
            cardio_activity=cardio_activity or "Other",
            cardio_duration_min=round_minutes(duration_seconds),
            cardio_avg_hr=round_int(avg_hr),
            cardio_perceived_effort="",
        )

    return ImportedWorkout(
        source=source,
        external_id=external_id,
        source_activity_type=activity,
        workout_type=workout_type,
        start=start,
        end=end,
        metrics=drop_none(metrics),
        note="Imported from Apple Health.",
    )


def map_apple_activity(activity: str, include_walking: bool) -> tuple[str, str]:
    if activity == "HKWorkoutActivityTypeRunning":
        return "Run", ""
    if activity == "HKWorkoutActivityTypeSwimming":
        return "Swim", ""
    if activity in APPLE_CARDIO:
        return "Cardio", APPLE_CARDIO[activity]
    if include_walking and activity in {"HKWorkoutActivityTypeWalking", "HKWorkoutActivityTypeHiking"}:
        return "Cardio", "Hiking" if activity.endswith("Hiking") else "Other"
    return "", ""


def apple_stat_distance_km(stats: dict[str, dict[str, str]]) -> float | None:
    for key in (
        "HKQuantityTypeIdentifierDistanceWalkingRunning",
        "HKQuantityTypeIdentifierDistanceCycling",
        "HKQuantityTypeIdentifierDistanceSwimming",
    ):
        stat = stats.get(key)
        if stat:
            return distance_to_km(stat.get("sum"), stat.get("unit"))
    return None


def apple_stat_heart_rate(stats: dict[str, dict[str, str]]) -> float | None:
    stat = stats.get("HKQuantityTypeIdentifierHeartRate")
    if not stat:
        return None
    return to_float(stat.get("average")) or to_float(stat.get("value"))


def fill_heart_rates(workouts: list[ImportedWorkout], heart_rates: list[tuple[float, float]]) -> None:
    if not heart_rates:
        return
    times = [row[0] for row in heart_rates]
    values = [row[1] for row in heart_rates]
    for workout in workouts:
        if any(key.endswith("_avg_hr") and workout.metrics.get(key) for key in workout.metrics):
            continue
        if not workout.end:
            continue
        start_i = bisect.bisect_left(times, workout.start.timestamp())
        end_i = bisect.bisect_right(times, workout.end.timestamp())
        if start_i >= end_i:
            continue
        avg = sum(values[start_i:end_i]) / (end_i - start_i)
        if workout.workout_type == "Run":
            workout.metrics["run_avg_hr"] = round_int(avg)
        elif workout.workout_type == "Swim":
            workout.metrics["swim_avg_hr"] = round_int(avg)
        elif workout.workout_type == "Cardio":
            workout.metrics["cardio_avg_hr"] = round_int(avg)


def parse_garmin_csv(path: Path) -> list[ImportedWorkout]:
    workouts: list[ImportedWorkout] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            workout = garmin_csv_row(row, path.stem, index)
            if workout:
                workouts.append(workout)
    return workouts


def garmin_csv_row(row: dict[str, str], file_stem: str, index: int) -> ImportedWorkout | None:
    activity = cell(row, "Activity Type", "Activity", "Type", "Sport") or "Other"
    date_raw = cell(row, "Date", "Start Time", "Start", "Begin Timestamp")
    start = parse_datetime(date_raw)
    if not start:
        return None

    duration_seconds = parse_duration(cell(row, "Time", "Duration", "Elapsed Time", "Moving Time"))
    distance_km = distance_to_km(cell(row, "Distance", "Distance km", "Distance (km)"), header_unit(row, "distance"))
    avg_hr = to_float(cell(row, "Avg HR", "Average HR", "Avg Heart Rate", "Average Heart Rate"))
    activity_id = cell(row, "Activity ID", "Activity Id", "ID", "UUID")
    external_id = f"garmin_csv:{activity_id}" if activity_id else f"garmin_csv:{file_stem}:{index}:{sha1(str(row))}"

    workout_type, cardio_activity = map_garmin_activity(activity)
    if not workout_type:
        return None

    metrics: dict[str, Any]
    if workout_type == "Run":
        metrics = {
            "run_type": "Imported",
            "run_distance_km": distance_km,
            "run_time": format_seconds(duration_seconds),
            "run_avg_hr": round_int(avg_hr),
            "run_zone2_time_min": "",
            "run_zone4_time_min": "",
            "run_perceived_effort": "",
        }
    elif workout_type == "Swim":
        metrics = {
            "swim_distance_m": round_int(distance_km * 1000) if distance_km is not None else None,
            "swim_duration_min": round_minutes(duration_seconds),
            "swim_stroke": "Mixed",
            "swim_1km_time": "",
            "swim_avg_hr": round_int(avg_hr),
        }
    else:
        metrics = {
            "cardio_activity": cardio_activity or "Other",
            "cardio_duration_min": round_minutes(duration_seconds),
            "cardio_avg_hr": round_int(avg_hr),
            "cardio_perceived_effort": "",
        }

    return ImportedWorkout(
        source="garmin_csv",
        external_id=external_id,
        source_activity_type=activity,
        workout_type=workout_type,
        start=start,
        end=None,
        metrics=drop_none(metrics),
        note="Imported from Garmin Connect CSV.",
    )


def parse_tcx(handle: BinaryIO, source_id: str) -> list[ImportedWorkout]:
    root = ET.parse(handle).getroot()
    workouts: list[ImportedWorkout] = []
    for activity in root.iter():
        if strip_ns(activity.tag) != "Activity":
            continue
        sport = activity.attrib.get("Sport", "Other")
        id_text = first_text(activity, "Id")
        start = parse_datetime(id_text)
        if not start:
            continue
        total_seconds = 0.0
        total_distance_m = 0.0
        heart_values: list[float] = []
        for lap in children_named(activity, "Lap"):
            total_seconds += to_float(first_text(lap, "TotalTimeSeconds")) or 0
            total_distance_m += to_float(first_text(lap, "DistanceMeters")) or 0
            avg = to_float(first_text(lap, "AverageHeartRateBpm", "Value"))
            if avg:
                heart_values.append(avg)
        for point in descendants_named(activity, "Trackpoint"):
            hr = to_float(first_text(point, "HeartRateBpm", "Value"))
            if hr:
                heart_values.append(hr)
        duration_seconds = int(total_seconds) if total_seconds else None
        distance_km = total_distance_m / 1000 if total_distance_m else None
        avg_hr = sum(heart_values) / len(heart_values) if heart_values else None
        workout_type, cardio_activity = map_garmin_activity(sport)
        if not workout_type:
            continue
        external_id = f"{source_id}:{id_text or sha1(ET.tostring(activity, encoding='unicode'))}"
        metrics = metrics_for_garmin(workout_type, cardio_activity, distance_km, duration_seconds, avg_hr)
        workouts.append(
            ImportedWorkout(
                source="garmin_tcx",
                external_id=external_id,
                source_activity_type=sport,
                workout_type=workout_type,
                start=start,
                end=None,
                metrics=metrics,
                note="Imported from Garmin TCX.",
            )
        )
    return workouts


def parse_gpx(handle: BinaryIO, source_id: str, file_stem: str) -> list[ImportedWorkout]:
    root = ET.parse(handle).getroot()
    points: list[tuple[float, float, datetime, float | None]] = []
    for point in root.iter():
        if strip_ns(point.tag) != "trkpt":
            continue
        lat = to_float(point.attrib.get("lat"))
        lon = to_float(point.attrib.get("lon"))
        time_text = first_text(point, "time")
        dt = parse_datetime(time_text)
        hr = None
        for child in point.iter():
            if strip_ns(child.tag).lower() == "hr":
                hr = to_float(child.text)
        if lat is not None and lon is not None and dt:
            points.append((lat, lon, dt, hr))
    if not points:
        return []

    distance_km = 0.0
    for prev, cur in zip(points, points[1:]):
        distance_km += haversine_km(prev[0], prev[1], cur[0], cur[1])
    duration_seconds = int((points[-1][2] - points[0][2]).total_seconds())
    hr_values = [p[3] for p in points if p[3]]
    avg_hr = sum(hr_values) / len(hr_values) if hr_values else None
    source_activity = file_stem
    workout_type, cardio_activity = map_garmin_activity(file_stem)
    if not workout_type:
        workout_type, cardio_activity = "Run", ""
    metrics = metrics_for_garmin(workout_type, cardio_activity, distance_km, duration_seconds, avg_hr)
    return [
        ImportedWorkout(
            source="garmin_gpx",
            external_id=f"{source_id}:{points[0][2].isoformat()}:{sha1(file_stem)}",
            source_activity_type=source_activity,
            workout_type=workout_type,
            start=points[0][2],
            end=points[-1][2],
            metrics=metrics,
            note="Imported from Garmin GPX.",
        )
    ]


def metrics_for_garmin(workout_type: str, cardio_activity: str, distance_km: float | None, duration_seconds: int | None, avg_hr: float | None) -> dict[str, Any]:
    if workout_type == "Run":
        return drop_none(
            {
                "run_type": "Imported",
                "run_distance_km": distance_km,
                "run_time": format_seconds(duration_seconds),
                "run_avg_hr": round_int(avg_hr),
                "run_zone2_time_min": "",
                "run_zone4_time_min": "",
                "run_perceived_effort": "",
            }
        )
    if workout_type == "Swim":
        return drop_none(
            {
                "swim_distance_m": round_int(distance_km * 1000) if distance_km is not None else None,
                "swim_duration_min": round_minutes(duration_seconds),
                "swim_stroke": "Mixed",
                "swim_1km_time": "",
                "swim_avg_hr": round_int(avg_hr),
            }
        )
    return drop_none(
        {
            "cardio_activity": cardio_activity or "Other",
            "cardio_duration_min": round_minutes(duration_seconds),
            "cardio_avg_hr": round_int(avg_hr),
            "cardio_perceived_effort": "",
        }
    )


def map_garmin_activity(activity: str) -> tuple[str, str]:
    text = activity.lower().replace("_", " ")
    if "run" in text or "treadmill" in text:
        return "Run", ""
    if "swim" in text:
        return "Swim", ""
    for key, label in GARMIN_CARDIO_KEYWORDS.items():
        if key in text:
            return "Cardio", label
    return "", ""


def write_workouts(
    workouts: list[ImportedWorkout],
    output_dir: Path,
    existing: list[dict[str, Any]],
    settings: dict[str, str],
    dry_run: bool,
) -> dict[str, list[dict[str, str]]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing_ids = {str(note.get("import_external_id", "")).strip() for note in existing if note.get("import_external_id")}
    result: dict[str, list[dict[str, str]]] = {"created": [], "skipped": []}

    for workout in workouts:
        skip_reason = duplicate_reason(workout, existing, existing_ids)
        file_name = workout_file_name(workout)
        target = output_dir / file_name
        if not skip_reason and target.exists():
            skip_reason = "file exists"
        if skip_reason:
            result["skipped"].append({"date": workout.date_key, "type": workout.workout_type, "reason": skip_reason, "file": file_name})
            continue

        content = render_workout_note(workout, settings)
        if not dry_run:
            target.write_text(content, encoding="utf-8")
            existing.append(parse_note_for_duplicate(target))
            existing_ids.add(workout.external_id)
        result["created"].append({"date": workout.date_key, "type": workout.workout_type, "reason": "dry run" if dry_run else "created", "file": file_name})
    return result


def duplicate_reason(workout: ImportedWorkout, existing: list[dict[str, Any]], existing_ids: set[str]) -> str:
    if workout.external_id in existing_ids:
        return "same import_external_id"
    for note in existing:
        if likely_duplicate(workout, note):
            return "likely manual duplicate"
    return ""


def likely_duplicate(workout: ImportedWorkout, note: dict[str, Any]) -> bool:
    if str(note.get("date", "")) != workout.date_key:
        return False
    if str(note.get("workout_type", "")) != workout.workout_type:
        return False
    metrics = workout.metrics
    if workout.workout_type == "Run":
        dist_a = to_float(note.get("run_distance_km"))
        dist_b = to_float(metrics.get("run_distance_km"))
        time_a = parse_duration(str(note.get("run_time", ""))) or minute_field_seconds(note.get("run_duration_min"))
        time_b = parse_duration(str(metrics.get("run_time", "")))
        return close(dist_a, dist_b, 0.05) and close(time_a, time_b, 60)
    if workout.workout_type == "Swim":
        dist_a = to_float(note.get("swim_distance_m"))
        dist_b = to_float(metrics.get("swim_distance_m"))
        min_a = to_float(note.get("swim_duration_min"))
        min_b = to_float(metrics.get("swim_duration_min"))
        return close(dist_a, dist_b, 25) and close(min_a, min_b, 2)
    if workout.workout_type == "Cardio":
        activity_a = str(note.get("cardio_activity", "")).lower()
        activity_b = str(metrics.get("cardio_activity", "")).lower()
        min_a = to_float(note.get("cardio_duration_min"))
        min_b = to_float(metrics.get("cardio_duration_min"))
        return activity_a == activity_b and close(min_a, min_b, 2)
    return False


def render_workout_note(workout: ImportedWorkout, settings: dict[str, str]) -> str:
    context = program_context(workout.date_key, settings)
    frontmatter: dict[str, Any] = {
        "schema_version": 1,
        "date": workout.date_key,
        "day": workout.day_name,
        "block": context["block"],
        "block_name": context["block_name"],
        "week": context["week"],
        "workout_type": workout.workout_type,
        "import_source": workout.source,
        "import_external_id": workout.external_id,
        "imported_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_activity_type": workout.source_activity_type,
    }
    frontmatter.update(workout.metrics)
    frontmatter["notes"] = ""
    yaml = "\n".join(f"{key}: {yaml_value(value)}" for key, value in frontmatter.items())
    title = f"Imported {workout.workout_type}"
    summary = summary_line(workout)
    return f"---\n{yaml}\n---\n\n# {title}\n\n{summary}\n\n{workout.note}\n"


def summary_line(workout: ImportedWorkout) -> str:
    metrics = workout.metrics
    if workout.workout_type == "Run":
        parts = [metrics.get("run_distance_km") and f"{metrics['run_distance_km']} km", metrics.get("run_time"), metrics.get("run_avg_hr") and f"{metrics['run_avg_hr']} bpm"]
    elif workout.workout_type == "Swim":
        parts = [metrics.get("swim_distance_m") and f"{metrics['swim_distance_m']} m", metrics.get("swim_duration_min") and f"{metrics['swim_duration_min']} min", metrics.get("swim_avg_hr") and f"{metrics['swim_avg_hr']} bpm"]
    else:
        parts = [metrics.get("cardio_activity"), metrics.get("cardio_duration_min") and f"{metrics['cardio_duration_min']} min", metrics.get("cardio_avg_hr") and f"{metrics['cardio_avg_hr']} bpm"]
    return " - ".join(str(part) for part in parts if part) or "Imported workout."


def workout_file_name(workout: ImportedWorkout) -> str:
    slug = {"Run": "run", "Swim": "swim", "Cardio": "cardio"}.get(workout.workout_type, slugify(workout.workout_type))
    return f"{workout.date_key}-{slug}-{workout.start_time_key}.md"


def load_existing_notes(output_dir: Path) -> list[dict[str, Any]]:
    if not output_dir.exists():
        return []
    return [parse_note_for_duplicate(path) for path in output_dir.glob("*.md")]


def parse_note_for_duplicate(path: Path) -> dict[str, Any]:
    data = parse_frontmatter(path)
    data["_path"] = str(path)
    return data


def parse_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data: dict[str, Any] = {}
    for line in text[3:end].splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = clean_yaml_value(value.strip())
    return data


def load_settings(path: Path) -> dict[str, str]:
    return {k: str(v) for k, v in parse_frontmatter(path).items()}


def program_context(date_key: str, settings: dict[str, str]) -> dict[str, Any]:
    start_raw = settings.get("program_start_date", "")
    start_date = datetime_from_date(start_raw)
    workout_date = datetime_from_date(date_key)
    if not start_date or not workout_date or workout_date < start_date:
        return {"block": "", "block_name": "Imported", "week": ""}
    days = (workout_date.date() - start_date.date()).days
    week = max(1, days // 7 + 1)
    block = min(4, (week - 1) // 12 + 1)
    block_name = settings.get("block_name") or BLOCK_NAMES.get(block, "Imported")
    return {"block": block, "block_name": block_name, "week": week}


def write_report(path: Path, result: dict[str, list[dict[str, str]]], errors: list[str], dry_run: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Import Report",
        "",
        f"- Mode: {'dry run' if dry_run else 'write'}",
        f"- {'Would create' if dry_run else 'Created'}: {len(result['created'])}",
        f"- Skipped: {len(result['skipped'])}",
        f"- Errors: {len(errors)}",
        "",
    ]
    if result["created"]:
        lines.extend([f"## {'Would Create' if dry_run else 'Created'}", "", "| Date | Type | File |", "|---|---|---|"])
        lines.extend(f"| {row['date']} | {row['type']} | `{row['file']}` |" for row in result["created"])
        lines.append("")
    if result["skipped"]:
        lines.extend(["## Skipped", "", "| Date | Type | Reason | File |", "|---|---|---|---|"])
        lines.extend(f"| {row['date']} | {row['type']} | {row['reason']} | `{row['file']}` |" for row in result["skipped"])
        lines.append("")
    if errors:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def default_report_path(vault: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    return vault / "Imports" / "reports" / f"import-{stamp}.md"


def cell(row: dict[str, str], *names: str) -> str:
    lookup = {normalize_header(key): value for key, value in row.items()}
    for name in names:
        value = lookup.get(normalize_header(name))
        if value not in (None, ""):
            return str(value).strip()
    return ""


def header_unit(row: dict[str, str], needle: str) -> str:
    for key in row:
        if needle.lower() in key.lower():
            return key
    return ""


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def first_text(elem: ET.Element, *path: str) -> str:
    current = elem
    for name in path:
        found = next((child for child in current if strip_ns(child.tag) == name), None)
        if found is None:
            return ""
        current = found
    return (current.text or "").strip()


def children_named(elem: ET.Element, name: str) -> Iterable[ET.Element]:
    return (child for child in elem if strip_ns(child.tag) == name)


def descendants_named(elem: ET.Element, name: str) -> Iterable[ET.Element]:
    return (child for child in elem.iter() if strip_ns(child.tag) == name)


def parse_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    if re.search(r"[+-]\d{4}$", text):
        text_colon = text[:-5] + text[-5:-2] + ":" + text[-2:]
    else:
        text_colon = text
    for candidate in (text_colon, text):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            pass
    formats = [
        "%Y-%m-%d %H:%M:%S %z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %I:%M %p",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def datetime_from_date(value: Any) -> datetime | None:
    text = str(value or "").strip().strip('"')
    if not text:
        return None
    return parse_datetime(text[:10])


def local_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone()


def parse_duration(value: Any) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    if re.fullmatch(r"\d+(\.\d+)?", text):
        # Garmin numeric duration columns are usually seconds only when labelled as seconds.
        return int(float(text))
    parts = text.split(":")
    if len(parts) == 2 and all(is_number(p) for p in parts):
        return int(float(parts[0]) * 60 + float(parts[1]))
    if len(parts) == 3 and all(is_number(p) for p in parts):
        return int(float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]))
    match = re.search(r"(\d+(?:\.\d+)?)\s*(h|hr|hour|m|min|minute|s|sec|second)", text.lower())
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2)
    if unit.startswith("h"):
        return int(amount * 3600)
    if unit.startswith("m"):
        return int(amount * 60)
    return int(amount)


def duration_to_seconds(value: Any, unit: Any) -> int | None:
    amount = to_float(value)
    if amount is None:
        return None
    unit_text = str(unit or "min").lower()
    if unit_text in {"s", "sec", "second", "seconds"}:
        return int(amount)
    if unit_text in {"h", "hr", "hour", "hours"}:
        return int(amount * 3600)
    return int(amount * 60)


def distance_to_km(value: Any, unit: Any = "") -> float | None:
    amount = to_float(value)
    if amount is None:
        return None
    unit_text = str(unit or "").lower()
    if "mi" in unit_text or "mile" in unit_text:
        return clean_float(amount * 1.609344)
    if re.search(r"\bm\b|meter", unit_text) and "km" not in unit_text:
        return clean_float(amount / 1000)
    if "yd" in unit_text or "yard" in unit_text:
        return clean_float(amount * 0.0009144)
    return clean_float(amount)


def to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    text = str(value).strip().replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def format_seconds(seconds: int | float | None) -> str:
    if seconds is None:
        return ""
    total = max(0, int(round(seconds)))
    minutes = total // 60
    secs = total % 60
    return f"{minutes}:{secs:02d}"


def round_minutes(seconds: int | float | None) -> int | str:
    if seconds is None:
        return ""
    return int(round(float(seconds) / 60))


def round_int(value: float | None) -> int | str:
    if value is None:
        return ""
    return int(round(value))


def clean_float(value: float) -> float:
    rounded = round(value, 2)
    return int(rounded) if rounded.is_integer() else rounded


def minute_field_seconds(value: Any) -> int | None:
    minutes = to_float(value)
    return int(minutes * 60) if minutes is not None else None


def close(a: float | int | None, b: float | int | None, tolerance: float) -> bool:
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) <= tolerance


def drop_none(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


def yaml_value(value: Any) -> str:
    if value is None:
        return '""'
    if value == "":
        return '""'
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if re.fullmatch(r"-?\d+(\.\d+)?", text):
        return text
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def clean_yaml_value(value: str) -> Any:
    text = value.strip()
    if text in {'""', "''"}:
        return ""
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


def sha1(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "workout"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


if __name__ == "__main__":
    raise SystemExit(main())
