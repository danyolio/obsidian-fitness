# Programs

```dataviewjs
const wrap = dv.container;
const programs = [
  {
    name:"80/20 Running",
    tag:"Aerobic",
    color:"#FF3B30",
    purpose:"Build aerobic capacity and recover better between harder training days.",
    use:["Zone 2 base runs","One hard run when recovery allows","Race or time-trial days"],
    guardrail:"Most runs should feel easy enough to repeat tomorrow."
  },
  {
    name:"5/3/1",
    tag:"Strength",
    color:"#FF9500",
    purpose:"Heavy strength without letting barbell fatigue eat the whole week.",
    use:["Deadlift, squat, bench, OHP","Conservative training maxes","AMRAP top sets on good days"],
    guardrail:"Do not stack heavy posterior-chain work with hard climbing or hard running."
  },
  {
    name:"Calisthenics",
    tag:"Progression",
    color:"#5856D6",
    purpose:"Build useful bodyweight strength, clean reps, and visible progressions over time.",
    use:["Pull-up, row, dip, push-up, and squat totals","Harder progressions after clean reps","Minimal sessions when life is crowded"],
    guardrail:"Treat progression jumps as new exercises, not just harder reps."
  },
  {
    name:"Knees Over Toes",
    tag:"Tissue",
    color:"#5AC8FA",
    purpose:"Knees, ankles, calves, and hips that tolerate running, climbing, and sport.",
    use:["Tibialis, calf, VMO, ATG split squat","Post-run recovery sessions","Low-friction restorative work"],
    guardrail:"Progress range and control before load."
  },
  {
    name:"Climbing",
    tag:"Skill",
    color:"#30D158",
    purpose:"Turn strength and conditioning into actual movement skill.",
    use:["Technique volume","Comfortable grade mileage","Projecting when grip and sleep are fresh"],
    guardrail:"Hard climbing is systemic stress, not just an upper-body session."
  },
  {
    name:"Yoga / Downshift",
    tag:"Recovery",
    color:"#AF52DE",
    purpose:"Mobility, breath, and nervous system recovery so the next hard day is better.",
    use:["High-load weeks","Poor sleep days","Evening recovery when motivation is low"],
    guardrail:"Choose easy consistency over heroic sessions."
  }
];

const hero = wrap.createEl("div", {attr:{style:"background:linear-gradient(158deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03));border:1px solid rgba(255,255,255,0.12);border-radius:20px;padding:20px;margin:8px 0 18px;box-shadow:0 8px 34px rgba(0,0,0,0.42),inset 0 1px 0 rgba(255,255,255,0.12);"}});
hero.createEl("div", {text:"Training Methods", attr:{style:"font-size:24px;font-weight:820;color:#fff;line-height:1.05;"}});
hero.createEl("div", {text:"Use the right system for the adaptation you want, then keep the rest ticking over.", attr:{style:"font-size:13px;color:rgba(255,255,255,0.48);line-height:1.4;margin-top:8px;"}});

const grid = wrap.createEl("div", {attr:{style:"display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px;margin-bottom:18px;"}});
for (const p of programs) {
  const card = grid.createEl("div", {attr:{style:`background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.09);border-top:2px solid ${p.color};border-radius:16px;padding:15px;min-width:0;`}});
  const head = card.createEl("div", {attr:{style:"display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:10px;"}});
  head.createEl("div", {text:p.name, attr:{style:"font-size:16px;font-weight:820;color:#fff;line-height:1.1;"}});
  head.createEl("div", {text:p.tag, attr:{style:`font-size:10px;font-weight:820;color:${p.color};background:${p.color}22;border:1px solid ${p.color}66;border-radius:8px;padding:4px 7px;text-transform:uppercase;letter-spacing:.4px;white-space:nowrap;`}});
  card.createEl("div", {text:p.purpose, attr:{style:"font-size:12px;color:rgba(255,255,255,0.55);line-height:1.42;margin-bottom:12px;"}});
  const list = card.createEl("div", {attr:{style:"display:flex;flex-direction:column;gap:6px;margin-bottom:12px;"}});
  for (const item of p.use) {
    const row = list.createEl("div", {attr:{style:"display:flex;gap:8px;align-items:flex-start;"}});
    row.createEl("div", {attr:{style:`width:6px;height:6px;border-radius:99px;background:${p.color};margin-top:6px;flex-shrink:0;`}});
    row.createEl("div", {text:item, attr:{style:"font-size:12px;color:rgba(255,255,255,0.72);line-height:1.35;"}});
  }
  card.createEl("div", {text:p.guardrail, attr:{style:"font-size:11px;color:rgba(255,255,255,0.42);line-height:1.35;border-top:1px solid rgba(255,255,255,0.08);padding-top:10px;"}});
}

```
