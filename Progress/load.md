# Load Management

```dataviewjs
const wrap = dv.container;
const meta = {
  Run:{color:"#FF3B30", group:"Cardio", duration:null},
  Swim:{color:"#AF52DE", group:"Cardio", duration:"swim_duration_min"},
  Cardio:{color:"#FF2D55", group:"Cardio", duration:"cardio_duration_min"},
  Lift:{color:"#FF9500", group:"Strength", duration:null},
  Calisthenics:{color:"#5856D6", group:"Strength", duration:"rr_duration_min"},
  Climb:{color:"#30D158", group:"Strength", duration:"climb_duration_min"},
  KOT:{color:"#5AC8FA", group:"Mobility", duration:"kot_duration_min"},
  Yoga:{color:"#AF52DE", group:"Mobility", duration:"yoga_duration_min"},
  Sauna:{color:"#FFCC00", group:"Mobility", duration:"sauna_duration_min"}
};
const bands = {
  Deload:{color:"#5AC8FA", label:"Deload", tone:"Very light"},
  Low:{color:"#30D158", label:"Low", tone:"Room to build"},
  Medium:{color:"#FFCC00", label:"Balanced", tone:"On track"},
  High:{color:"#FF9500", label:"High", tone:"Back off soon"}
};

const normalizeType = wt => wt === "Knees Over Toes" ? "KOT" : wt;
const number = v => Number(v) || 0;
const dateKey = value => value?.toISODate?.() || String(value || "").slice(0, 10);
const todayKey = window.moment ? window.moment().format("YYYY-MM-DD") : new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
const currentYear = todayKey.slice(0, 4);
const currentYearStart = `${currentYear}-01-01`;
const dateObj = value => new Date(dateKey(value) + "T00:00:00");
const localKey = d => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
const daysBetween = (a, b) => Math.floor((dateObj(a) - dateObj(b)) / 86400000);
const toSeconds = value => {
  if (value === null || value === undefined || value === "") return null;
  const parts = String(value).trim().split(":").map(Number);
  if (parts.length === 1 && Number.isFinite(parts[0])) return parts[0] * 60;
  if (parts.length === 2 && parts.every(Number.isFinite)) return parts[0] * 60 + parts[1];
  if (parts.length === 3 && parts.every(Number.isFinite)) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return null;
};
const runSeconds = p => toSeconds(p.run_time) || (number(p.run_duration_min) ? number(p.run_duration_min) * 60 : null);
const minutes = p => {
  const wt = normalizeType(p.workout_type);
  if (wt === "Run") return runSeconds(p) ? runSeconds(p) / 60 : 0;
  const field = meta[wt]?.duration;
  return field ? number(p[field]) : 0;
};

function weekStart(value) {
  const d = dateObj(value);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
  return localKey(d);
}

function shiftWeek(value, offset) {
  const d = dateObj(value);
  d.setDate(d.getDate() + offset * 7);
  return localKey(d);
}

function classify(hours, baseline) {
  const base = Math.max(baseline || 0, 1);
  if (hours < 1 || hours < base * 0.55) return "Deload";
  if (hours < base * 0.85) return "Low";
  if (hours <= base * 1.2) return "Medium";
  return "High";
}

function ratio(hours, baseline) {
  return hours / Math.max(baseline || 0, 1);
}

function nextMove(currentBand, currentRatio, rows) {
  let highStreak = 0;
  for (const row of rows) {
    if (row.band !== "High") break;
    highStreak++;
  }
  if (currentBand === "High" && (highStreak >= 2 || currentRatio >= 1.6)) return {text:"Deload next", sub:"High load is stacking", color:"#5AC8FA"};
  if (currentBand === "High") return {text:"Low week next", sub:"Let this week land", color:"#30D158"};
  if (currentBand === "Deload") return {text:"Rebuild gently", sub:"Light week already", color:"#30D158"};
  if (currentBand === "Low") return {text:"Room to build", sub:"Add volume if you feel good", color:"#30D158"};
  return {text:"Stay steady", sub:"Load is in range", color:"#FFCC00"};
}

function statCard(parent, label, value, sub, color) {
  const el = parent.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.10);border-top:2px solid ${color};border-radius:15px;padding:12px;min-width:0;`}});
  el.createEl("div", {text:label, attr:{style:"font-size:10px;font-weight:820;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);"}});
  el.createEl("div", {text:value, attr:{style:"font-size:19px;font-weight:840;color:#fff;margin-top:5px;line-height:1.05;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  el.createEl("div", {text:sub, attr:{style:"font-size:11px;color:rgba(255,255,255,0.44);margin-top:6px;line-height:1.25;"}});
}

function loadChart(parent, rows, baseline) {
  const w = 340, h = 184, left = 42, right = 14, top = 20, bottom = 28;
  const chartW = w - left - right;
  const chartH = h - top - bottom;
  const maxHours = Math.max(...rows.map(r => r.hours), baseline, 1);
  const axisMax = Math.ceil(maxHours * 1.15);
  const ticks = [axisMax, axisMax / 2, 0];
  const yFor = value => top + chartH - (value / axisMax) * chartH;
  const points = rows.map((r, i) => {
    const x = left + (i / Math.max(1, rows.length - 1)) * chartW;
    const y = yFor(r.hours);
    return {...r, x, y};
  });
  const line = points.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
  const avgY = yFor(Math.min(baseline, axisMax));
  const startLabel = rows[0]?.week.slice(5).replace("-", "/") || "";
  const endLabel = rows[rows.length - 1]?.week.slice(5).replace("-", "/") || "";
  const box = parent.createEl("div", {attr:{style:"background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.09);border-radius:16px;padding:10px;margin:8px 0 22px;"}});
  box.innerHTML = `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;display:block;">
    <rect x="0" y="0" width="${w}" height="${h}" rx="14" fill="rgba(255,255,255,0.018)"/>
    ${ticks.map(t => `<line x1="${left}" y1="${yFor(t).toFixed(1)}" x2="${w - right}" y2="${yFor(t).toFixed(1)}" stroke="rgba(255,255,255,0.08)"/><text x="${left - 8}" y="${(yFor(t) + 3).toFixed(1)}" text-anchor="end" fill="rgba(255,255,255,0.42)" font-size="9" font-weight="700">${t.toFixed(t === 0 ? 0 : 1)}h</text>`).join("")}
    <line x1="${left}" y1="${top}" x2="${left}" y2="${h - bottom}" stroke="rgba(255,255,255,0.14)"/>
    <line x1="${left}" y1="${h - bottom}" x2="${w - right}" y2="${h - bottom}" stroke="rgba(255,255,255,0.14)"/>
    <line x1="${left}" y1="${avgY.toFixed(1)}" x2="${w - right}" y2="${avgY.toFixed(1)}" stroke="rgba(255,255,255,0.28)" stroke-dasharray="4 5"/>
    <polyline points="${line}" fill="none" stroke="#FF9500" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    ${points.map(p => `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.7" fill="${bands[p.band].color}" stroke="rgba(0,0,0,0.48)" stroke-width="1"/>`).join("")}
    <text x="${w - right - 50}" y="${Math.max(13, avgY - 5).toFixed(1)}" fill="rgba(255,255,255,0.46)" font-size="9" font-weight="700">4wk avg</text>
    <text x="${left}" y="${h - 8}" fill="rgba(255,255,255,0.35)" font-size="9">${startLabel}</text>
    <text x="${w - right - 28}" y="${h - 8}" fill="rgba(255,255,255,0.35)" font-size="9">${endLabel}</text>
  </svg>`;
}

const workouts = dv.pages('"Workouts"').where(p => p.date && p.workout_type).array();
const currentWeekStart = weekStart(todayKey);
const recent28 = workouts.filter(p => daysBetween(todayKey, p.date) >= 0 && daysBetween(todayKey, p.date) < 28);
const thisWeek = workouts.filter(p => weekStart(p.date) === currentWeekStart);
const yearWorkouts = workouts.filter(p => dateKey(p.date).startsWith(`${currentYear}-`));

const monthHours = recent28.reduce((sum, p) => sum + minutes(p), 0) / 60;
const monthAvg = monthHours / 4;
const first = workouts.map(p => dateKey(p.date)).sort()[0] || todayKey;
const allWeeks = Math.max(1, Math.ceil((daysBetween(todayKey, first) + 1) / 7));
const totalHours = workouts.reduce((sum, p) => sum + minutes(p), 0) / 60;
const allAvg = totalHours / allWeeks;
const baseline = monthAvg || allAvg;
const yearWeeks = Math.max(1, Math.ceil((daysBetween(todayKey, currentYearStart) + 1) / 7));
const yearHours = yearWorkouts.reduce((sum, p) => sum + minutes(p), 0) / 60;
const yearAvg = yearHours / yearWeeks;

const weekly = new Map();
for (const p of workouts) {
  const key = weekStart(p.date);
  if (!weekly.has(key)) weekly.set(key, {sessions:0, minutes:0, groups:{Cardio:0, Strength:0, Mobility:0}});
  const row = weekly.get(key);
  const wt = normalizeType(p.workout_type);
  const mins = minutes(p);
  row.sessions++;
  row.minutes += mins;
  const group = meta[wt]?.group || "Other";
  row.groups[group] = (row.groups[group] || 0) + 1;
}
if (!weekly.has(currentWeekStart)) weekly.set(currentWeekStart, {sessions:0, minutes:0, groups:{Cardio:0, Strength:0, Mobility:0}});

const rows = Array.from({length:12}, (_, i) => {
  const week = shiftWeek(currentWeekStart, -i);
  const raw = weekly.get(week) || {sessions:0, minutes:0, groups:{Cardio:0, Strength:0, Mobility:0}};
  const hours = raw.minutes / 60;
  const band = classify(hours, baseline);
  return {week, ...raw, hours, band, ratio:ratio(hours, baseline)};
});
const current = rows[0];
const rec = nextMove(current.band, current.ratio, rows);
const currentBand = bands[current.band];

const hero = wrap.createEl("div", {attr:{style:`background:linear-gradient(158deg,rgba(255,255,255,0.07),rgba(255,255,255,0.025));border:1px solid rgba(255,255,255,0.12);border-left:4px solid ${currentBand.color};border-radius:18px;padding:16px 16px;margin:8px 0 12px;box-shadow:0 8px 30px rgba(0,0,0,0.32);`}});
hero.createEl("div", {text:"Current Load", attr:{style:"font-size:10px;font-weight:820;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);"}});
hero.createEl("div", {text:currentBand.label, attr:{style:`font-size:32px;font-weight:860;color:${currentBand.color};line-height:1;margin-top:8px;`}});
hero.createEl("div", {text:`${current.hours.toFixed(1)}h this week · ${current.sessions} sessions · ${current.ratio.toFixed(1)}x 4-week average`, attr:{style:"font-size:13px;color:rgba(255,255,255,0.54);margin-top:8px;line-height:1.35;"}});
hero.createEl("div", {text:`Next week: ${rec.text}. ${rec.sub}.`, attr:{style:"font-size:13px;color:rgba(255,255,255,0.76);margin-top:10px;line-height:1.35;"}});

const top = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:8px 0 18px;"}});
statCard(top, "4wk Avg", baseline.toFixed(1) + "h/wk", monthHours.toFixed(1) + "h in 28d", "#AF52DE");
statCard(top, `${currentYear} Avg`, yearAvg.toFixed(1) + "h/wk", yearHours.toFixed(1) + "h this year", "#5AC8FA");

wrap.createEl("h2", {text:"12-Week Hours"});
loadChart(wrap, rows.slice().reverse(), baseline);

wrap.createEl("h2", {text:"Recent Weeks"});
const list = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;margin-bottom:22px;"}});
const maxMin = Math.max(...rows.map(r => r.minutes), 1);
for (const row of rows.slice(0, 8)) {
  const band = bands[row.band];
  const weekLabel = row.week === currentWeekStart ? "This week" : row.week;
  const item = list.createEl("div", {attr:{style:`background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-left:3px solid ${band.color};border-radius:14px;padding:11px 13px;`}});
  const head = item.createEl("div", {attr:{style:"display:flex;justify-content:space-between;align-items:flex-start;gap:12px;"}});
  const left = head.createEl("div", {attr:{style:"min-width:0;"}});
  left.createEl("div", {text:weekLabel, attr:{style:"font-size:13px;font-weight:740;color:#fff;"}});
  left.createEl("div", {text:`${row.hours.toFixed(1)}h · ${row.sessions} sessions · ${row.ratio.toFixed(1)}x avg`, attr:{style:"font-size:12px;color:rgba(255,255,255,0.45);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  left.createEl("div", {text:`Cardio ${row.groups.Cardio || 0} · Strength ${row.groups.Strength || 0} · Mobility ${row.groups.Mobility || 0}`, attr:{style:"font-size:11px;color:rgba(255,255,255,0.32);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  const right = head.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;min-width:72px;"}});
  right.createEl("div", {text:band.label, attr:{style:`font-size:13px;font-weight:840;color:${band.color};white-space:nowrap;`}});
  right.createEl("div", {text:band.tone, attr:{style:"font-size:10px;color:rgba(255,255,255,0.38);margin-top:3px;white-space:nowrap;"}});
  const bar = item.createEl("div", {attr:{style:"height:6px;background:rgba(255,255,255,0.08);border-radius:99px;overflow:hidden;margin-top:9px;"}});
  bar.createEl("div", {attr:{style:`height:100%;width:${Math.max(3, row.minutes / maxMin * 100).toFixed(0)}%;background:${band.color};border-radius:99px;`}});
}
```
