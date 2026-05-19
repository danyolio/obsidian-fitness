---
cssclasses:
  - fitness-home
---

# Home

```dataviewjs
const wrap = dv.container;
try {
const currentFile = dv.current().file.path;
const now = new Date();
const todayKey = window.moment
  ? window.moment().format("YYYY-MM-DD")
  : new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);

const cfg = dv.page("System/settings") || dv.page("System/settings.md") || dv.page('"System/settings"');
const settingText = value => String(value || "").trim();
const displayName = settingText(cfg?.display_name) || "Athlete";
const hemisphere = settingText(cfg?.hemisphere).toLowerCase().startsWith("n") ? "Northern" : "Southern";
const defaultProgramStart = `${todayKey.slice(0, 4)}-${hemisphere === "Northern" ? "09" : "03"}-01`;
const blockNames = {1:"Endurance",2:"Strength",3:"Muscle",4:"Resilience"};
const targetsByBlock = {
  1: {cardio:3, strength:1, mobility:2},
  2: {cardio:2, strength:3, mobility:1},
  3: {cardio:3, strength:3, mobility:1},
  4: {cardio:2, strength:1, mobility:3}
};

const meta = {
  Run:{icon:"Run", color:"#FF3B30", group:"cardio", duration:null},
  Swim:{icon:"Swim", color:"#AF52DE", group:"cardio", duration:"swim_duration_min"},
  Cardio:{icon:"Cardio", color:"#FF2D55", group:"cardio", duration:"cardio_duration_min"},
  Lift:{icon:"Lift", color:"#FF9500", group:"strength", duration:null},
  Calisthenics:{icon:"Calis", color:"#5856D6", group:"strength", duration:"rr_duration_min"},
  Climb:{icon:"Climb", color:"#30D158", group:"strength", duration:"climb_duration_min"},
  KOT:{icon:"Knees", color:"#5AC8FA", group:"mobility", duration:"kot_duration_min"},
  Yoga:{icon:"Yoga", color:"#AF52DE", group:"mobility", duration:"yoga_duration_min"},
  Sauna:{icon:"Sauna", color:"#FFCC00", group:"mobility", duration:"sauna_duration_min"}
};

const normalizeType = wt => wt === "Knees Over Toes" ? "KOT" : wt;
const displayType = wt => normalizeType(wt) === "KOT" ? "Knees Over Toes" : normalizeType(wt);
const num = v => Number(v) || 0;
const dateKey = value => value?.toISODate?.() || String(value || "").slice(0, 10);
const dateObj = value => new Date(dateKey(value) + "T00:00:00");
const daysAgo = value => Math.floor((dateObj(todayKey) - dateObj(value)) / 86400000);
const toSeconds = value => {
  if (value === null || value === undefined || value === "") return null;
  const parts = String(value).trim().split(":").map(Number);
  if (parts.length === 1 && Number.isFinite(parts[0])) return parts[0] * 60;
  if (parts.length === 2 && parts.every(Number.isFinite)) return parts[0] * 60 + parts[1];
  if (parts.length === 3 && parts.every(Number.isFinite)) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return null;
};
const runSeconds = p => toSeconds(p.run_time) || (num(p.run_duration_min) ? num(p.run_duration_min) * 60 : null);
const runMinutes = p => runSeconds(p) ? runSeconds(p) / 60 : 0;
const runTimeLabel = p => p.run_time || (num(p.run_duration_min) ? p.run_duration_min + " min" : "");
const minutes = p => {
  const wt = normalizeType(p.workout_type);
  if (wt === "Run") return runMinutes(p);
  const field = meta[wt]?.duration;
  return field ? num(p[field]) : 0;
};
const calisParts = p => ({
  pull: ["pullup","row"].reduce((sum, key) => sum + num(p[`rr_${key}_s1_reps`]) + num(p[`rr_${key}_s2_reps`]) + num(p[`rr_${key}_s3_reps`]), 0),
  push: ["dip","pushup"].reduce((sum, key) => sum + num(p[`rr_${key}_s1_reps`]) + num(p[`rr_${key}_s2_reps`]) + num(p[`rr_${key}_s3_reps`]), 0),
  legs: ["squat","hinge"].reduce((sum, key) => sum + num(p[`rr_${key}_s1_reps`]) + num(p[`rr_${key}_s2_reps`]) + num(p[`rr_${key}_s3_reps`]), 0)
});
const sportKmRate = {soccer:0.09, basketball:0.07, tennis:0.06, cycling:0.28, hiit:0.08, rowing:0.16, elliptical:0.10, hiking:0.06, imported:0.05, other:0.05};

function sportKm(p) {
  if (normalizeType(p.workout_type) !== "Cardio") return 0;
  const activity = String(p.cardio_activity || "other").toLowerCase();
  return num(p.cardio_duration_min) * (sportKmRate[activity] || sportKmRate.other);
}

function blockInfo(value) {
  const start = dateObj(cfg?.program_start_date || defaultProgramStart);
  const days = Math.floor((dateObj(value) - start) / 86400000);
  const week = Math.max(1, Math.floor(days / 7) + 1);
  const derivedBlock = Math.min(4, Math.floor((week - 1) / 12) + 1);
  const configuredBlock = Number(cfg?.current_block);
  const block = configuredBlock >= 1 && configuredBlock <= 4 ? configuredBlock : derivedBlock;
  return {block, week};
}

function cardStyle(extra = "") {
  return "background:linear-gradient(158deg,rgba(255,255,255,0.068),rgba(255,255,255,0.028));border:1px solid rgba(255,255,255,0.12);border-radius:18px;box-shadow:0 8px 34px rgba(0,0,0,0.42),inset 0 1px 0 rgba(255,255,255,0.12);" + extra;
}

function loadBand(hours, baseline) {
  const base = Math.max(baseline || 0, 1);
  if (hours < base * 0.85) return {label:"Low", color:"#30D158"};
  if (hours <= base * 1.2) return {label:"Medium", color:"#FFCC00"};
  return {label:"High", color:"#FF9500"};
}

async function createWorkout() {
  const tp = app.plugins.plugins["templater-obsidian"];
  const tf = app.vault.getAbstractFileByPath("System/workout-template.md");
  const folder = app.vault.getAbstractFileByPath("Workouts");
  if (!tp || !tf || !folder) return;

  const dateStr = window.moment().format("YYYY-MM-DD");
  let fileName = dateStr;
  let suffix = 1;
  while (app.vault.getAbstractFileByPath(`Workouts/${fileName}.md`)) {
    suffix++;
    fileName = `${dateStr}-${suffix}`;
  }

  const newFile = await tp.templater.create_new_note_from_template(tf, folder, fileName, false);
  if (newFile) await app.workspace.getLeaf(false).openFile(newFile);
}

const workouts = dv.pages('"Workouts"').where(p => p.date && p.workout_type).array();
const recent = workouts
  .slice()
  .sort((a, b) => dateKey(b.date).localeCompare(dateKey(a.date)));
const week = workouts.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 7);
const last3 = workouts.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 3);
const last28 = workouts.filter(p => daysAgo(p.date) >= 0 && daysAgo(p.date) < 28);
const {block, week: programWeek} = blockInfo(todayKey);
const targets = targetsByBlock[block] || targetsByBlock[1];

const days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const hr = now.getHours();
const greet = hr < 5 ? `Still up, ${displayName}?` : hr < 12 ? `Good morning, ${displayName}` : hr < 17 ? `Good afternoon, ${displayName}` : `Good evening, ${displayName}`;

const header = wrap.createEl("div", {attr:{style:"padding:0 0 14px;"}});
header.createEl("div", {text:`${days[now.getDay()]} ${now.getDate()} ${months[now.getMonth()]}`, attr:{style:"font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.36);margin-bottom:6px;"}});
header.createEl("div", {text:greet, attr:{style:"font-size:28px;font-weight:760;color:#fff;line-height:1.08;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
header.createEl("div", {text:`Block ${block} - ${settingText(cfg?.block_name) || blockNames[block]} - Week ${programWeek}`, attr:{style:"font-size:13px;color:rgba(255,255,255,0.42);margin-top:6px;"}});

const counts = {cardio:0, strength:0, mobility:0};
for (const p of week) {
  const group = meta[normalizeType(p.workout_type)]?.group;
  if (group) counts[group]++;
}

wrap.createEl("div", {text:"This Week", attr:{style:"font-size:12px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);margin:16px 0 8px 4px;"}});

const rings = wrap.createEl("div", {attr:{style:cardStyle("padding:30px 22px;display:flex;flex-direction:column;align-items:center;position:relative;")}});
const uid = "rg" + Date.now();
function arc(cx, cy, r, pct, color) {
  const circ = 2 * Math.PI * r;
  const filled = Math.min(Math.max(pct, 0), 1) * circ;
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}" stroke-opacity="0.14" stroke-width="13"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}" stroke-width="13" stroke-linecap="round" stroke-dasharray="${filled.toFixed(2)} ${(circ - filled).toFixed(2)}" transform="rotate(-90 ${cx} ${cy})" filter="url(#${uid})"/>`;
}
rings.createEl("div").innerHTML = `<svg width="180" height="180" viewBox="0 0 160 160" style="flex-shrink:0;"><defs><filter id="${uid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur in="SourceGraphic" stdDeviation="2.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>${arc(80,80,62,counts.cardio/targets.cardio,"#FF3B30")}${arc(80,80,45,counts.strength/targets.strength,"#FF9500")}${arc(80,80,28,counts.mobility/targets.mobility,"#30D158")}</svg>`;
const ringText = rings.createEl("div", {attr:{style:"margin-top:18px;display:flex;gap:14px;flex-wrap:wrap;justify-content:center;font-size:12px;font-weight:650;"}});
for (const item of [
  ["Cardio", counts.cardio, targets.cardio, "#FF3B30"],
  ["Strength", counts.strength, targets.strength, "#FF9500"],
  ["Mobility", counts.mobility, targets.mobility, "#30D158"]
]) {
  ringText.createEl("span", {text:`${item[1]}/${item[2]} ${item[0]}`, attr:{style:`color:${item[3]};white-space:nowrap;`}});
}

