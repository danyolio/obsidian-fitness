---
cssclasses:
  - fitness-settings
display_name: Daniel
program_start_date: 2026-03-04
hemisphere: Southern
current_block: Auto
block_name: ""
blocks:
  "1": Endurance
  "2": Strength
  "3": Muscle
  "4": Resilience
rr_pushup: ""
rr_row: ""
rr_dip: ""
rr_pullup: ""
rr_pike: ""
rr_squat: ""
rr_hinge: ""
kot_locomotion: ""
kot_tibialis: ""
kot_fhl_calf: ""
kot_atg_split: ""
kot_stepup: ""
kot_nordic: ""
kot_seated_gm: ""
lift_primary: ""
lift_secondary: ""
tm_deadlift: ""
tm_squat: ""
tm_bench: ""
tm_ohp: ""
swim_1km_pb: ""
swim_1km_goal: ""
---

# Settings

```dataviewjs
const cfg = dv.current();
const clean = value => String(value || "").trim();
const displayName = clean(cfg.display_name) || "Athlete";
const blockNames = {1:"Endurance",2:"Strength",3:"Muscle",4:"Resilience"};
const block = Number(cfg.current_block);
const blockLabel = block >= 1 && block <= 4 ? `Block ${block}` : "Auto";
const hemisphere = clean(cfg.hemisphere).toLowerCase().startsWith("n") ? "Northern" : "Southern";
const isOverride = value => {
  const text = clean(value).toLowerCase();
  return text && !["auto", "last logged", "null", "none"].includes(text);
};
const configured = ["rr_pullup","rr_row","rr_dip","rr_pushup","rr_squat","rr_hinge"].filter(key => isOverride(cfg[key])).length;
const tms = ["tm_deadlift","tm_squat","tm_bench","tm_ohp"].filter(key => Number(cfg[key]) > 0).length;

const hero = dv.container.createEl("div", {attr:{style:"background:linear-gradient(158deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03));border:1px solid rgba(255,255,255,0.12);border-radius:20px;padding:20px;margin:8px 0 20px;box-shadow:0 8px 34px rgba(0,0,0,0.42),inset 0 1px 0 rgba(255,255,255,0.12);"}});
hero.createEl("div", {text:"Control Panel", attr:{style:"font-size:24px;font-weight:850;color:#fff;line-height:1.05;"}});
hero.createEl("div", {text:"Programme, progressions, training maxes, and personal targets.", attr:{style:"font-size:13px;color:rgba(255,255,255,0.50);line-height:1.45;margin-top:9px;"}});
const chips = hero.createEl("div", {attr:{style:"display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;"}});
const chip = (label, value, color) => {
  const el = chips.createEl("div", {attr:{style:`background:${color}1f;border:1px solid ${color}55;border-radius:999px;padding:7px 10px;min-width:0;`}});
  el.createEl("span", {text:label + " ", attr:{style:"font-size:10px;font-weight:820;letter-spacing:.5px;text-transform:uppercase;color:rgba(255,255,255,0.45);"}});
  el.createEl("span", {text:value, attr:{style:`font-size:12px;font-weight:850;color:${color};`}});
};
chip("Profile", displayName, "#FF3B30");
chip("Block", blockLabel, "#5AC8FA");
chip("Hemisphere", hemisphere, "#AF52DE");
chip("Progressions", `${configured}/6`, configured ? "#30D158" : "#8E8E93");
chip("Strength", `${tms}/4 TMs`, tms ? "#FF9500" : "#8E8E93");
```

> [!tip|settings]+ Program
> **Display name** `INPUT[text(placeholder(Athlete)):display_name]`
>
> **Start date** `INPUT[datePicker:program_start_date]`
>
> **Hemisphere** `INPUT[suggester(option(Southern), option(Northern)):hemisphere]`
>
> **Current block** `INPUT[suggester(option(Auto), option(1), option(2), option(3), option(4)):current_block]`
>
> **Block name** `INPUT[text(placeholder(Optional label)):block_name]`

