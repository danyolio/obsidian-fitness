# Blocks

```dataviewjs
try {
const wrap = dv.container;
const cfg = dv.page("System/settings") || dv.page("System/settings.md") || dv.page('"System/settings"') || {};
const blockNames = {1:"Endurance",2:"Strength",3:"Muscle",4:"Resilience"};
const clean = value => String(value || "").trim();
const hemisphere = clean(cfg.hemisphere).toLowerCase().startsWith("n") ? "Northern" : "Southern";
const defaultProgramStart = `${new Date().getFullYear()}-${hemisphere === "Northern" ? "09" : "03"}-01`;
const seasons = hemisphere === "Northern"
  ? {
      1:{season:"Autumn", months:"Sep-Nov"},
      2:{season:"Winter", months:"Dec-Feb"},
      3:{season:"Spring", months:"Mar-May"},
      4:{season:"Summer", months:"Jun-Aug"}
    }
  : {
      1:{season:"Autumn", months:"Mar-May"},
      2:{season:"Winter", months:"Jun-Aug"},
      3:{season:"Spring", months:"Sep-Nov"},
      4:{season:"Summer", months:"Dec-Feb"}
    };

function cleanDate(value) {
  return value?.toISODate?.() || value || defaultProgramStart;
}

function currentProgramWeek() {
  const start = new Date(`${cleanDate(cfg.program_start_date)}T00:00:00`);
  const today = new Date();
  const days = Math.floor((today - start) / 86400000);
  return Math.max(1, Math.floor(days / 7) + 1);
}

const week = currentProgramWeek();
const derivedBlock = Math.min(4, Math.floor((week - 1) / 12) + 1);
const configuredBlock = Number(cfg.current_block);
const activeBlock = configuredBlock >= 1 && configuredBlock <= 4 ? configuredBlock : derivedBlock;
const activeSeason = seasons[activeBlock] || seasons[1];

const blocks = [
  {
    number:1,
    name:"Endurance",
    season:seasons[1].season,
    months:seasons[1].months,
    color:"#FF3B30",
    focus:"Build aerobic base, easy volume, and repeatable conditioning.",
    keep:"Calisthenics, Knees Over Toes, light climbing.",
    week:"3 runs, 1 calisthenics, 1 recovery, 1 climb",
    watch:"Keep easy work easy."
  },
  {
    number:2,
    name:"Strength",
    season:seasons[2].season,
    months:seasons[2].months,
    color:"#FF9500",
    focus:"Build maximal strength, heavier loading, and force production.",
    keep:"Easy running and joint care.",
    week:"2 lifts, 2 climbs, 1 easy run",
    watch:"Do not stack deadlifts, hard climbing, and hard runs."
  },
  {
    number:3,
    name:"Muscle",
    season:seasons[3].season,
    months:seasons[3].months,
    color:"#5856D6",
    focus:"Build muscle, clean reps, bodyweight volume, and control.",
    keep:"Running support, minimum effective lifting.",
    week:"2 calisthenics, 2 runs, 1 lift, 1 recovery",
    watch:"Progression jumps are new stress."
  },
  {
    number:4,
    name:"Resilience",
    season:seasons[4].season,
    months:seasons[4].months,
    color:"#5AC8FA",
    focus:"Build recovery capacity, mobility, tissue tolerance, and low-impact cardio.",
    keep:"Fun climbing and light strength.",
    week:"2 swims, 1 yoga, 1 sauna, 1 recovery, 1 climb",
    watch:"Reset deliberately. Do not chase fatigue."
  }
];

function card(parent, style = "") {
  return parent.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-radius:16px;min-width:0;${style}`}});
}

function row(parent, label, value) {
  const el = parent.createEl("div", {attr:{style:"display:grid;grid-template-columns:64px minmax(0,1fr);gap:10px;border-top:1px solid rgba(255,255,255,0.07);padding-top:11px;margin-top:11px;"}});
  el.createEl("div", {text:label, attr:{style:"font-size:11px;font-weight:820;color:rgba(255,255,255,0.36);text-transform:uppercase;letter-spacing:.5px;"}});
  el.createEl("div", {text:value, attr:{style:"font-size:13px;color:rgba(255,255,255,0.74);line-height:1.4;"}});
}

