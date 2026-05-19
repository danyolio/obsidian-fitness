# History

```dataviewjs
const wrap = dv.container;
const currentFile = dv.current().file.path;
const icons = {Run:"Run", Lift:"Lift", Calisthenics:"Calis", KOT:"Knees Over Toes", Climb:"Climb", Swim:"Swim", Yoga:"Yoga", Sauna:"Sauna", Cardio:"Cardio"};
const colors = {Run:"#FF3B30", Lift:"#FF9500", Calisthenics:"#5856D6", KOT:"#5AC8FA", Climb:"#30D158", Swim:"#AF52DE", Yoga:"#AF52DE", Sauna:"#FFCC00", Cardio:"#FF2D55"};
const normalizeType = wt => wt === "Knees Over Toes" ? "KOT" : wt;
const num = v => Number(v) || 0;
const runTimeLabel = p => p.run_time || (num(p.run_duration_min) ? p.run_duration_min + " min" : "");

function getStat(p) {
  const wt = normalizeType(p.workout_type);
  if (wt === "Run") {
    const parts = [];
    if (p.run_distance_km > 0) parts.push(p.run_distance_km + " km");
    if (runTimeLabel(p)) parts.push(runTimeLabel(p));
    if (p.run_avg_hr > 0) parts.push(p.run_avg_hr + " bpm");
    return parts.join(" - ") || "-";
  }
  if (wt === "Lift" && p.lift_top_set_prescribed_weight > 0) return (p.lift_exercise || "Lift") + " " + p.lift_top_set_prescribed_weight + "kg x " + (p.lift_top_set_actual_reps || "?");
  if (wt === "Climb") {
    const parts = [];
    if (p.climb_max_grade) parts.push(p.climb_max_grade);
    if (p.climb_problems_sent > 0) parts.push(p.climb_problems_sent + "/" + (p.climb_problems_attempted || "?") + " sent");
    if (p.climb_duration_min > 0) parts.push(p.climb_duration_min + " min");
    return parts.join(" - ") || "-";
  }
  if (wt === "Swim" && p.swim_distance_m > 0) return p.swim_distance_m + "m " + (p.swim_1km_time || "");
  if (wt === "Cardio" && p.cardio_duration_min > 0) {
    const parts = [p.cardio_activity || "Cardio", p.cardio_duration_min + " min"];
    if (p.cardio_avg_hr > 0) parts.push(p.cardio_avg_hr + " bpm");
    return parts.join(" - ");
  }
  const durField = {Calisthenics:"rr_duration_min", KOT:"kot_duration_min", Yoga:"yoga_duration_min", Sauna:"sauna_duration_min"}[wt];
  return durField && p[durField] > 0 ? p[durField] + " min" : "-";
}

const all = dv.pages('"Workouts"')
  .where(p => p.workout_type)
  .sort(p => p.date, "desc");

const card = wrap.createEl("div", {attr:{style:"background:linear-gradient(158deg,rgba(255,255,255,0.068),rgba(255,255,255,0.028));border:1px solid rgba(255,255,255,0.12);border-radius:18px;overflow:hidden;"}});

for (let i = 0; i < all.length; i++) {
  const p = all[i];
  const wt = normalizeType(p.workout_type);
  const c = colors[wt] || "#fff";
  const d = p.date ? new Date(p.date.toString()) : new Date();
  const ds = d.toLocaleDateString("en-GB", {weekday:"short", day:"numeric", month:"short"});

  const row = card.createEl("div", {attr:{style:"display:flex;align-items:center;gap:13px;padding:14px 16px;cursor:pointer;" + (i === all.length - 1 ? "" : "border-bottom:1px solid rgba(255,255,255,0.06);")}});
  row.createEl("div", {attr:{style:`width:8px;height:8px;border-radius:50%;background:${c};box-shadow:0 0 8px ${c}88;flex-shrink:0;`}});

  const info = row.createEl("div", {attr:{style:"flex:1;min-width:0;"}});
  const title = info.createEl("div", {attr:{style:"display:flex;align-items:center;gap:7px;"}});
  title.createEl("span", {text:icons[wt] || wt, attr:{style:"font-size:14px;font-weight:740;color:#fff;"}});
  info.createEl("div", {text:getStat(p), attr:{style:"font-size:12px;color:rgba(255,255,255,0.4);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px;"}});

  row.createEl("div", {text:ds, attr:{style:"font-size:12px;color:rgba(255,255,255,0.38);flex-shrink:0;"}});
  row.addEventListener("click", () => app.workspace.openLinkText(p.file.path, currentFile));
}
```
