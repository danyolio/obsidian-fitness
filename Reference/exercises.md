# Exercise

```dataviewjs
try {
const wrap = dv.container;
const cfg = dv.page("System/settings") || dv.page("System/settings.md") || dv.page('"System/settings"') || {};
const workoutPages = dv.pages('"Workouts"')
  .where(p => p.workout_type === "Calisthenics")
  .sort(p => p.date, "desc");
const workouts = typeof workoutPages.array === "function" ? workoutPages.array() : Array.from(workoutPages);

const movements = [
  {
    key:"pullup",
    setting:"rr_pullup",
    name:"Pull-up",
    group:"Pull",
    color:"#5AC8FA",
    steps:["Scapular Pull-up","Arch Hang","Negative Pull-up","Pull-up","L-sit Pull-up","Weighted Pull-up"]
  },
  {
    key:"row",
    setting:"rr_row",
    name:"Row",
    group:"Pull",
    color:"#AF52DE",
    steps:["Vertical Row","Incline Row","Horizontal Row","Wide Row","Tuck Front Lever Row","Advanced Tuck Front Lever Row"]
  },
  {
    key:"dip",
    setting:"rr_dip",
    name:"Dip",
    group:"Push",
    color:"#FF9500",
    steps:["Parallel Bar Support Hold","Negative Dip","Parallel Bar Dip","Ring RTO Dip","Weighted Dip"]
  },
  {
    key:"pushup",
    setting:"rr_pushup",
    name:"Push-up",
    group:"Push",
    color:"#5856D6",
    steps:["Wall Push-up","Incline Push-up","Standard Push-up","Diamond Push-up","Pseudo Planche Push-up","Ring Push-up","Weighted Push-up"]
  },
  {
    key:"squat",
    setting:"rr_squat",
    name:"Squat",
    group:"Legs",
    color:"#30D158",
    steps:["Assisted Squat","Bodyweight Squat","Split Squat","Bulgarian Split Squat","Beginner Shrimp Squat","Intermediate Shrimp Squat","Advanced Shrimp Squat","Partial ROM Pistol Squat","Pistol Squat","Weighted Pistol Squat"]
  },
  {
    key:"hinge",
    setting:"rr_hinge",
    name:"Hinge",
    group:"Legs",
    color:"#FFD60A",
    steps:["Beginner Harop Curl","Harop Curl","Advanced Harop Curl","Banded Nordic Curl","Nordic Curl"]
  }
];

function clean(value) {
  if (value === null || value === undefined) return "";
  return String(value).replace(/^["']|["']$/g, "").trim();
}

function selectedSetting(value) {
  const text = clean(value);
  return ["auto", "last logged", "null", "none"].includes(text.toLowerCase()) ? "" : text;
}

function dateKey(value) {
  return value?.toISODate?.() || clean(value);
}

function reps(p, key) {
  return [1, 2, 3].reduce((sum, set) => sum + (Number(p[`rr_${key}_s${set}_reps`]) || 0), 0);
}

function latestProgression(key) {
  const session = workouts.find(p => clean(p[`rr_${key}_progression`]));
  if (!session) return {value:"", date:""};
  return {value:clean(session[`rr_${key}_progression`]), date:dateKey(session.date)};
}

function isSame(a, b) {
  return clean(a).toLowerCase() === clean(b).toLowerCase();
}

function card(parent, style = "") {
  return parent.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:18px;min-width:0;${style}`}});
}

function badge(parent, text, color) {
  return parent.createEl("div", {text, attr:{style:`font-size:10px;font-weight:820;color:${color};background:${color}20;border:1px solid ${color}55;border-radius:999px;padding:5px 8px;text-transform:uppercase;letter-spacing:.35px;white-space:nowrap;flex-shrink:0;`}});
}

const rows = movements.map(m => {
  const latest = latestProgression(m.key);
  const selected = selectedSetting(cfg[m.setting]);
  const active = selected || latest.value;
  const total = workouts.reduce((sum, p) => sum + reps(p, m.key), 0);
  return {...m, selected, latest, active, total};
});

const most = rows.reduce((best, row) => row.total > best.total ? row : best, {total:0});
const selectedCount = rows.filter(row => row.selected).length;

const hero = card(wrap, "padding:22px 20px;margin:8px 0 20px;background:linear-gradient(158deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03));box-shadow:0 8px 34px rgba(0,0,0,0.42),inset 0 1px 0 rgba(255,255,255,0.12);");
hero.createEl("div", {text:"Movement Map", attr:{style:"font-size:24px;font-weight:850;color:#fff;line-height:1.05;"}});
hero.createEl("div", {text:"A cleaner map of current progressions and the movement ladders behind them.", attr:{style:"font-size:13px;color:rgba(255,255,255,0.50);line-height:1.45;margin-top:9px;max-width:34rem;"}});
const heroMeta = hero.createEl("div", {attr:{style:"display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;"}});
badge(heroMeta, selectedCount ? `${selectedCount}/${rows.length} configured` : `${rows.length} movements`, selectedCount ? "#30D158" : "#8E8E93");
badge(heroMeta, most.total ? `Most reps: ${most.name} ${most.total}` : "No reps yet", most.color || "#8E8E93");