```dataviewjs
const clean = value => {
  if (value === null || value === undefined) return "";
  return String(value).replace(/^["']|["']$/g, "").trim();
};
const number = value => Number(value) || 0;
const dateKey = value => value?.toISODate?.() || clean(value);
const allWorkouts = dv.pages('"Workouts"')
  .where(p => clean(p.workout_type))
  .sort(p => p.date, "desc")
  .array();
const normType = value => {
  const text = clean(value).toLowerCase();
  if (text === "kot" || text === "knees over toes") return "KOT";
  if (text === "run") return "Run";
  if (text === "lift") return "Lift";
  if (text === "calisthenics") return "Calisthenics";
  if (text === "climb") return "Climb";
  if (text === "swim") return "Swim";
  if (text === "yoga") return "Yoga";
  if (text === "sauna") return "Sauna";
  if (text === "cardio") return "Cardio";
  return text.replace(/\b\w/g, ch => ch.toUpperCase());
};
const latest = type => allWorkouts.find(p => normType(p.workout_type) === type);
const runTime = p => clean(p?.run_time) || (number(p?.run_duration_min) ? `${p.run_duration_min} min` : "");
const reps = (p, key) => [1,2,3].reduce((sum, set) => sum + number(p?.[`rr_${key}_s${set}_reps`]), 0);
const rrSummary = p => {
  const parts = [
    clean(p?.rr_pullup_progression),
    clean(p?.rr_row_progression),
    clean(p?.rr_pushup_progression)
  ].filter(Boolean);
  const total = ["pullup","row","dip","pushup","squat","hinge"].reduce((sum, key) => sum + reps(p, key), 0);
  if (total) parts.push(`${total} reps`);
  return parts;
};
const types = [
  {type:"Run", color:"#FF3B30", detail:p => [clean(p?.run_type) || "Run", p?.run_distance_km ? `${p.run_distance_km} km` : "", runTime(p), p?.run_avg_hr ? `${p.run_avg_hr} bpm` : ""].filter(Boolean)},
  {type:"Lift", color:"#FF9500", detail:p => [clean(p?.lift_exercise) || "Lift", p?.lift_top_set_prescribed_weight ? `${p.lift_top_set_prescribed_weight} kg` : "", p?.lift_top_set_actual_reps ? `${p.lift_top_set_actual_reps} reps` : ""].filter(Boolean)},
  {type:"Calisthenics", color:"#5856D6", detail:rrSummary},
  {type:"KOT", label:"Knees Over Toes", color:"#5AC8FA", detail:p => [clean(p?.kot_locomotion_prog), clean(p?.kot_tib_prog), clean(p?.kot_fhl_prog), p?.kot_duration_min ? `${p.kot_duration_min} min` : ""].filter(Boolean)},
  {type:"Climb", color:"#30D158", detail:p => [clean(p?.climb_max_grade), p?.climb_problems_sent ? `${p.climb_problems_sent}/${p.climb_problems_attempted || "?"} sent` : "", p?.climb_duration_min ? `${p.climb_duration_min} min` : ""].filter(Boolean)},
  {type:"Swim", color:"#AF52DE", detail:p => [p?.swim_distance_m ? `${p.swim_distance_m} m` : "", clean(p?.swim_stroke), clean(p?.swim_1km_time), p?.swim_duration_min ? `${p.swim_duration_min} min` : ""].filter(Boolean)},
  {type:"Yoga", color:"#AF52DE", detail:p => [clean(p?.yoga_style) || "Yoga", p?.yoga_duration_min ? `${p.yoga_duration_min} min` : ""].filter(Boolean)},
  {type:"Sauna", color:"#FFCC00", detail:p => [p?.sauna_rounds ? `${p.sauna_rounds} rounds` : "", clean(p?.sauna_type), p?.sauna_duration_min ? `${p.sauna_duration_min} min` : ""].filter(Boolean)},
  {type:"Cardio", color:"#FF2D55", detail:p => [clean(p?.cardio_activity) || "Cardio", p?.cardio_duration_min ? `${p.cardio_duration_min} min` : "", p?.cardio_avg_hr ? `${p.cardio_avg_hr} bpm` : "", p?.cardio_perceived_effort ? `RPE ${p.cardio_perceived_effort}` : ""].filter(Boolean)}
];

const panel = dv.container.createEl("div", {attr:{style:"background:rgba(255,255,255,0.036);border:1px solid rgba(255,255,255,0.09);border-radius:20px;padding:18px 16px;margin:18px 0 24px;box-shadow:0 8px 30px rgba(0,0,0,0.34),inset 0 1px 0 rgba(255,255,255,0.09);"}});
const header = panel.createEl("div", {attr:{style:"display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px;"}});
header.createEl("div", {text:"Last Logged", attr:{style:"font-size:13px;font-weight:840;letter-spacing:.9px;text-transform:uppercase;color:#fff;"}});
header.createEl("div", {text:"by workout type", attr:{style:"font-size:10px;font-weight:820;letter-spacing:.55px;text-transform:uppercase;color:rgba(255,255,255,.42);"}});
const grid = panel.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:10px;"}});
for (const item of types) {
  const p = latest(item.type);
  const details = p ? item.detail(p) : [];
  const card = grid.createEl("div", {attr:{style:`min-width:0;padding:12px 13px;border:1px solid rgba(255,255,255,.075);border-left:3px solid ${item.color};border-radius:14px;background:rgba(255,255,255,.030);`}})
  card.createEl("div", {text:item.label || item.type, attr:{style:`font-size:10px;font-weight:830;letter-spacing:.65px;text-transform:uppercase;color:${item.color};margin-bottom:6px;`}});
  card.createEl("div", {text:details.join(" · ") || "Nothing logged yet", attr:{style:"font-size:14px;font-weight:760;color:rgba(255,255,255,.88);line-height:1.25;white-space:normal;overflow-wrap:anywhere;"}});
  card.createEl("div", {text:p ? dateKey(p.date) : "No history", attr:{style:"font-size:11px;color:rgba(255,255,255,.42);margin-top:6px;"}});
}
```

