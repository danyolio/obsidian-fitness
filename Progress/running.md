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
    return {start, key:isoDate(start), runKm:0, sportKm:0, minutes:0};
  });
  const byWeek = new Map(weeks.map(week => [week.key, week]));

  for (const p of runSource) {
    const week = byWeek.get(isoDate(weekStart(p.date)));
    if (!week) continue;
    week.runKm += num(p.run_distance_km);
    week.minutes += runMinutes(p);
  }

  for (const p of sportSource) {
    const week = byWeek.get(isoDate(weekStart(p.date)));
    if (!week) continue;
    week.sportKm += sportKm(p);
    week.minutes += num(p.cardio_duration_min);
  }

  const rows = weeks.map(week => ({
    ...week,
    totalKm: week.runKm + week.sportKm
  }));
  const thisWeek = rows[rows.length - 1];
  const avgWeeklyKm = avg(rows.map(row => row.totalKm)) || 0;
  const maxObservedKm = Math.max(...rows.map(row => row.totalKm), avgWeeklyKm);
  const axisMax = (() => {
    const padded = Math.max(5, maxObservedKm) * 1.12;
    if (padded <= 10) return 10;
    if (padded <= 30) return Math.ceil(padded / 5) * 5;
    return Math.ceil(padded / 10) * 10;
  })();
  const w = 340, h = 214, left = 36, right = 24, top = 28, bottom = 34;
  const chartW = w - left - right;
  const chartH = h - top - bottom;
  const step = chartW / rows.length;
  const barW = Math.max(8, step * 0.58);
  const xMid = i => left + step * i + step / 2;
  const yKm = value => top + chartH - (value / axisMax) * chartH;
  const grid = [1, 0.5, 0].map(t => {
    const y = top + chartH - t * chartH;
    const label = Math.round(axisMax * t);
    return `<line x1="${left}" y1="${y.toFixed(1)}" x2="${w - right}" y2="${y.toFixed(1)}" stroke="rgba(255,255,255,0.07)"/>
      <text x="4" y="${(y + 3).toFixed(1)}" fill="rgba(255,255,255,0.34)" font-size="9" font-weight="700">${label}km</text>`;
  }).join("");
  const bars = rows.map((row, i) => {
    if (!row.totalKm) return "";
    const x = xMid(i) - barW / 2;
    const y = yKm(row.totalKm);
    const height = Math.max(2, top + chartH - y);
    const fill = row.totalKm >= axisMax * 0.65 ? "#FF3B30" : row.totalKm >= axisMax * 0.35 ? "#FF9500" : "#5AC8FA";
    return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${height.toFixed(1)}" rx="4" fill="${fill}" opacity="0.9"/>`;
  }).join("");
  const avgY = yKm(avgWeeklyKm);
  const avgLine = avgWeeklyKm > 0
    ? `<line x1="${left}" y1="${avgY.toFixed(1)}" x2="${w - right}" y2="${avgY.toFixed(1)}" stroke="#34D399" stroke-width="1.5" stroke-dasharray="4 5" opacity="0.72"/>
      <text x="${w - right - 45}" y="${(avgY - 5).toFixed(1)}" fill="rgba(52,211,153,0.78)" font-size="9" font-weight="760">12w avg</text>`
    : "";
  const startLabel = weekLabel(rows[0].start);
  const endLabel = weekLabel(rows[rows.length - 1].start);

  const box = parent.createEl("div", {attr:{style:"background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:18px;padding:13px 13px 11px;margin:2px 0 22px;"}});
  const head = box.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin:0 2px 8px;"}});
  const leftHead = head.createEl("div", {attr:{style:"min-width:0;"}});
  leftHead.createEl("div", {text:"12 Week Mileage Trend", attr:{style:"font-size:14px;font-weight:820;color:#fff;"}});
  leftHead.createEl("div", {text:"weekly km + 12w average", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:3px;"}});
  const rightHead = head.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});
  rightHead.createEl("div", {text:avgWeeklyKm.toFixed(1) + "km/wk", attr:{style:"font-size:18px;font-weight:850;color:#FF3B30;line-height:1;"}});
  rightHead.createEl("div", {text:thisWeek.totalKm.toFixed(1) + "km this week", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:5px;"}});
  const svg = box.createEl("div");
  svg.innerHTML = `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;display:block;">
    <rect x="0" y="0" width="${w}" height="${h}" rx="15" fill="rgba(255,255,255,0.018)"/>
    ${grid}
    ${bars}
    ${avgLine}
    <line x1="${left}" y1="${top + chartH}" x2="${w - right}" y2="${top + chartH}" stroke="rgba(255,255,255,0.12)"/>
    <text x="${left}" y="${h - 10}" fill="rgba(255,255,255,0.34)" font-size="9" font-weight="700">${startLabel}</text>
    <text x="${w - right - 34}" y="${h - 10}" fill="rgba(255,255,255,0.34)" font-size="9" font-weight="700">${endLabel}</text>
  </svg>`;
}

function zone2Share(p) {
  const minutes = runMinutes(p);
  const zone2 = num(p.run_zone2_time_min);
  return minutes > 0 ? zone2 / minutes : 0;
}

function isZone2BenchmarkRun(p) {
  const type = String(p.run_type || "").toLowerCase();
  const effort = num(p.run_perceived_effort);
  const hard = type.includes("tempo") || type.includes("interval") || type.includes("race") || effort >= 7;
  const zone2 = num(p.run_zone2_time_min);
  return !hard && zone2 >= 30;
}

function benchmarkHr(p) {
  const hr = num(p.run_avg_hr);
  return hr >= 60 && hr <= 220 ? hr : null;
}

function monthLabel(key) {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return months[num(key.slice(5, 7)) - 1] || key;
}

function hrBenchmarkChart(parent, source) {
  const groups = new Map();
  for (const p of source) {
    if (!benchmarkHr(p) || !isZone2BenchmarkRun(p)) continue;
    const key = dateKey(p.date).slice(0, 7);
    const rows = groups.get(key) || [];
    rows.push({
      p,
      date:dateKey(p.date),
      distance:num(p.run_distance_km),
      minutes:runMinutes(p),
      zone2:num(p.run_zone2_time_min),
      zone2Pct:zone2Share(p),
      hr:benchmarkHr(p)
    });
    groups.set(key, rows);
  }

  const rows = Array.from(groups.entries())
    .map(([month, runs]) => {
      const avgHr = runs.reduce((sum, row) => sum + row.hr, 0) / runs.length;
      const avgDistance = runs.reduce((sum, row) => sum + row.distance, 0) / runs.length;
      const avgMinutes = runs.reduce((sum, row) => sum + row.minutes, 0) / runs.length;
      const avgZone2 = runs.reduce((sum, row) => sum + row.zone2, 0) / runs.length;
      return {month, runs, avgHr, avgDistance, avgMinutes, avgZone2};
    })
    .sort((a, b) => a.month.localeCompare(b.month))
    .slice(-6);

  const box = parent.createEl("div", {attr:{style:"background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:18px;padding:13px 13px 11px;margin:2px 0 22px;"}});
  const head = box.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin:0 2px 8px;"}});
  const leftHead = head.createEl("div", {attr:{style:"min-width:0;"}});
  leftHead.createEl("div", {text:"Zone 2 HR by Month", attr:{style:"font-size:14px;font-weight:820;color:#fff;"}});
  leftHead.createEl("div", {text:"non-hard runs with 30+ min Z2", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:3px;"}});
  const rightHead = head.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;"}});

  if (!rows.length) {
    rightHead.createEl("div", {text:"-", attr:{style:"font-size:18px;font-weight:850;color:#34D399;line-height:1;"}});
    rightHead.createEl("div", {text:"no benchmark yet", attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:5px;"}});
    box.createEl("div", {text:"Log a non-hard run with average HR and 30+ minutes in Zone 2 to start this benchmark.", attr:{style:"background:rgba(255,255,255,0.025);border-radius:15px;padding:18px 16px;font-size:12px;line-height:1.4;color:rgba(255,255,255,0.46);"}});
    return;
  }

  const latest = rows[rows.length - 1];
  const previous = rows.length > 1 ? rows[rows.length - 2] : null;
  const delta = previous ? latest.avgHr - previous.avgHr : 0;
  const deltaText = rows.length > 1
    ? `${Math.abs(Math.round(delta))} bpm ${delta < -0.5 ? "lower" : delta > 0.5 ? "higher" : "steady"} vs ${monthLabel(previous.month)}`
    : "need another month";
  const trendColor = rows.length < 2 ? "#34D399" : delta < -0.5 ? "#30D158" : delta > 0.5 ? "#FF9500" : "#5AC8FA";

  rightHead.createEl("div", {text:Math.round(latest.avgHr) + " bpm", attr:{style:`font-size:18px;font-weight:850;color:${trendColor};line-height:1;`}});
  rightHead.createEl("div", {text:deltaText, attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:5px;"}});

  const minHr = Math.min(120, Math.floor((Math.min(...rows.map(row => row.avgHr)) - 5) / 5) * 5);
  const maxHr = Math.max(170, Math.ceil((Math.max(...rows.map(row => row.avgHr)) + 5) / 5) * 5);
  const span = Math.max(1, maxHr - minHr);
  const list = box.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;margin-top:10px;"}});
  for (const row of rows) {
    const marker = Math.max(0, Math.min(100, ((row.avgHr - minHr) / span) * 100));
    const active = row === latest;
    const item = list.createEl("div", {attr:{style:`background:rgba(255,255,255,0.025);border:1px solid ${active ? "rgba(52,211,153,0.32)" : "rgba(255,255,255,0.06)"};border-radius:14px;padding:10px 11px;`}});
    const topRow = item.createEl("div", {attr:{style:"display:flex;align-items:baseline;justify-content:space-between;gap:10px;"}});
    topRow.createEl("div", {text:monthLabel(row.month), attr:{style:"font-size:13px;font-weight:820;color:#fff;"}});
    topRow.createEl("div", {text:Math.round(row.avgHr) + " bpm", attr:{style:`font-size:14px;font-weight:820;color:${active ? trendColor : "rgba(255,255,255,0.82)"};white-space:nowrap;`}});
    item.createEl("div", {text:`${row.runs.length} run${row.runs.length === 1 ? "" : "s"} - ${Math.round(row.avgZone2)} min Z2 avg - ${row.avgDistance.toFixed(1)}km avg`, attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
    const bar = item.createEl("div", {attr:{style:"height:5px;background:rgba(255,255,255,0.07);border-radius:999px;margin-top:8px;position:relative;"}});
    bar.createEl("div", {attr:{style:`position:absolute;left:${marker.toFixed(0)}%;top:50%;width:9px;height:9px;margin:-4.5px 0 0 -4.5px;background:${active ? trendColor : "#34D399"};border-radius:999px;box-shadow:0 0 0 3px rgba(52,211,153,0.12);`}});
  }

  box.createEl("div", {text:`Latest month: ${monthLabel(latest.month)} - ${latest.runs.length} run${latest.runs.length === 1 ? "" : "s"} - ${Math.round(latest.avgMinutes)} min avg`, attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin:9px 2px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
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
hrBenchmarkChart(wrap, runs);

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
