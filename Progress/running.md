# Running

```dataviewjs
const wrap = dv.container;
const todayKey = window.moment ? window.moment().format("YYYY-MM-DD") : new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
const currentYear = todayKey.slice(0, 4);
const currentYearStart = `${currentYear}-01-01`;
const workouts = dv.pages('"Workouts"')
  .where(p => p.workout_type && p.date)
  .array()
  .sort((a, b) => dateKey(a.date).localeCompare(dateKey(b.date)));
const runs = workouts.filter(p => p.workout_type === "Run");
const cardio = workouts.filter(p => p.workout_type === "Cardio");
const yearRuns = runs.filter(p => dateKey(p.date).startsWith(`${currentYear}-`));
const yearCardio = cardio.filter(p => dateKey(p.date).startsWith(`${currentYear}-`));
const sportKmRate = {soccer:0.09, basketball:0.07, tennis:0.06, cycling:0.28, hiit:0.08, rowing:0.16, elliptical:0.10, hiking:0.06, imported:0.05, other:0.05};

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

function sportKm(p) {
  const activity = String(p.cardio_activity || "other").toLowerCase();
  return num(p.cardio_duration_min) * (sportKmRate[activity] || sportKmRate.other);
}

function sportName(p) {
  return String(p.cardio_activity || "Sport").replace(/\b\w/g, ch => ch.toUpperCase());
}

function toSeconds(value) {
  if (value === null || value === undefined || value === "") return null;
  const parts = String(value).trim().split(":").map(Number);
  if (parts.length === 1 && Number.isFinite(parts[0])) return parts[0] * 60;
  if (parts.length === 2 && parts.every(Number.isFinite)) return parts[0] * 60 + parts[1];
  if (parts.length === 3 && parts.every(Number.isFinite)) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return null;
}

function runSeconds(p) {
  return toSeconds(p.run_time) || (num(p.run_duration_min) ? num(p.run_duration_min) * 60 : null);
}

function runMinutes(p) {
  const seconds = runSeconds(p);
  return seconds ? seconds / 60 : 0;
}

function runTimeLabel(p) {
  return p.run_time || (num(p.run_duration_min) ? p.run_duration_min + " min" : "");
}

function pace(seconds) {
  if (!seconds) return "-";
  const min = Math.floor(seconds / 60);
  const sec = String(Math.round(seconds % 60)).padStart(2, "0");
  return `${min}:${sec}`;
}

function runPace(p) {
  const distance = num(p.run_distance_km);
  const seconds = runSeconds(p);
  if (!distance || !seconds) return p.run_avg_pace ? String(p.run_avg_pace) : "";
  return `${pace(seconds / distance)}/km`;
}

function fiveKSeconds(p) {
  const explicit = toSeconds(p.run_5km_time);
  if (explicit) return explicit;
  const distance = num(p.run_distance_km);
  const seconds = runSeconds(p);
  if (!distance || !seconds) return null;
  if (distance >= 4.8 && distance <= 5.2) return seconds / distance * 5;
  return null;
}

function avgSeconds(rows) {
  const values = rows.map(fiveKSeconds).filter(Boolean);
  if (!values.length) return null;
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

function card(parent, label, value, sub, color) {
  const el = parent.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-top:2px solid ${color};border-radius:16px;padding:14px;min-width:0;`}});
  el.createEl("div", {text:label, attr:{style:"font-size:10px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);"}});
  el.createEl("div", {text:value, attr:{style:"font-size:24px;font-weight:820;color:#fff;margin-top:5px;line-height:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  el.createEl("div", {text:sub, attr:{style:"font-size:11px;color:rgba(255,255,255,0.45);margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
}

function renderRows(title, rows, empty) {
  wrap.createEl("h2", {text:title});
  if (!rows.length) {
    wrap.createEl("div", {text:empty, attr:{style:"font-size:13px;color:rgba(255,255,255,0.45);margin:6px 0 18px;"}});
    return;
  }
  const list = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;margin-bottom:22px;"}});
  const best = Math.min(...rows.map(r => r.sec));
  for (const row of rows) {
    const el = list.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:center;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:14px;padding:12px 14px;"}});
    const left = el.createEl("div", {attr:{style:"min-width:0;"}});
    left.createEl("div", {text:dateKey(row.p.date), attr:{style:"font-size:13px;font-weight:740;color:#fff;"}});
    left.createEl("div", {text:[row.p.run_type || "Run", row.p.run_distance_km ? row.p.run_distance_km + "km" : "", runTimeLabel(row.p), row.p.run_avg_hr ? row.p.run_avg_hr + " bpm" : ""].filter(Boolean).join(" - "), attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
    const right = el.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});
    right.createEl("div", {text:pace(row.sec), attr:{style:"font-size:15px;font-weight:820;color:#FF3B30;"}});
    right.createEl("div", {text:row.sec === best ? "PR" : "+" + pace(row.sec - best), attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:2px;"}});
  }
}

function renderSportRows(title, rows, empty) {
  wrap.createEl("h2", {text:title});
  if (!rows.length) {
    wrap.createEl("div", {text:empty, attr:{style:"font-size:13px;color:rgba(255,255,255,0.45);margin:6px 0 18px;"}});
    return;
  }
  const list = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;margin-bottom:22px;"}});
  for (const row of rows) {
    const el = list.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:center;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:14px;padding:12px 14px;"}});
    const left = el.createEl("div", {attr:{style:"min-width:0;"}});
    left.createEl("div", {text:sportName(row.p), attr:{style:"font-size:13px;font-weight:740;color:#fff;"}});
    left.createEl("div", {text:[dateKey(row.p.date), row.p.cardio_duration_min ? row.p.cardio_duration_min + " min" : "", row.p.cardio_avg_hr ? row.p.cardio_avg_hr + " bpm" : ""].filter(Boolean).join(" - "), attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
    const right = el.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});
    right.createEl("div", {text:row.km.toFixed(1) + "km", attr:{style:"font-size:15px;font-weight:820;color:#FF2D55;"}});
    right.createEl("div", {text:"estimate", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:2px;"}});
  }
}

function isoDate(d) {
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

function weekStart(value) {
  const d = dateObj(value);
  const diff = (d.getDay() + 6) % 7;
  d.setDate(d.getDate() - diff);
  return d;
}

function weekLabel(d) {
  return d.toLocaleDateString(undefined, {month:"short", day:"numeric"});
}

function avg(values) {
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function runningChart(parent, runSource, sportSource) {
  const weekCount = 12;
  const end = weekStart(todayKey);
  const weeks = Array.from({length:weekCount}, (_, i) => {
    const start = new Date(end);
    start.setDate(end.getDate() - (weekCount - 1 - i) * 7);
    return {start, key:isoDate(start), runKm:0, sportKm:0, minutes:0, hr:[]};
  });
  const byWeek = new Map(weeks.map(week => [week.key, week]));

  for (const p of runSource) {
    const week = byWeek.get(isoDate(weekStart(p.date)));
    if (!week) continue;
    week.runKm += num(p.run_distance_km);
    week.minutes += runMinutes(p);
    if (num(p.run_avg_hr)) week.hr.push(num(p.run_avg_hr));
  }

  for (const p of sportSource) {
    const week = byWeek.get(isoDate(weekStart(p.date)));
    if (!week) continue;
    week.sportKm += sportKm(p);
    week.minutes += num(p.cardio_duration_min);
    if (num(p.cardio_avg_hr)) week.hr.push(num(p.cardio_avg_hr));
  }

  const rows = weeks.map(week => ({
    ...week,
    totalKm: week.runKm + week.sportKm,
    avgHr: avg(week.hr)
  }));
  const thisWeek = rows[rows.length - 1];
  const maxKm = Math.max(5, ...rows.map(row => row.totalKm));
  const hrRows = rows.map((row, i) => ({i, value:row.avgHr})).filter(row => row.value);
  const minHr = hrRows.length ? Math.min(...hrRows.map(row => row.value)) : 0;
  const maxHr = hrRows.length ? Math.max(...hrRows.map(row => row.value)) : 0;
  const hrSpread = Math.max(1, maxHr - minHr);
  const w = 340, h = 214, left = 36, right = 24, top = 28, bottom = 34;
  const chartW = w - left - right;
  const chartH = h - top - bottom;
  const step = chartW / rows.length;
  const barW = Math.max(8, step * 0.58);
  const xMid = i => left + step * i + step / 2;
  const yKm = value => top + chartH - (value / maxKm) * chartH;
  const yHr = value => top + chartH - ((value - minHr) / hrSpread) * chartH;
  const grid = [1, 0.5, 0].map(t => {
    const y = top + chartH - t * chartH;
    const label = Math.round(maxKm * t);
    return `<line x1="${left}" y1="${y.toFixed(1)}" x2="${w - right}" y2="${y.toFixed(1)}" stroke="rgba(255,255,255,0.07)"/>
      <text x="4" y="${(y + 3).toFixed(1)}" fill="rgba(255,255,255,0.34)" font-size="9" font-weight="700">${label}km</text>`;
  }).join("");
  const bars = rows.map((row, i) => {
    const x = xMid(i) - barW / 2;
    const y = yKm(row.totalKm);
    const height = Math.max(2, top + chartH - y);
    const fill = row.totalKm >= maxKm * 0.75 ? "#FF3B30" : row.totalKm >= maxKm * 0.45 ? "#FF9500" : "#5AC8FA";
    return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${height.toFixed(1)}" rx="4" fill="${fill}" opacity="0.9"/>`;
  }).join("");
  const hrLine = hrRows.length > 1
    ? hrRows.map(row => `${xMid(row.i).toFixed(1)},${yHr(row.value).toFixed(1)}`).join(" ")
    : "";
  const hrDots = hrRows.map(row => `<circle cx="${xMid(row.i).toFixed(1)}" cy="${yHr(row.value).toFixed(1)}" r="2.7" fill="#34D399"/>`).join("");
  const startLabel = weekLabel(rows[0].start);
  const endLabel = weekLabel(rows[rows.length - 1].start);
  const hrRange = hrRows.length ? `${Math.round(minHr)}-${Math.round(maxHr)} bpm` : "HR empty";

  const box = parent.createEl("div", {attr:{style:"background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:18px;padding:13px 13px 11px;margin:2px 0 22px;"}});
  const head = box.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin:0 2px 8px;"}});
  const leftHead = head.createEl("div", {attr:{style:"min-width:0;"}});
  leftHead.createEl("div", {text:"12 Week Running Trend", attr:{style:"font-size:14px;font-weight:820;color:#fff;"}});
  leftHead.createEl("div", {text:"weekly km + average HR", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:3px;"}});
  const rightHead = head.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});
  rightHead.createEl("div", {text:thisWeek.totalKm.toFixed(1) + "km", attr:{style:"font-size:18px;font-weight:850;color:#FF3B30;line-height:1;"}});
  rightHead.createEl("div", {text:Math.round(thisWeek.minutes) + " min", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:5px;"}});
  const svg = box.createEl("div");
  svg.innerHTML = `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;display:block;">
    <rect x="0" y="0" width="${w}" height="${h}" rx="15" fill="rgba(255,255,255,0.018)"/>
    ${grid}
    ${bars}
    ${hrLine ? `<polyline points="${hrLine}" fill="none" stroke="#34D399" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>` : ""}
    ${hrDots}
    <line x1="${left}" y1="${top + chartH}" x2="${w - right}" y2="${top + chartH}" stroke="rgba(255,255,255,0.12)"/>
    <text x="${left}" y="${h - 10}" fill="rgba(255,255,255,0.34)" font-size="9" font-weight="700">${startLabel}</text>
    <text x="${w - right - 34}" y="${h - 10}" fill="rgba(255,255,255,0.34)" font-size="9" font-weight="700">${endLabel}</text>
    <circle cx="${w - right - 88}" cy="15" r="4" fill="#34D399"/>
    <text x="${w - right - 78}" y="18" fill="rgba(255,255,255,0.52)" font-size="9" font-weight="700">${hrRange}</text>
  </svg>`;
}

const timeTrials = runs
  .map(p => ({p, sec:fiveKSeconds(p)}))
  .filter(r => r.sec)
  .sort((a, b) => a.sec - b.sec);
const bestTrial = timeTrials[0] || null;
const runs7 = runs.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 7);
const cardio7 = cardio.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 7);
const runKm7 = runs7.reduce((sum, p) => sum + num(p.run_distance_km), 0);
const sportKm7 = cardio7.reduce((sum, p) => sum + sportKm(p), 0);
const totalKm2026 = yearRuns.reduce((sum, p) => sum + num(p.run_distance_km), 0);
const sportKm2026 = yearCardio.reduce((sum, p) => sum + sportKm(p), 0);
const totalMin2026 = Math.round(yearRuns.reduce((sum, p) => sum + runMinutes(p), 0));
const z2 = yearRuns.reduce((sum, p) => sum + num(p.run_zone2_time_min), 0);
const avg7 = avgSeconds(runs.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 7));
const avg28 = avgSeconds(runs.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 28));
const avgAll = avgSeconds(runs);
const sportRows = yearCardio
  .map(p => ({p, km:sportKm(p)}))
  .filter(row => row.km > 0)
  .sort((a, b) => dateKey(b.p.date).localeCompare(dateKey(a.p.date)));

const top = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:8px 0 18px;"}});
card(top, "7d KM", (runKm7 + sportKm7).toFixed(1) + "km", `${runKm7.toFixed(1)} run + ${sportKm7.toFixed(1)} sport est`, "#FF3B30");
card(top, `${currentYear} KM`, (totalKm2026 + sportKm2026).toFixed(1) + "km", `${totalKm2026.toFixed(1)} run + ${sportKm2026.toFixed(1)} sport est`, "#FF2D55");
card(top, `${currentYear} Time`, totalMin2026 + " min", `Zone 2 ${z2} min`, "#FF9500");
card(top, "Best 5K", bestTrial ? pace(bestTrial.sec) : "-", bestTrial ? dateKey(bestTrial.p.date) : "No time trial yet", "#5AC8FA");

runningChart(wrap, runs, cardio);

wrap.createEl("h2", {text:"Average 5K"});
const avgGrid = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:8px 0 20px;"}});
card(avgGrid, "7d", avg7 ? pace(avg7) : "-", "time trials", "#FF3B30");
card(avgGrid, "28d", avg28 ? pace(avg28) : "-", "time trials", "#FF9500");
card(avgGrid, "All", avgAll ? pace(avgAll) : "-", timeTrials.length + " trials", "#5AC8FA");

renderRows(
  "5K Time Trials",
  timeTrials,
  "No 5K time trials logged yet."
);

renderSportRows(
  "Sport Distance Estimates",
  sportRows,
  `No cardio sport sessions logged in ${currentYear} yet.`
);

wrap.createEl("h2", {text:"Run Log"});
const log = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;"}});
for (const p of yearRuns.slice().reverse()) {
  const row = log.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:10px 12px;"}});
  const left = row.createEl("div", {attr:{style:"min-width:0;"}});
  left.createEl("div", {text:p.run_type || "Run", attr:{style:"font-size:13px;font-weight:740;color:#fff;"}});
  left.createEl("div", {text:[p.run_distance_km ? p.run_distance_km + "km" : "", runTimeLabel(p), runPace(p)].filter(Boolean).join(" - "), attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  const right = row.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});
  right.createEl("div", {text:dateKey(p.date), attr:{style:"font-size:12px;color:rgba(255,255,255,0.42);"}});
}
```