function hasType(list, type) {
  return list.some(p => normalizeType(p.workout_type) === type);
}

function isHard(p) {
  const wt = normalizeType(p.workout_type);
  const rt = String(p.run_type || "").toLowerCase();
  return wt === "Lift" || wt === "Climb" || wt === "Cardio" || rt.includes("interval") || rt.includes("tempo") || rt.includes("race");
}

function lastSeen(type) {
  const found = recent.find(p => normalizeType(p.workout_type) === type);
  return found ? daysAgo(found.date) : 99;
}

const choices = [
  {type:"Run", badge:"Run", title:"Zone 2 Run", desc:"Easy aerobic minutes. Keep it conversational.", color:"#FF3B30", group:"cardio", block:[4,1,4,2]},
  {type:"KOT", badge:"Recovery", icon:"🌿", title:"Recovery Mobility", desc:"Knees, calves, hips. Keep it easy and restorative.", color:"#5AC8FA", group:"mobility", block:[3,1,2,3]},
  {type:"Calisthenics", badge:"Calis", title:"Calisthenics Progression", desc:"Build the push/pull base and log clean reps.", color:"#5856D6", group:"strength", block:[1,2,5,2]},
  {type:"Lift", badge:"Lift", title:"5/3/1 Lift", desc:"Heavy strength only if the last couple of days were not loaded.", color:"#FF9500", group:"strength", block:[1,4,2,1]},
  {type:"Climb", badge:"Climb", title:"Climb Session", desc:"Skill, tension, and grip. Avoid stacking it near heavy pulls.", color:"#30D158", group:"strength", block:[2,5,2,1]},
  {type:"Swim", badge:"Swim", title:"Swim", desc:"Low-impact cardio with joint-friendly volume.", color:"#AF52DE", group:"cardio", block:[1,1,1,5]},
  {type:"Yoga", badge:"Yoga", title:"Yoga Downshift", desc:"Mobility and nervous system reset.", color:"#AF52DE", group:"mobility", block:[2,2,3,5]}
];

