<%* // Only run the engine if this is a brand new file (no workout_type yet)
if (!tp.frontmatter.workout_type) {
    await tp.user.workoutEngine(tp);
}
// If the user cancelled the menu, stop
if (!tp.w?.wt) return; 
_%>
---
schema_version: 1
date: <% tp.w.dateStr %>
day: <% tp.w.day %>
block: <% tp.w.blockNum %>
block_name: "<% tp.w.blockName %>"
week: <% tp.w.weekNum %>
workout_type: "<% tp.w.wt %>"
<%* if (tp.w.wt === "Lift") { -%>
lift_exercise: "<% tp.w.liftEx %>"
lift_week: <% tp.w.liftWeek %>
lift_training_max: <% tp.w.liftTM %>
lift_top_set_prescribed_weight: <% tp.w.liftTopWeight %>
lift_top_set_actual_reps: ""
lift_rpe: ""
lift_supplemental_scheme: ""
lift_supplemental_weight: <% tp.w.liftSupplementalWeight %>
lift_supplemental_sets: ""
lift_supplemental_reps: ""
lift_accessory_1: ""
lift_accessory_1_sets_reps: ""
lift_accessory_2: ""
lift_accessory_2_sets_reps: ""
lift_accessory_3: ""
lift_accessory_3_sets_reps: ""
<%* } else if (tp.w.wt === "Run") { -%>
run_type: ""
run_distance_km: ""
run_time: ""
run_avg_hr: ""
run_zone2_time_min: ""
run_zone4_time_min: ""
run_perceived_effort: ""
<%* } else if (tp.w.wt === "Calisthenics") { -%>
rr_variant: "<% tp.w.calisVariant %>"
rr_warmup: ""
rr_warmup_minimal: ""
rr_pullup_progression: "<% tp.w.calisProgression?.pullup || "" %>"
rr_pullup_weight: "<% tp.w.prev.pullup?.w || "" %>"
rr_pullup_s1_reps: ""
rr_pullup_s2_reps: ""
rr_pullup_s3_reps: ""
rr_squat_progression: "<% tp.w.calisProgression?.squat || "" %>"
rr_squat_weight: "<% tp.w.prev.squat?.w || "" %>"
rr_squat_s1_reps: ""
rr_squat_s2_reps: ""
rr_squat_s3_reps: ""
rr_dip_progression: "<% tp.w.calisProgression?.dip || "" %>"
rr_dip_weight: "<% tp.w.prev.dip?.w || "" %>"
rr_dip_s1_reps: ""
rr_dip_s2_reps: ""
rr_dip_s3_reps: ""
rr_hinge_progression: "<% tp.w.calisProgression?.hinge || "" %>"
rr_hinge_weight: "<% tp.w.prev.hinge?.w || "" %>"
rr_hinge_s1_reps: ""
rr_hinge_s2_reps: ""
rr_hinge_s3_reps: ""
rr_row_progression: "<% tp.w.calisProgression?.row || "" %>"
rr_row_weight: "<% tp.w.prev.row?.w || "" %>"
rr_row_s1_reps: ""
rr_row_s2_reps: ""
rr_row_s3_reps: ""
rr_pushup_progression: "<% tp.w.calisProgression?.pushup || "" %>"
rr_pushup_weight: "<% tp.w.prev.pushup?.w || "" %>"
rr_pushup_s1_reps: ""
rr_pushup_s2_reps: ""
rr_pushup_s3_reps: ""
rr_core_antiext_progression: ""
rr_core_antiext_s1: ""
rr_core_antiext_s2: ""
rr_core_antiext_s3: ""
rr_core_antirot_progression: ""
rr_core_antirot_s1: ""
rr_core_antirot_s2: ""
rr_core_antirot_s3: ""
rr_core_ext_progression: ""
rr_core_ext_s1: ""
rr_core_ext_s2: ""
rr_core_ext_s3: ""
<%* } else if (tp.w.wt === "KOT") { -%>
kot_locomotion_prog: "<% tp.w.kotProgression?.locomotion || "" %>"
kot_locomotion_mins: ""
kot_tib_prog: "<% tp.w.kotProgression?.tibialis || "" %>"
kot_tib_load: ""
kot_tib_reps: ""
kot_fhl_prog: "<% tp.w.kotProgression?.fhlCalf || "" %>"
kot_fhl_load: ""
kot_fhl_reps: ""
kot_atg_prog: "<% tp.w.kotProgression?.atgSplit || "" %>"
kot_atg_load: ""
kot_atg_reps: ""
kot_stepup_prog: "<% tp.w.kotProgression?.stepup || "" %>"
kot_stepup_load: ""
kot_stepup_reps: ""
kot_nordic_prog: "<% tp.w.kotProgression?.nordic || "" %>"
kot_nordic_reps: ""
kot_gm_prog: "<% tp.w.kotProgression?.seatedGm || "" %>"
kot_gm_load: ""
kot_gm_reps: ""
kot_acc_1: ""
kot_acc_1_prog: ""
kot_acc_1_load: ""
kot_acc_1_reps: ""
kot_acc_2: ""
kot_acc_2_prog: ""
kot_acc_2_load: ""
kot_acc_2_reps: ""
kot_pain_notes: ""
<%* } else if (tp.w.wt === "Climb") { -%>
climb_max_grade: ""
climb_problems_attempted: ""
climb_problems_sent: ""
<%* } else if (tp.w.wt === "Swim") { -%>
swim_distance_m: ""
swim_1km_time: ""
swim_stroke: ""
swim_avg_hr: ""
<%* } else if (tp.w.wt === "Yoga") { -%>
yoga_style: ""
<%* } else if (tp.w.wt === "Sauna") { -%>
sauna_rounds: ""
sauna_type: ""
sauna_cold_plunge: false
sauna_perceived_effort: ""
<%* } else if (tp.w.wt === "Cardio") { -%>
cardio_activity: ""
cardio_avg_hr: ""
cardio_perceived_effort: ""
<%* } -%>
<%* if (tp.w.durationField !== "") { -%>
<% tp.w.durationField %>: ""
<%* } -%>
notes: ""
---