```dataviewjs
const cfg = dv.current();
const file = app.vault.getAbstractFileByPath(cfg.file.path);
const clean = value => {
  if (value === null || value === undefined) return "";
  return String(value).replace(/^["']|["']$/g, "").trim();
};
const override = value => {
  const text = clean(value);
  return ["auto", "last logged", "null", "none"].includes(text.toLowerCase()) ? "" : text;
};
const workouts = dv.pages('"Workouts"')
  .where(p => p.workout_type === "Calisthenics")
  .sort(p => p.date, "desc")
  .array();
const movements = [
  {key:"pullup", setting:"rr_pullup", label:"Pull-up", color:"#5AC8FA", steps:["Scapular Pull-up","Arch Hang","Negative Pull-up","Pull-up","L-sit Pull-up","Weighted Pull-up"]},
  {key:"row", setting:"rr_row", label:"Row", color:"#AF52DE", steps:["Vertical Row","Incline Row","Horizontal Row","Wide Row","Tuck Front Lever Row","Advanced Tuck Front Lever Row"]},
  {key:"dip", setting:"rr_dip", label:"Dip", color:"#FF9500", steps:["Parallel Bar Support Hold","Negative Dip","Parallel Bar Dip","Ring RTO Dip","Weighted Dip"]},
  {key:"pushup", setting:"rr_pushup", label:"Push-up", color:"#5856D6", steps:["Wall Push-up","Incline Push-up","Standard Push-up","Diamond Push-up","Pseudo Planche Push-up","Ring Push-up","Weighted Push-up"]},
  {key:"squat", setting:"rr_squat", label:"Squat", color:"#30D158", steps:["Assisted Squat","Bodyweight Squat","Split Squat","Bulgarian Split Squat","Beginner Shrimp Squat","Intermediate Shrimp Squat","Advanced Shrimp Squat","Partial ROM Pistol Squat","Pistol Squat","Weighted Pistol Squat"]},
  {key:"hinge", setting:"rr_hinge", label:"Hinge", color:"#FFD60A", steps:["Beginner Harop Curl","Harop Curl","Advanced Harop Curl","Banded Nordic Curl","Nordic Curl"]}
];
function latestProgression(key) {
  const field = `rr_${key}_progression`;
  const session = workouts.find(p => clean(p[field]));
  return session ? {value:clean(session[field]), date:session.date?.toISODate?.() || clean(session.date)} : {value:"", date:""};
}
function writeSetting(key, value) {
  app.fileManager.processFrontMatter(file, fm => {
    fm[key] = value || "";
  });
}
const panel = dv.container.createEl("div", {attr:{style:"background:rgba(255,255,255,0.036);border:1px solid rgba(255,255,255,0.09);border-radius:20px;padding:18px 16px;margin:18px 0 24px;box-shadow:0 8px 30px rgba(0,0,0,0.34),inset 0 1px 0 rgba(255,255,255,0.09);"}});
const header = panel.createEl("div", {attr:{style:"display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px;"}});
header.createEl("div", {text:"Calisthenics", attr:{style:"font-size:13px;font-weight:840;letter-spacing:.9px;text-transform:uppercase;color:#5856D6;"}});
header.createEl("div", {text:"auto from workouts", attr:{style:"font-size:10px;font-weight:820;letter-spacing:.55px;text-transform:uppercase;color:rgba(255,255,255,.42);"}});
const grid = panel.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px;"}});
for (const movement of movements) {
  const explicit = override(cfg[movement.setting]);
  const latest = latestProgression(movement.key);
  const effective = explicit || latest.value;
  const card = grid.createEl("div", {attr:{style:"min-width:0;padding:13px 14px;border:1px solid rgba(255,255,255,0.075);border-radius:15px;background:rgba(255,255,255,0.030);"}});
  const top = card.createEl("div", {attr:{style:"display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:9px;"}});
  top.createEl("div", {text:movement.label, attr:{style:"font-size:9px;font-weight:830;letter-spacing:.85px;color:rgba(255,255,255,.36);text-transform:uppercase;"}});
  top.createEl("div", {text:explicit ? "override" : (latest.date || "unset"), attr:{style:`font-size:9px;font-weight:820;letter-spacing:.55px;text-transform:uppercase;color:${explicit ? movement.color : "rgba(255,255,255,.38)"};white-space:nowrap;`}});
  const row = card.createEl("div", {attr:{style:"display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;"}});
  const select = row.createEl("select", {attr:{style:"width:100%;min-width:0;min-height:46px;margin:0;padding:10px 38px 10px 12px;border-radius:13px;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.10);color:rgba(255,255,255,0.92);font-size:16px;font-weight:720;box-sizing:border-box;"}});
  if (!effective) {
    const empty = select.createEl("option", {text:"Choose progression", attr:{value:""}});
    empty.selected = true;
  }
  const options = [...new Set([effective, ...movement.steps].filter(Boolean))];
  for (const option of options) {
    const el = select.createEl("option", {text:option, attr:{value:option}});
    if (option === effective) el.selected = true;
  }
  select.onchange = () => writeSetting(movement.setting, select.value);
  const reset = row.createEl("button", {text:"Auto", attr:{style:`min-height:42px;padding:0 11px;border-radius:13px;border:1px solid ${explicit ? movement.color + "88" : "rgba(255,255,255,.08)"};background:${explicit ? movement.color + "22" : "rgba(255,255,255,.035)"};color:${explicit ? movement.color : "rgba(255,255,255,.36)"};font-size:11px;font-weight:830;text-transform:uppercase;letter-spacing:.5px;`}});
  reset.onclick = () => writeSetting(movement.setting, "");
}
```