const hero = card(wrap, "padding:20px;margin:8px 0 18px;background:linear-gradient(158deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03));box-shadow:0 8px 34px rgba(0,0,0,0.42),inset 0 1px 0 rgba(255,255,255,0.12);");
hero.createEl("div", {text:"Seasonal Blocks", attr:{style:"font-size:26px;font-weight:850;color:#fff;line-height:1.05;"}});
hero.createEl("div", {text:"A seasonal priority map. The time of year sets the training emphasis, while everything else stays ticking over.", attr:{style:"font-size:14px;color:rgba(255,255,255,0.52);line-height:1.45;margin-top:9px;"}});
const chips = hero.createEl("div", {attr:{style:"display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;"}});
chips.createEl("div", {text:`Block ${activeBlock} - ${blockNames[activeBlock] || "Unknown"}`, attr:{style:"font-size:12px;font-weight:820;color:#fff;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);border-radius:10px;padding:7px 10px;"}});
chips.createEl("div", {text:`${activeSeason.season} · ${activeSeason.months}`, attr:{style:"font-size:12px;font-weight:820;color:rgba(255,255,255,0.74);background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.10);border-radius:10px;padding:7px 10px;"}});
chips.createEl("div", {text:`Week ${week}`, attr:{style:"font-size:12px;font-weight:820;color:rgba(255,255,255,0.58);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:7px 10px;"}});
chips.createEl("div", {text:`${hemisphere} hemisphere`, attr:{style:"font-size:12px;font-weight:820;color:rgba(255,255,255,0.58);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:7px 10px;"}});

const grid = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin-bottom:14px;"}});
for (const b of blocks) {
  const active = b.number === activeBlock;
  const c = card(grid, `padding:15px;border-top:2px solid ${b.color};${active ? `box-shadow:0 0 0 1px ${b.color}66,0 10px 30px ${b.color}22;` : ""}`);
  const head = c.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:10px;align-items:flex-start;margin-bottom:10px;"}});
  const title = head.createEl("div", {attr:{style:"min-width:0;"}});
  title.createEl("div", {text:`Block ${b.number}`, attr:{style:`font-size:11px;font-weight:820;color:${b.color};text-transform:uppercase;letter-spacing:.55px;margin-bottom:5px;`}});
  title.createEl("div", {text:b.name, attr:{style:"font-size:19px;font-weight:850;color:#fff;line-height:1.08;"}});
  const season = head.createEl("div", {attr:{style:`text-align:right;color:${b.color};background:${b.color}1c;border:1px solid ${b.color}66;border-radius:11px;padding:7px 9px;white-space:nowrap;flex-shrink:0;`}});
  season.createEl("div", {text:b.season, attr:{style:"font-size:12px;font-weight:860;line-height:1.05;"}});
  season.createEl("div", {text:b.months, attr:{style:"font-size:10px;font-weight:780;letter-spacing:.45px;text-transform:uppercase;margin-top:3px;opacity:.78;"}});
  row(c, "Focus", b.focus);
  row(c, "Keep", b.keep);
  row(c, "Week", b.week);
  row(c, "Watch", b.watch);
}

const note = card(wrap, "padding:14px;border-left:3px solid #FF3B30;");
note.createEl("div", {text:"Rule of thumb", attr:{style:"font-size:15px;font-weight:820;color:#fff;"}});
note.createEl("div", {text:"Blocks choose the priority. They do not ban the other work; they keep it at maintenance dose.", attr:{style:"font-size:12px;color:rgba(255,255,255,0.56);line-height:1.42;margin-top:6px;"}});

} catch (err) {
  console.error("Training Blocks render failed", err);
  const card = dv.container.createEl("div", {attr:{style:"background:rgba(255,255,255,0.055);border:1px solid rgba(255,255,255,0.12);border-left:3px solid #FF9500;border-radius:16px;padding:14px 16px;margin:8px 0 18px;"}});
  card.createEl("div", {text:"Blocks are warming up", attr:{style:"font-size:15px;font-weight:780;color:#fff;"}});
  card.createEl("div", {text:"Dataview did not finish rendering this pass. Reopen the note after Obsidian finishes syncing/indexing.", attr:{style:"font-size:12px;color:rgba(255,255,255,0.48);line-height:1.35;margin-top:5px;"}});
}
```
