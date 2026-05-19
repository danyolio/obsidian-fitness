# Strength

```dataviewjs
const wrap = dv.container;
const todayKey = window.moment ? window.moment().format("YYYY-MM-DD") : new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
const currentYear = todayKey.slice(0, 4);
const lifts = ["deadlift", "squat", "bench", "ohp"];
const colors = {deadlift:"#FF9500", squat:"#30D158", bench:"#FF3B30", ohp:"#5AC8FA"};
const names = {deadlift:"Deadlift", squat:"Squat", bench:"Bench", ohp:"OHP"};
const sessions = dv.pages('"Workouts"')
  .where(p => p.workout_type === "Lift" && p.date)
  .array()
  .sort((a, b) => dateKey(a.date).localeCompare(dateKey(b.date)));
const settings = dv.page("System/settings") || {};

function dateKey(value) {
  return value?.toISODate?.() || String(value || "").slice(0, 10);
}

function dateObj(value) {
  return new Date(dateKey(value) + "T00:00:00");
}

function daysAgo(value) {
  return Math.floor((dateObj(todayKey) - dateObj(value)) / 86400000);
}

function num(value) {
  return Number(value) || 0;
}

function title(value) {
  return String(value || "").replace(/\b\w/g, ch => ch.toUpperCase());
}

function estMax(weight, reps) {
  if (!weight || !reps) return 0;
  return Math.round(weight * (1 + reps / 30));
}

function topWeight(p) {
  return num(p.lift_top_set_prescribed_weight) || num(p.lift_s3_weight);
}

function topReps(p) {
  return num(p.lift_top_set_actual_reps) || num(p.lift_s3_reps);
}

function topLabel(p) {
  const weight = topWeight(p);
  const reps = topReps(p);
  return weight ? `${weight}kg x ${reps || "?"}` : "-";
}

function liftName(p) {
  return String(p.lift_exercise || "").toLowerCase();
}

function card(parent, label, value, sub, color) {
  const el = parent.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-top:2px solid ${color};border-radius:16px;padding:14px;min-width:0;`}});
  el.createEl("div", {text:label, attr:{style:"font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);"}});
  el.createEl("div", {text:value, attr:{style:"font-size:24px;font-weight:820;color:#fff;margin-top:5px;line-height:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  el.createEl("div", {text:sub, attr:{style:"font-size:11px;color:rgba(255,255,255,0.45);margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
}

const week = sessions.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 7);
const year = sessions.filter(p => dateKey(p.date).startsWith(`${currentYear}-`));
const hardSets = week.filter(p => topReps(p) >= 5 || num(p.lift_rpe) >= 8).length;
const best = sessions
  .map(p => ({p, value:estMax(topWeight(p), topReps(p))}))
  .filter(row => row.value)
  .sort((a, b) => b.value - a.value)[0];

wrap.createEl("h2", {text:"Strength Snapshot"});
const grid = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:8px 0 22px;"}});
card(grid, "7D Sessions", String(week.length), `${hardSets} hard sets`, "#FF9500");
card(grid, `${currentYear} Sessions`, String(year.length), "lift days", "#5AC8FA");
card(grid, "Best Est Max", best ? `${best.value}kg` : "-", best ? `${title(best.p.lift_exercise)} · ${dateKey(best.p.date)}` : "No top sets yet", "#30D158");
card(grid, "Training Maxes", lifts.filter(lift => num(settings[`tm_${lift}`])).length + "/4", "configured", "#AF52DE");

wrap.createEl("h2", {text:"Main Lifts"});
const board = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;margin-bottom:22px;"}});
for (const lift of lifts) {
  const rows = sessions.filter(p => liftName(p) === lift);
  const latest = rows[rows.length - 1];
  const pr = rows
    .map(p => ({p, value:estMax(topWeight(p), topReps(p))}))
    .filter(row => row.value)
    .sort((a, b) => b.value - a.value || dateKey(b.p.date).localeCompare(dateKey(a.p.date)))[0];
  const tm = num(settings[`tm_${lift}`]);
  const row = board.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-left:3px solid ${colors[lift]};border-radius:14px;padding:12px 14px;`}});
  const head = row.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:baseline;"}});
  head.createEl("div", {text:names[lift], attr:{style:"font-size:14px;font-weight:800;color:#fff;"}});
  head.createEl("div", {text:pr ? `${pr.value}kg est` : "-", attr:{style:`font-size:14px;font-weight:850;color:${colors[lift]};white-space:nowrap;`}});
  const detail = [
    latest ? `last ${topLabel(latest)}` : "not logged",
    latest ? dateKey(latest.date) : "",
    tm ? `TM ${tm}kg` : ""
  ].filter(Boolean).join(" · ");
  row.createEl("div", {text:detail, attr:{style:"font-size:12px;color:rgba(255,255,255,0.45);margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
}

wrap.createEl("h2", {text:"Recent Lifts"});
const history = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;"}});
for (const p of sessions.slice().reverse().slice(0, 12)) {
  const color = colors[liftName(p)] || "#FF9500";
  const row = history.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:center;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:14px;padding:12px 14px;"}});
  const left = row.createEl("div", {attr:{style:"min-width:0;"}});
  left.createEl("div", {text:title(p.lift_exercise || "Lift"), attr:{style:"font-size:13px;font-weight:760;color:#fff;"}});
  left.createEl("div", {text:[dateKey(p.date), p.lift_week ? `week ${p.lift_week}` : "", p.lift_rpe ? `RPE ${p.lift_rpe}` : ""].filter(Boolean).join(" · "), attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  const right = row.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});
  right.createEl("div", {text:topLabel(p), attr:{style:`font-size:14px;font-weight:820;color:${color};`}});
  right.createEl("div", {text:estMax(topWeight(p), topReps(p)) ? `${estMax(topWeight(p), topReps(p))}kg est` : "", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:2px;"}});
}
if (!sessions.length) history.createEl("div", {text:"No lift sessions logged yet.", attr:{style:"font-size:13px;color:rgba(255,255,255,0.45);"}});
```
