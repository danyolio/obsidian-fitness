# Calisthenics

```dataviewjs
const wrap = dv.container;
const todayKey = window.moment ? window.moment().format("YYYY-MM-DD") : new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
const currentYear = todayKey.slice(0, 4);
const currentYearStart = `${currentYear}-01-01`;
const sessions = dv.pages('"Workouts"')
  .where(p => p.workout_type === "Calisthenics" && p.date)
  .array()
  .sort((a, b) => dateKey(a.date).localeCompare(dateKey(b.date)));

const movements = [
  {key:"pullup", label:"Pull-ups", color:"#5AC8FA", volume:true},
  {key:"row", label:"Rows", color:"#AF52DE", volume:true},
  {key:"dip", label:"Dips", color:"#FF9500", volume:true},
  {key:"pushup", label:"Push-ups", color:"#5856D6", volume:true},
  {key:"squat", label:"Squats", color:"#30D158", volume:true},
  {key:"hinge", label:"Hinge", color:"#FFCC00", volume:false}
];

function dateKey(value) {
  return value?.toISODate?.() || String(value || "").slice(0, 10);
}

function dateObj(value) {
  return new Date(dateKey(value) + "T00:00:00");
}

function daysAgo(value) {
  return Math.floor((dateObj(todayKey) - dateObj(value)) / 86400000);
}

function rep(p, key, set) {
  return Number(p[`rr_${key}_s${set}_reps`]) || 0;
}

function total(p, key) {
  return rep(p, key, 1) + rep(p, key, 2) + rep(p, key, 3);
}

function bestSet(p, key) {
  return Math.max(rep(p, key, 1), rep(p, key, 2), rep(p, key, 3));
}

function progression(p, key) {
  return p[`rr_${key}_progression`] || "";
}

function load(p, key) {
  const v = Number(p[`rr_${key}_weight`]) || 0;
  return v ? v + "kg" : "";
}

function sumIn(key, days) {
  return sessions
    .filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < days)
    .reduce((sum, p) => sum + total(p, key), 0);
}

function sumYear(key) {
  return sessions
    .filter(p => dateKey(p.date).startsWith(`${currentYear}-`))
    .reduce((sum, p) => sum + total(p, key), 0);
}

function bestBy(key, fn) {
  return sessions
    .map(p => ({p, value:fn(p, key)}))
    .filter(r => r.value > 0)
    .sort((a, b) => b.value - a.value || dateKey(b.p.date).localeCompare(dateKey(a.p.date)))[0] || null;
}

function latestWith(key) {
  return sessions.slice().reverse().find(p => total(p, key) || progression(p, key));
}

function avgPerWeek(total, days) {
  return (total / Math.max(1, days / 7)).toFixed(1);
}

wrap.createEl("h2", {text:"Rep Volume"});
const volumeGrid = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:8px 0 20px;"}});
for (const m of movements.filter(m => m.volume)) {
  const all = sessions.reduce((sum, p) => sum + total(p, m.key), 0);
  const last7 = sumIn(m.key, 7);
  const last28 = sumIn(m.key, 28);
  const ytd = sumYear(m.key);
  const card = volumeGrid.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-top:2px solid ${m.color};border-radius:16px;padding:14px;min-width:0;`}});
  card.createEl("div", {text:m.label, attr:{style:"font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);"}});
  card.createEl("div", {text:all + " reps", attr:{style:"font-size:23px;font-weight:820;color:#fff;margin-top:4px;line-height:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  card.createEl("div", {text:`7d ${last7} - 28d ${avgPerWeek(last28, 28)}/wk - ${currentYear} ${avgPerWeek(ytd, Math.max(7, daysAgo(currentYearStart) + 1))}/wk`, attr:{style:"font-size:10px;color:rgba(255,255,255,0.45);margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
}

wrap.createEl("h2", {text:"PR Board"});
const board = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;margin-bottom:22px;"}});
for (const m of movements) {
  const totalPR = bestBy(m.key, total);
  const setPR = bestBy(m.key, bestSet);
  const latest = latestWith(m.key);
  const row = board.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-left:3px solid ${m.color};border-radius:12px;padding:10px 12px;`}});
  const head = row.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:baseline;"}});
  head.createEl("div", {text:m.label, attr:{style:"font-size:13px;font-weight:760;color:#fff;"}});
  head.createEl("div", {text:totalPR ? totalPR.value + " total" : "-", attr:{style:`font-size:13px;font-weight:820;color:${m.color};white-space:nowrap;`}});
  const detail = [
    setPR ? "best set " + setPR.value : "",
    totalPR ? dateKey(totalPR.p.date) : "",
    latest ? "current " + (progression(latest, m.key) || "unlisted") : "",
    latest ? load(latest, m.key) : ""
  ].filter(Boolean).join(" - ");
  row.createEl("div", {text:detail || "No reps logged yet", attr:{style:"font-size:12px;color:rgba(255,255,255,0.45);margin-top:3px;"}});
}

wrap.createEl("h2", {text:"Session History"});
const history = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;"}});
for (const p of sessions.slice().reverse()) {
  const row = history.createEl("div", {attr:{style:"background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:10px 12px;"}});
  const head = row.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:baseline;"}});
  head.createEl("div", {text:dateKey(p.date), attr:{style:"font-size:13px;font-weight:740;color:#fff;"}});
  head.createEl("div", {text:p.rr_duration_min ? p.rr_duration_min + " min" : "No duration", attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);"}});
  const detail = movements.map(m => {
    const t = total(p, m.key);
    return t ? `${m.label} ${t}` : "";
  }).filter(Boolean).join(" - ");
  row.createEl("div", {text:detail || "No reps logged", attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);margin-top:4px;"}});
}
```