const hardRecent = last3.some(isHard);
const ranRecently = hasType(last3, "Run");
let rec = choices.map(c => {
  let score = c.block[block - 1] || 1;
  const gap = Math.max(0, (targets[c.group] || 0) - (counts[c.group] || 0));
  score += gap * 2.4;
  score += Math.min(lastSeen(c.type), 7) * 0.35;
  if (recent[0] && normalizeType(recent[0].workout_type) === c.type) score -= 2.5;
  if (hardRecent && ["Lift","Climb"].includes(c.type)) score -= 2.5;
  if (hardRecent && c.type === "Yoga") score += 2.8;
  if (ranRecently && !hasType(week, "KOT") && c.type === "KOT") score += 4;
  if (!hasType(week, "Yoga") && c.type === "Yoga") score += 1.5;
  if (c.type === "Run" && ranRecently) score -= 1.6;
  return {...c, score};
}).sort((a, b) => b.score - a.score)[0];

wrap.createEl("div", {text:"Today's Move", attr:{style:"font-size:12px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);margin:28px 0 10px 4px;"}});
const moveCard = wrap.createEl("div", {attr:{style:cardStyle(`border-top:2px solid ${rec.color};padding:18px;display:flex;align-items:center;gap:14px;cursor:pointer;margin-bottom:16px;`)}});
moveCard.createEl("div", {text:rec.icon || rec.badge || rec.type, attr:{style:`width:48px;height:48px;border-radius:16px;background:${rec.color}22;border:1px solid ${rec.color}55;color:${rec.color};display:flex;align-items:center;justify-content:center;font-size:${rec.icon ? "23px" : "11px"};font-weight:850;flex-shrink:0;`}});
const moveText = moveCard.createEl("div", {attr:{style:"flex:1;min-width:0;"}});
moveText.createEl("div", {text:rec.title, attr:{style:"font-size:17px;font-weight:760;color:#fff;line-height:1.15;"}});
moveText.createEl("div", {text:rec.desc, attr:{style:"font-size:12px;color:rgba(255,255,255,0.46);line-height:1.35;margin-top:4px;"}});
moveCard.addEventListener("click", async e => {
  e.preventDefault();
  e.stopPropagation();
  if (moveCard.dataset.locked) return;
  moveCard.dataset.locked = "true";
  try { await createWorkout(); } catch (err) { console.error(err); }
  setTimeout(() => moveCard.dataset.locked = "", 1600);
});

