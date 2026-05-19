> [!abstract]- ⚡ Warm-Up 
<%* if (tp.w.calisVariant === "recommended") { -%>
> - [ ] Yuri's Shoulder Band Warmup
> - [ ] Squat Sky Reaches
> - [ ] GMB Wrist Prep
> - [ ] Deadbugs
> - [ ] Arch Hang
> - [ ] Parallel Bar Support
<%* } else { -%>
> - [ ] Yuri's Shoulder Band Warmup
> - [ ] GMB Wrist Prep
> - [ ] Arch Hang
<%* } -%>

<%* if (tp.w.calisVariant === "recommended") { -%>
> [!success]- 💪 Exercise Selection
> #### PAIR 1: PULL & SQUAT
> *Target: <% tp.w.getAdvice(tp.w.prev.pullup.s1, tp.w.prev.pullup.s2, tp.w.prev.pullup.s3) %>*
> 
> **PULL**`INPUT[inlineSelect(option(Scapular Pull-up), option(Arch Hang), option(Negative Pull-up), option(Pull-up), option(L-sit Pull-up), option(Weighted Pull-up)):rr_pullup_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_pullup_weight]`
> 
> ---
> 
> **SQUAT**`INPUT[inlineSelect(option(Assisted Squat), option(Bodyweight Squat), option(Split Squat), option(Bulgarian Split Squat), option(Beginner Shrimp Squat), option(Intermediate Shrimp Squat), option(Advanced Shrimp Squat), option(Partial ROM Pistol Squat), option(Pistol Squat), option(Weighted Pistol Squat)):rr_squat_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_squat_weight]`
> 
> #### PAIR 2: DIP & HINGE
> *Target: <% tp.w.getAdvice(tp.w.prev.dip.s1, tp.w.prev.dip.s2, tp.w.prev.dip.s3) %>*
> 
> **DIP**`INPUT[inlineSelect(option(Parallel Bar Support Hold), option(Negative Dip), option(Parallel Bar Dip), option(Ring RTO Dip), option(Weighted Dip)):rr_dip_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_dip_weight]`
> 
> ---
> 
> **HINGE**`INPUT[inlineSelect(option(Beginner Harop Curl), option(Harop Curl), option(Advanced Harop Curl), option(Banded Nordic Curl), option(Nordic Curl)):rr_hinge_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_hinge_weight]`
> 
> #### PAIR 3: ROW & PUSH-UP
> *Target: <% tp.w.getAdvice(tp.w.prev.row.s1, tp.w.prev.row.s2, tp.w.prev.row.s3) %>*
> 
> **ROW**`INPUT[inlineSelect(option(Vertical Row), option(Incline Row), option(Horizontal Row), option(Wide Row), option(Tuck Front Lever Row), option(Advanced Tuck Front Lever Row)):rr_row_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_row_weight]`
> 
> ---
> 
> **PUSH-UP**`INPUT[inlineSelect(option(Wall Push-up), option(Incline Push-up), option(Standard Push-up), option(Diamond Push-up), option(Pseudo Planche Push-up), option(Ring Push-up), option(Weighted Push-up)):rr_pushup_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_pushup_weight]`
> 
> #### CORE TRIPLET
> *Target: 3 sets of 8-12 reps or 10-30s holds*
> 
> **ANTI-EXTENSION**`INPUT[inlineSelect(option(Plank), option(Ring Plank), option(Hollow Body Hold), option(Deadbug), option(Kneeling Ab Wheel Rollout), option(Kneeling Ring Ab Rollout), option(Standing Ab Wheel Rollout), option(Standing Ring Ab Rollout)):rr_core_antiext_progression]`
> 
> ---
> 
> **ANTI-ROTATION**`INPUT[inlineSelect(option(Side Plank), option(Short Lever Copenhagen Plank), option(Long Lever Copenhagen Plank), option(Dynamic Copenhagen Plank), option(Elevated Copenhagen Plank)):rr_core_antirot_progression]`
> 
> ---
> 
> **EXTENSION**`INPUT[inlineSelect(option(Arch Body Hold), option(Arch Body Rocks), option(Reverse Hyperextension)):rr_core_ext_progression]`

> [!success]- 1️⃣ Pair 1
> #### SET 1
> **PULL**`INPUT[number(placeholder(<% tp.w.prev.pullup.s1 || "Reps" %>)):rr_pullup_s1_reps]`
> **SQUAT**`INPUT[number(placeholder(<% tp.w.prev.squat.s1 || "Reps" %>)):rr_squat_s1_reps]`
> 
> ---
> 
> #### SET 2
> **PULL**`INPUT[number(placeholder(<% tp.w.prev.pullup.s2 || "Reps" %>)):rr_pullup_s2_reps]`
> **SQUAT**`INPUT[number(placeholder(<% tp.w.prev.squat.s2 || "Reps" %>)):rr_squat_s2_reps]`
> 
> ---
> 
> #### SET 3
> **PULL**`INPUT[number(placeholder(<% tp.w.prev.pullup.s3 || "Reps" %>)):rr_pullup_s3_reps]`
> **SQUAT**`INPUT[number(placeholder(<% tp.w.prev.squat.s3 || "Reps" %>)):rr_squat_s3_reps]`

> [!success]- 2️⃣ Pair 2
> #### SET 1
> **DIP**`INPUT[number(placeholder(<% tp.w.prev.dip.s1 || "Reps" %>)):rr_dip_s1_reps]`
> **HINGE**`INPUT[number(placeholder(<% tp.w.prev.hinge.s1 || "Reps" %>)):rr_hinge_s1_reps]`
> 
> ---
> 
> #### SET 2
> **DIP**`INPUT[number(placeholder(<% tp.w.prev.dip.s2 || "Reps" %>)):rr_dip_s2_reps]`
> **HINGE**`INPUT[number(placeholder(<% tp.w.prev.hinge.s2 || "Reps" %>)):rr_hinge_s2_reps]`
> 
> ---
> 
> #### SET 3
> **DIP**`INPUT[number(placeholder(<% tp.w.prev.dip.s3 || "Reps" %>)):rr_dip_s3_reps]`
> **HINGE**`INPUT[number(placeholder(<% tp.w.prev.hinge.s3 || "Reps" %>)):rr_hinge_s3_reps]`

> [!success]- 3️⃣ Pair 3
> #### SET 1
> **ROW**`INPUT[number(placeholder(<% tp.w.prev.row.s1 || "Reps" %>)):rr_row_s1_reps]`
> **PUSH-UP**`INPUT[number(placeholder(<% tp.w.prev.pushup.s1 || "Reps" %>)):rr_pushup_s1_reps]`
> 
> ---
> 
> #### SET 2
> **ROW**`INPUT[number(placeholder(<% tp.w.prev.row.s2 || "Reps" %>)):rr_row_s2_reps]`
> **PUSH-UP**`INPUT[number(placeholder(<% tp.w.prev.pushup.s2 || "Reps" %>)):rr_pushup_s2_reps]`
> 
> ---
> 
> #### SET 3
> **ROW**`INPUT[number(placeholder(<% tp.w.prev.row.s3 || "Reps" %>)):rr_row_s3_reps]`
> **PUSH-UP**`INPUT[number(placeholder(<% tp.w.prev.pushup.s3 || "Reps" %>)):rr_pushup_s3_reps]`

> [!success]- 🔄 Core Triplet
> #### SET 1
> **ANTI-EXT**`INPUT[text(placeholder(Sec/Reps)):rr_core_antiext_s1]`
> **ANTI-ROT**`INPUT[text(placeholder(Sec/Reps)):rr_core_antirot_s1]`
> **EXTENSION**`INPUT[text(placeholder(Sec/Reps)):rr_core_ext_s1]`
> 
> ---
> 
> #### SET 2
> **ANTI-EXT**`INPUT[text(placeholder(Sec/Reps)):rr_core_antiext_s2]`
> **ANTI-ROT**`INPUT[text(placeholder(Sec/Reps)):rr_core_antirot_s2]`
> **EXTENSION**`INPUT[text(placeholder(Sec/Reps)):rr_core_ext_s2]`
> 
> ---
> 
> #### SET 3
> **ANTI-EXT**`INPUT[text(placeholder(Sec/Reps)):rr_core_antiext_s3]`
> **ANTI-ROT**`INPUT[text(placeholder(Sec/Reps)):rr_core_antirot_s3]`
> **EXTENSION**`INPUT[text(placeholder(Sec/Reps)):rr_core_ext_s3]`

<%* } else { -%>
> [!success]- 📋 Circuit Selection
> #### SQUAT / PUSH / ROW / PLANK
> 
> **SQUAT**`INPUT[inlineSelect(option(Assisted Squat), option(Bodyweight Squat), option(Split Squat), option(Bulgarian Split Squat), option(Beginner Shrimp Squat), option(Intermediate Shrimp Squat), option(Advanced Shrimp Squat), option(Partial ROM Pistol Squat), option(Pistol Squat), option(Weighted Pistol Squat)):rr_squat_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_squat_weight]`
> 
> ---
> 
> **PUSH-UP**`INPUT[inlineSelect(option(Wall Push-up), option(Incline Push-up), option(Standard Push-up), option(Diamond Push-up), option(Pseudo Planche Push-up), option(Ring Push-up), option(Weighted Push-up)):rr_pushup_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_pushup_weight]`
> 
> ---
> 
> **ROW**`INPUT[inlineSelect(option(Vertical Row), option(Incline Row), option(Horizontal Row), option(Wide Row), option(Tuck Front Lever Row), option(Advanced Tuck Front Lever Row)):rr_row_progression]`
> **LOAD**`INPUT[number(placeholder(KG)):rr_row_weight]`
> 
> ---
> 
> **PLANK**`INPUT[inlineSelect(option(Plank), option(Ring Plank), option(Hollow Body Hold), option(Deadbug), option(Kneeling Ab Wheel Rollout), option(Kneeling Ring Ab Rollout), option(Standing Ab Wheel Rollout), option(Standing Ring Ab Rollout)):rr_core_antiext_progression]`

> [!success]- ⏱️ Circuit Working Sets
> #### ROUND 1
> **SQUAT**`INPUT[number(placeholder(<% tp.w.prev.squat.s1 || "Reps" %>)):rr_squat_s1_reps]`
> **PUSH-UP**`INPUT[number(placeholder(<% tp.w.prev.pushup.s1 || "Reps" %>)):rr_pushup_s1_reps]`
> **ROW**`INPUT[number(placeholder(<% tp.w.prev.row.s1 || "Reps" %>)):rr_row_s1_reps]`
> **PLANK**`INPUT[text(placeholder(Sec/Reps)):rr_core_antiext_s1]`
> 
> ---
> 
> #### ROUND 2
> **SQUAT**`INPUT[number(placeholder(<% tp.w.prev.squat.s2 || "Reps" %>)):rr_squat_s2_reps]`
> **PUSH-UP**`INPUT[number(placeholder(<% tp.w.prev.pushup.s2 || "Reps" %>)):rr_pushup_s2_reps]`
> **ROW**`INPUT[number(placeholder(<% tp.w.prev.row.s2 || "Reps" %>)):rr_row_s2_reps]`
> **PLANK**`INPUT[text(placeholder(Sec/Reps)):rr_core_antiext_s2]`
> 
> ---
> 
> #### ROUND 3
> **SQUAT**`INPUT[number(placeholder(<% tp.w.prev.squat.s3 || "Reps" %>)):rr_squat_s3_reps]`
> **PUSH-UP**`INPUT[number(placeholder(<% tp.w.prev.pushup.s3 || "Reps" %>)):rr_pushup_s3_reps]`
> **ROW**`INPUT[number(placeholder(<% tp.w.prev.row.s3 || "Reps" %>)):rr_row_s3_reps]`
> **PLANK**`INPUT[text(placeholder(Sec/Reps)):rr_core_antiext_s3]`
<%* } -%>