<%*
const headIcons  = {Run:"🏃", Lift:"🏋️", Calisthenics:"💪", KOT:"🦵", Climb:"🧗", Swim:"🏊", Yoga:"🧘", Sauna:"🔥", Cardio:"⚽"};
const headColors = {Run:"#FF3B30", Lift:"#FF9500", Calisthenics:"#5856D6", KOT:"#5AC8FA", Climb:"#30D158", Swim:"#AF52DE", Yoga:"#AF52DE", Sauna:"#FFCC00", Cardio:"#FF2D55"};
const headSubs   = {Run:"80/20 Running", Lift:"Wendler 5/3/1", Calisthenics:"Reddit Routine", KOT:"Knees Over Toes", Climb:"Bouldering", Swim:"Pool Session", Yoga:"Mobility & Recovery", Sauna:"Heat Protocol", Cardio:"Court & Pitch Sports"};
const headWt = tp.w.wt === "Knees Over Toes" ? "KOT" : tp.w.wt;
const headTitle = headWt === "KOT" ? "Knees Over Toes" : headWt;
const headColor = headColors[headWt] || "#FF3B30";
const headDate = new Date(tp.w.dateStr + "T00:00:00").toLocaleDateString("en-GB", {weekday:"short", day:"numeric", month:"short"});
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
tR += `<div style="background:linear-gradient(158deg,rgba(255,255,255,0.068) 0%,rgba(255,255,255,0.028) 100%);
  backdrop-filter:blur(40px) saturate(160%);-webkit-backdrop-filter:blur(40px) saturate(160%);
  border:1px solid rgba(255,255,255,0.12);border-top:2px solid ${headColor};border-radius:22px;
  box-shadow:0 6px 30px rgba(0,0,0,0.48),0 0 44px ${headColor}14,inset 0 1px 0 rgba(255,255,255,0.16);
  padding:16px 18px;margin-bottom:14px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:0;left:16px;right:16px;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.22),transparent);"></div>
  <div style="display:flex;align-items:center;gap:13px;">
    <div style="font-size:34px;line-height:1;flex-shrink:0;">${headIcons[headWt] || "🏋️"}</div>
    <div style="flex:1;min-width:0;">
      <div style="font-size:9px;font-weight:760;letter-spacing:1px;text-transform:uppercase;color:${headColor};margin-bottom:5px;">${escapeHtml(headDate)} · Block ${tp.w.blockNum} · Week ${tp.w.weekNum}</div>
      <div style="font-size:24px;font-weight:760;color:#fff;line-height:1.05;">${escapeHtml(headTitle)}</div>
      <div style="font-size:12px;color:rgba(255,255,255,0.40);margin-top:3px;">${escapeHtml(headSubs[headWt] || "")} · ${escapeHtml(tp.w.blockName)}</div>
    </div>
  </div>
</div>\n\n`;
_%>

<%* // =====================================================================
// 2. THE VIEWS (ROUTING TO UI MODULES)
// =====================================================================
-%>

<%* if (tp.w.wt === "Run") { -%>
<% await tp.file.include("[[ui-run]]") %>
<%* } else if (tp.w.wt === "Lift") { -%>
<% await tp.file.include("[[ui-lift]]") %>
<%* } else if (tp.w.wt === "Calisthenics") { -%>
<% await tp.file.include("[[ui-calisthenics]]") %>
<%* } else if (tp.w.wt === "KOT") { -%>
<% await tp.file.include("[[ui-kot]]") %>
<%* } else if (tp.w.wt === "Climb") { -%>
<% await tp.file.include("[[ui-climb]]") %>
<%* } else if (tp.w.wt === "Swim") { -%>
<% await tp.file.include("[[ui-swim]]") %>
<%* } else if (tp.w.wt === "Yoga") { -%>
<% await tp.file.include("[[ui-yoga]]") %>
<%* } else if (tp.w.wt === "Sauna") { -%>
<% await tp.file.include("[[ui-sauna]]") %>
<%* } else if (tp.w.wt === "Cardio") { -%>
<% await tp.file.include("[[ui-cardio]]") %>
<%* } -%>

<% await tp.file.include("[[ui-session-details]]") %>