const add = wrap.createEl("div", {attr:{style:"background:#FF3B30;border-radius:17px;padding:15px 18px;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 8px 24px rgba(255,59,48,.24),inset 0 1px 0 rgba(255,255,255,.2);cursor:pointer;margin-bottom:34px;"}});
add.createEl("span", {text:"+", attr:{style:"font-size:22px;font-weight:600;color:#fff;line-height:.8;"}});
add.createEl("span", {text:"Add Workout", attr:{style:"font-size:16px;font-weight:720;color:#fff;"}});
add.addEventListener("click", async e => {
  e.preventDefault();
  e.stopPropagation();
  if (add.dataset.locked) return;
  add.dataset.locked = "true";
  try { await createWorkout(); } catch (err) { console.error(err); }
  setTimeout(() => add.dataset.locked = "", 1600);
});

const weekHours = week.reduce((sum, p) => sum + minutes(p), 0) / 60;
const monthHours = last28.reduce((sum, p) => sum + minutes(p), 0) / 60;
const loadBaseline = monthHours / 4;
const load = loadBand(weekHours, loadBaseline);
const loadRatio = weekHours / Math.max(loadBaseline || 0, 1);
const runs7 = week.filter(p => normalizeType(p.workout_type) === "Run");
const runKm7 = runs7.reduce((sum, p) => sum + num(p.run_distance_km), 0);
const sportKm7 = week.reduce((sum, p) => sum + sportKm(p), 0);
const weeklyKm = runKm7 + sportKm7;
const calisThisWeek = week.filter(p => normalizeType(p.workout_type) === "Calisthenics").reduce((sum, p) => {
  const parts = calisParts(p);
  return {push:sum.push + parts.push, pull:sum.pull + parts.pull, legs:sum.legs + parts.legs};
}, {push:0, pull:0, legs:0});
const calisTotal = calisThisWeek.push + calisThisWeek.pull + calisThisWeek.legs;
const hardCount = week.filter(isHard).length;
const recoveryRows = week.filter(p => ["KOT","Yoga","Sauna"].includes(normalizeType(p.workout_type)));
const yogaCount = week.filter(p => normalizeType(p.workout_type) === "Yoga").length;
const recoveryDebt = Math.max(0, hardCount - recoveryRows.length);
const recoveryValue = hardCount === 0 ? "Fresh" : recoveryDebt === 0 ? "Balanced" : "Recovery due";
const recoverySub = yogaCount
  ? `${hardCount} hard · ${recoveryRows.length} recovery this week`
  : `${hardCount} hard · ${recoveryRows.length} recovery · yoga due`;