const grid = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:14px;margin-bottom:18px;"}});
for (const row of rows) {
  const isMost = most.total > 0 && row.key === most.key;
  const hasActive = Boolean(row.active);
  const source = row.selected ? "Selected progression" : (row.latest.value ? "Last logged progression" : "Progression");
  const c = card(grid, `padding:18px 16px 16px;border-top:3px solid ${row.color};${isMost ? `box-shadow:0 0 0 1px ${row.color}55,0 12px 32px ${row.color}18;` : ""}`);

  const head = c.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:16px;"}});
  const title = head.createEl("div", {attr:{style:"min-width:0;"}});
  title.createEl("div", {text:row.group, attr:{style:`font-size:10px;font-weight:820;color:${row.color};text-transform:uppercase;letter-spacing:.8px;margin-bottom:5px;`}});
  title.createEl("div", {text:row.name, attr:{style:"font-size:21px;font-weight:850;color:#fff;line-height:1.08;"}});
  badge(head, isMost ? "Most reps" : (row.selected ? "Selected" : (row.latest.value ? "Logged" : "Reference")), row.color);

  const current = c.createEl("div", {attr:{style:`background:${hasActive ? row.color + "18" : "rgba(255,255,255,0.035)"};border:1px solid ${hasActive ? row.color + "66" : "rgba(255,255,255,0.075)"};border-radius:14px;padding:13px 14px;margin-bottom:12px;`}})
  current.createEl("div", {text:source, attr:{style:"font-size:10px;font-weight:820;letter-spacing:.75px;text-transform:uppercase;color:rgba(255,255,255,0.42);"}});
  current.createEl("div", {text:row.active || "Not set", attr:{style:`font-size:18px;font-weight:850;color:${hasActive ? row.color : "rgba(255,255,255,0.52)"};line-height:1.22;margin-top:6px;white-space:normal;overflow-wrap:anywhere;`}});
  const meta = [];
  meta.push(row.total ? `${row.total} reps logged` : "No reps logged");
  if (row.latest.date) meta.push(`Last ${row.latest.date}`);
  c.createEl("div", {text:meta.join(" · "), attr:{style:"font-size:12px;color:rgba(255,255,255,0.46);line-height:1.4;margin-bottom:14px;"}});

  const ladder = c.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:7px;"}});
  row.steps.forEach((step, index) => {
    const active = row.active && isSame(step, row.active);
    const item = ladder.createEl("div", {
      attr:{style:`display:grid;grid-template-columns:24px minmax(0,1fr);gap:10px;align-items:center;background:${active ? row.color + "24" : "rgba(255,255,255,0.032)"};border:1px solid ${active ? row.color : "rgba(255,255,255,0.07)"};border-radius:13px;padding:9px 10px;`}
    });
    item.createEl("div", {text:String(index + 1), attr:{style:`width:24px;height:24px;border-radius:99px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:850;color:${active ? "#fff" : "rgba(255,255,255,0.44)"};background:${active ? row.color : "rgba(255,255,255,0.06)"};`}});
    item.createEl("div", {text:step, attr:{style:`font-size:13px;font-weight:${active ? "830" : "680"};line-height:1.25;color:${active ? "#fff" : "rgba(255,255,255,0.66)"};white-space:normal;overflow-wrap:anywhere;`}});
  });
}

const support = card(wrap, "padding:16px;margin-bottom:12px;border-left:3px solid #5AC8FA;");
support.createEl("div", {text:"Other modalities", attr:{style:"font-size:16px;font-weight:830;color:#fff;"}});
support.createEl("div", {text:"Running · lifting · Knees Over Toes · climbing · swimming · yoga · sauna · field and court sports", attr:{style:"font-size:12px;color:rgba(255,255,255,0.56);line-height:1.5;margin-top:7px;"}});

const settings = card(wrap, "padding:16px;border-left:3px solid #8E8E93;");
settings.createEl("div", {text:"Progression settings", attr:{style:"font-size:16px;font-weight:830;color:#fff;"}});
settings.createEl("div", {text:"New calisthenics workouts inherit rr_* values from System/settings.md. Public settings are intentionally blank.", attr:{style:"font-size:12px;color:rgba(255,255,255,0.52);line-height:1.45;margin-top:7px;"}});

} catch (err) {
  console.error("Exercise Reference render failed", err);
  const card = dv.container.createEl("div", {attr:{style:"background:rgba(255,255,255,0.055);border:1px solid rgba(255,255,255,0.12);border-left:3px solid #FF9500;border-radius:16px;padding:14px 16px;margin:8px 0 18px;"}});
  card.createEl("div", {text:"Exercises are warming up", attr:{style:"font-size:15px;font-weight:780;color:#fff;"}});
  card.createEl("div", {text:"Dataview did not finish rendering this pass. Reopen the note after Obsidian finishes syncing/indexing.", attr:{style:"font-size:12px;color:rgba(255,255,255,0.48);line-height:1.35;margin-top:5px;"}});
}
```