> [!success|settings]- Calisthenics Overrides
> **Pike / HSPU** `INPUT[text(placeholder(Optional progression)):rr_pike]`

```dataviewjs
const cfg = dv.current();
const file = app.vault.getAbstractFileByPath(cfg.file.path);
const clean = value => {
  if (value === null || value === undefined) return "";
  return String(value).replace(/^["']|["']$/g, "").trim();
};
const override = value => {
  const text = clean(value);
  return ["auto", "last logged", "null", "none"].includes(text.toLowerCase()) ? "" : text;
};
const workouts = dv.pages('"Workouts"')
  .where(p => p.workout_type === "KOT" || p.workout_type === "Knees Over Toes")
  .sort(p => p.date, "desc")
  .array();
const movements = [
  {field:"kot_locomotion_prog", setting:"kot_locomotion", label:"Locomotion", color:"#5AC8FA", steps:["Backward Walk - Flat","Backward Walk - Incline","Sled Pull - Light","Sled Pull - Heavy"]},
  {field:"kot_tib_prog", setting:"kot_tibialis", label:"Tibialis", color:"#5AC8FA", steps:["Wall - Close","Wall - Far","Tib Bar - Double Leg","Tib Bar - Single Leg"]},
  {field:"kot_fhl_prog", setting:"kot_fhl_calf", label:"FHL calf", color:"#5AC8FA", steps:["Flat Ground - Double Leg","Flat Ground - Single Leg","Deficit - Single Leg","Deficit Weighted"]},
  {field:"kot_atg_prog", setting:"kot_atg_split", label:"ATG split squat", color:"#5AC8FA", steps:["Front Foot Elevated - Assisted","Front Foot Elevated - Unassisted","Flat Ground","Weighted - Dumbbells","Weighted - Barbell"]},
  {field:"kot_stepup_prog", setting:"kot_stepup", label:"Step-up", color:"#5AC8FA", steps:["Flat Ground - Patrick","Heel Elevated - Poliquin","Weighted - Poliquin"]},
  {field:"kot_nordic_prog", setting:"kot_nordic", label:"Nordic", color:"#5AC8FA", steps:["Band Assisted","Eccentric Only","Partial Concentric","Full Strict ROM"]},
  {field:"kot_gm_prog", setting:"kot_seated_gm", label:"Seated good morning", color:"#5AC8FA", steps:["Straddle Stretch","Empty Barbell","Weighted Barbell"]}
];
function latestProgression(field) {
  const session = workouts.find(p => clean(p[field]));
  return session ? {value:clean(session[field]), date:session.date?.toISODate?.() || clean(session.date)} : {value:"", date:""};
}
function writeSetting(key, value) {
  app.fileManager.processFrontMatter(file, fm => {
    fm[key] = value || "";
  });
}
const panel = dv.container.createEl("div", {attr:{style:"background:rgba(255,255,255,0.036);border:1px solid rgba(255,255,255,0.09);border-radius:20px;padding:18px 16px;margin:18px 0 24px;box-shadow:0 8px 30px rgba(0,0,0,0.34),inset 0 1px 0 rgba(255,255,255,0.09);"}});
const header = panel.createEl("div", {attr:{style:"display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:14px;"}});
header.createEl("div", {text:"Knees Over Toes", attr:{style:"font-size:13px;font-weight:840;letter-spacing:.9px;text-transform:uppercase;color:#5AC8FA;"}});
header.createEl("div", {text:"auto from workouts", attr:{style:"font-size:10px;font-weight:820;letter-spacing:.55px;text-transform:uppercase;color:rgba(255,255,255,.42);"}});
const grid = panel.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px;"}});
for (const movement of movements) {
  const explicit = override(cfg[movement.setting]);
  const latest = latestProgression(movement.field);
  const effective = explicit || latest.value;
  const card = grid.createEl("div", {attr:{style:"min-width:0;padding:13px 14px;border:1px solid rgba(255,255,255,0.075);border-radius:15px;background:rgba(255,255,255,0.030);"}});
  const top = card.createEl("div", {attr:{style:"display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:9px;"}});
  top.createEl("div", {text:movement.label, attr:{style:"font-size:9px;font-weight:830;letter-spacing:.85px;color:rgba(255,255,255,.36);text-transform:uppercase;"}});
  top.createEl("div", {text:explicit ? "override" : (latest.date || "unset"), attr:{style:`font-size:9px;font-weight:820;letter-spacing:.55px;text-transform:uppercase;color:${explicit ? movement.color : "rgba(255,255,255,.38)"};white-space:nowrap;`}});
  const row = card.createEl("div", {attr:{style:"display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;"}});
  const select = row.createEl("select", {attr:{style:"width:100%;min-width:0;min-height:46px;margin:0;padding:10px 38px 10px 12px;border-radius:13px;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.10);color:rgba(255,255,255,0.92);font-size:16px;font-weight:720;box-sizing:border-box;"}});
  if (!effective) {
    const empty = select.createEl("option", {text:"Choose progression", attr:{value:""}});
    empty.selected = true;
  }
  const options = [...new Set([effective, ...movement.steps].filter(Boolean))];
  for (const option of options) {
    const el = select.createEl("option", {text:option, attr:{value:option}});
    if (option === effective) el.selected = true;
  }
  select.onchange = () => writeSetting(movement.setting, select.value);
  const reset = row.createEl("button", {text:"Auto", attr:{style:`min-height:42px;padding:0 11px;border-radius:13px;border:1px solid ${explicit ? movement.color + "88" : "rgba(255,255,255,.08)"};background:${explicit ? movement.color + "22" : "rgba(255,255,255,.035)"};color:${explicit ? movement.color : "rgba(255,255,255,.36)"};font-size:11px;font-weight:830;text-transform:uppercase;letter-spacing:.5px;`}});
  reset.onclick = () => writeSetting(movement.setting, "");
}
```

> [!example|settings]- Strength
> **Primary lift** `INPUT[suggester(option(deadlift), option(squat), option(bench), option(ohp)):lift_primary]`
>
> **Secondary lift** `INPUT[suggester(option(deadlift), option(squat), option(bench), option(ohp)):lift_secondary]`
>
> **Deadlift TM** `INPUT[number(placeholder(kg)):tm_deadlift]`
>
> **Squat TM** `INPUT[number(placeholder(kg)):tm_squat]`
>
> **Bench TM** `INPUT[number(placeholder(kg)):tm_bench]`
>
> **OHP TM** `INPUT[number(placeholder(kg)):tm_ohp]`

> [!info|settings]- Swimming
> **1km PB** `INPUT[text(placeholder(MM:SS)):swim_1km_pb]`
>
> **1km goal** `INPUT[text(placeholder(MM:SS)):swim_1km_goal]`

> [!abstract|settings]- Reference
> [[Reference/blocks|Blocks]] · [[Reference/programs|Programs]] · [[Reference/exercises|Exercise]]