const recoveryColor = recoveryDebt > 0 ? "#FF9500" : yogaCount ? "#30D158" : "#AF52DE";

wrap.createEl("div", {text:"This Week", attr:{style:"font-size:12px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);margin:18px 0 10px 4px;"}});
const snapshots = [
  {label:"Training Load", value:load.label, detail:`${loadRatio.toFixed(1)}x avg`, sub:`${week.length} sessions · ${weekHours.toFixed(1)}h · ${hardCount} hard`, path:"Progress/load", color:load.color},
  {label:"Running distance", value:weeklyKm.toFixed(1) + " km", detail:"this week", sub:`${runKm7.toFixed(1)} run · ${sportKm7.toFixed(1)} sport est`, path:"Progress/running", color:"#FF3B30"},
  {label:"Calisthenics reps", value:calisTotal + " reps", detail:"this week", sub:`Push ${calisThisWeek.push} · Pull ${calisThisWeek.pull} · Legs ${calisThisWeek.legs}`, path:"Progress/calisthenics", color:"#5856D6"},
  {label:"Recovery", value:recoveryValue, detail:"this week", sub:recoverySub, path:"Progress/load", color:recoveryColor}
];
const grid = wrap.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:8px;margin-bottom:24px;"}});
for (const item of snapshots) {
  const el = grid.createEl("div", {attr:{style:cardStyle(`border-left:3px solid ${item.color};padding:12px 14px;cursor:pointer;min-width:0;box-shadow:none;display:flex;align-items:center;justify-content:space-between;gap:12px;`)}});
  const left = el.createEl("div", {attr:{style:"min-width:0;"}});
  left.createEl("div", {text:item.label, attr:{style:"font-size:13px;font-weight:760;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  left.createEl("div", {text:item.sub, attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"}});
  const right = el.createEl("div", {attr:{style:"text-align:right;flex-shrink:0;min-width:74px;"}});
  right.createEl("div", {text:item.value, attr:{style:`font-size:15px;font-weight:820;color:${item.color};white-space:nowrap;`}});
  right.createEl("div", {text:item.detail, attr:{style:"font-size:10px;font-weight:760;color:rgba(255,255,255,0.36);margin-top:2px;white-space:nowrap;"}});
  el.addEventListener("click", () => app.workspace.openLinkText(item.path, currentFile));
}

