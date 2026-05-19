# Swimming

```dataviewjs
const wrap = dv.container;
const todayKey = window.moment ? window.moment().format("YYYY-MM-DD") : new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
const currentYear = todayKey.slice(0, 4);
const sessions = dv.pages('"Workouts"')
  .where(p => p.workout_type === "Swim" && p.date)
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

function toSeconds(value) {
  if (value === null || value === undefined || value === "") return null;
  const parts = String(value).trim().split(":").map(Number);
  if (parts.length === 1 && Number.isFinite(parts[0])) return parts[0] * 60;
  if (parts.length === 2 && parts.every(Number.isFinite)) return parts[0] * 60 + parts[1];
  if (parts.length === 3 && parts.every(Number.isFinite)) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return null;
}

function timeLabel(seconds) {
  if (!seconds) return "-";
  const min = Math.floor(seconds / 60);
  const sec = String(Math.round(seconds % 60)).padStart(2, "0");
  return `${min}:${sec}`;
}

function distance(rows) {
  return rows.reduce((sum, p) => sum + num(p.swim_distance_m), 0);
}

function minutes(rows) {
  return rows.reduce((sum, p) => sum + num(p.swim_duration_min), 0);
}

function pace1k(p) {
  const explicit = toSeconds(p.swim_1km_time);
  if (explicit) return explicit;
  const dist = num(p.swim_distance_m);
  const mins = num(p.swim_duration_min);
  if (!dist || !mins) return null;
  return mins * 60 / dist * 1000;
}

function card(parent, label, value, sub, color) {
  const el = parent.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-top:2px solid ${color};border-radius:16px;padding:14px;min-width:0;`}});
  el.createEl("div", {text:label, attr:{style:"font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);"}});
  el.createEl("div", {text:value, attr:{style:"font-size:24px;font-weight:820;color:#fff;margin-top:5px;line-height:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  el.createEl("div", {text:sub, attr:{style:"font-size:11px;color:rgba(255,255,255,0.45);margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
}

const week = sessions.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 7);
const year = sessions.filter(p => dateKey(p.date).startsWith(`${currentYear}-`));
const best1k = sessions
  .map(p => ({p, seconds:pace1k(p)}))
  .filter(row => row.seconds)
  .sort((a, b) => a.seconds - b.seconds)[0];

wrap.createEl("h2", {text:"Swim Snapshot"});
const grid = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:8px 0 22px;"}});
card(grid, "7D Distance", `${distance(week)}m`, `${minutes(week)} min`, "#AF52DE");
card(grid, `${currentYear} Distance`, `${distance(year)}m`, `${year.length} swims`, "#5AC8FA");
card(grid, "Best 1km", best1k ? timeLabel(best1k.seconds) : (settings.swim_1km_pb || "-"), best1k ? dateKey(best1k.p.date) : "from settings", "#30D158");
card(grid, "Goal", settings.swim_1km_goal || "-", "1km benchmark", "#FF9500");

wrap.createEl("h2", {text:"Recent Swims"});
const list = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;"}});
for (const p of sessions.slice().reverse().slice(0, 14)) {
  const row = list.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:center;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:14px;padding:12px 14px;"}});
  const left = row.createEl("div", {attr:{style:"min-width:0;"}});
  left.createEl("div", {text:dateKey(p.date), attr:{style:"font-size:13px;font-weight:760;color:#fff;"}});
  left.createEl("div", {text:[p.swim_stroke || "Swim", p.swim_duration_min ? `${p.swim_duration_min} min` : "", p.swim_avg_hr ? `${p.swim_avg_hr} bpm` : ""].filter(Boolean).join(" · "), attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  const right = row.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});
  right.createEl("div", {text:num(p.swim_distance_m) ? `${num(p.swim_distance_m)}m` : "-", attr:{style:"font-size:14px;font-weight:820;color:#AF52DE;"}});
  right.createEl("div", {text:pace1k(p) ? `${timeLabel(pace1k(p))}/1k` : "", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:2px;"}});
}
if (!sessions.length) list.createEl("div", {text:"No swims logged yet.", attr:{style:"font-size:13px;color:rgba(255,255,255,0.45);"}});
```