wrap.createEl("div", {text:"Recent", attr:{style:"font-size:12px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:rgba(255,255,255,0.38);margin:10px 0 8px 4px;"}});
function getStat(p) {
  const wt = normalizeType(p.workout_type);
  if (wt === "Run") return [p.run_distance_km ? p.run_distance_km + " km" : "", runTimeLabel(p), p.run_avg_hr ? p.run_avg_hr + " bpm" : ""].filter(Boolean).join(" - ") || "-";
  if (wt === "Lift" && p.lift_top_set_prescribed_weight > 0) return `${p.lift_exercise || "Lift"} ${p.lift_top_set_prescribed_weight}kg x ${p.lift_top_set_actual_reps || "?"}`;
  if (wt === "Climb") return [p.climb_max_grade || "", p.climb_problems_sent ? `${p.climb_problems_sent}/${p.climb_problems_attempted || "?"} sent` : "", p.climb_duration_min ? p.climb_duration_min + " min" : ""].filter(Boolean).join(" - ") || "-";
  if (wt === "Swim" && p.swim_distance_m > 0) return `${p.swim_distance_m}m ${p.swim_1km_time || ""}`.trim();
  if (wt === "Cardio" && p.cardio_duration_min > 0) return [p.cardio_activity || "Cardio", p.cardio_duration_min + " min", p.cardio_avg_hr ? p.cardio_avg_hr + " bpm" : ""].filter(Boolean).join(" - ");
  const field = meta[wt]?.duration;
  return field && p[field] > 0 ? p[field] + " min" : "-";
}

const list = wrap.createEl("div", {attr:{style:cardStyle("overflow:hidden;box-shadow:none;")}});
for (const [i, p] of recent.slice(0, 5).entries()) {
  const wt = normalizeType(p.workout_type);
  const c = meta[wt]?.color || "#fff";
  const d = dateObj(p.date);
  const ds = d.toLocaleDateString("en-GB", {weekday:"short", day:"numeric", month:"short"});
  const row = list.createEl("div", {attr:{style:`display:flex;align-items:center;gap:13px;padding:14px 16px;cursor:pointer;${i === Math.min(recent.length, 5) - 1 ? "" : "border-bottom:1px solid rgba(255,255,255,0.06);"}`}});
  row.createEl("div", {attr:{style:`width:8px;height:8px;border-radius:50%;background:${c};box-shadow:0 0 8px ${c}88;flex-shrink:0;`}});
  const info = row.createEl("div", {attr:{style:"flex:1;min-width:0;"}});
  info.createEl("div", {text:displayType(wt), attr:{style:"font-size:14px;font-weight:700;color:#fff;"}});
  info.createEl("div", {text:getStat(p), attr:{style:"font-size:12px;color:rgba(255,255,255,0.4);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px;"}});
  row.createEl("div", {text:ds, attr:{style:"font-size:12px;color:rgba(255,255,255,0.38);flex-shrink:0;"}});
  row.addEventListener("click", () => app.workspace.openLinkText(p.file.path, currentFile));
}
if (!recent.length) list.createEl("div", {text:"No workouts logged yet.", attr:{style:"font-size:13px;color:rgba(255,255,255,0.45);padding:14px 16px;"}});

const history = wrap.createEl("div", {text:"History", attr:{style:"margin-top:12px;text-align:center;font-size:13px;font-weight:700;color:#FF3B30;cursor:pointer;padding:9px;"}});
history.addEventListener("click", () => app.workspace.openLinkText("Progress/history", currentFile));

const tools = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:32px 0 24px;"}});
for (const item of [
  ["Settings", "System/settings"],
  ["Programs", "Reference/programs"]
]) {
  const btn = tools.createEl("div", {text:item[0], attr:{style:"background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:13px;text-align:center;font-size:13px;font-weight:700;color:rgba(255,255,255,0.78);cursor:pointer;"}});
  btn.addEventListener("click", () => app.workspace.openLinkText(item[1], currentFile));
}
} catch (err) {
  console.error("Fitness Home render failed", err);
  const card = wrap.createEl("div", {attr:{style:"background:rgba(255,255,255,0.055);border:1px solid rgba(255,255,255,0.12);border-left:3px solid #FF9500;border-radius:16px;padding:14px 16px;margin:8px 0 18px;"}});
  card.createEl("div", {text:"Home is warming up", attr:{style:"font-size:15px;font-weight:780;color:#fff;"}});
  card.createEl("div", {text:"Dataview did not finish rendering this pass. Reopen the note after Obsidian finishes syncing/indexing.", attr:{style:"font-size:12px;color:rgba(255,255,255,0.48);line-height:1.35;margin-top:5px;"}});
}
```
