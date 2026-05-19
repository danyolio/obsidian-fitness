> [!example]- 🏋️ <% tp.w.liftEx.charAt(0).toUpperCase() + tp.w.liftEx.slice(1) %> — Week <% tp.w.liftWeek %>
> *Phase: <% tp.w.phaseName %> | TM: <% tp.w.liftTM %>kg*
> 
> #### SET 1 (<% tp.w.s1Pct * 100 %>%)
> **LOAD (KG)**`INPUT[number(placeholder(<% tp.w.s1Weight %>)):lift_s1_weight]`
> **REPS**`INPUT[number(placeholder(<% tp.w.s1Target %>)):lift_s1_reps]`
> 
> ---
> 
> #### SET 2 (<% tp.w.s2Pct * 100 %>%)
> **LOAD (KG)**`INPUT[number(placeholder(<% tp.w.s2Weight %>)):lift_s2_weight]`
> **REPS**`INPUT[number(placeholder(<% tp.w.s2Target %>)):lift_s2_reps]`
> 
> ---
> 
> #### SET 3 <% tp.w.liftWeek === 4 ? "(DELOAD)" : "(AMRAP)" %>
> **LOAD (KG)**`INPUT[number(placeholder(<% tp.w.s3Weight %>)):lift_top_set_prescribed_weight]`
> **ACTUAL REPS**`INPUT[number(placeholder(<% tp.w.s3Target %>)):lift_top_set_actual_reps]`
> 
> ---
> 
> **RPE**`INPUT[slider(minValue(1), maxValue(10)):lift_rpe]`

> [!example]- 🛠️ Supplemental & Accessories
> 
> **SCHEME**`INPUT[inlineSelect(option(FSL 5x5), option(BBB 5x10), option(SSL 5x5), option(BBS 10x5), option(None)):lift_supplemental_scheme]`
> **LOAD (KG)**`INPUT[number(placeholder(<% tp.w.liftSupplementalWeight %>)):lift_supplemental_weight]`
> **SETS**`INPUT[number(placeholder(Sets)):lift_supplemental_sets]`
> **REPS**`INPUT[number(placeholder(Reps)):lift_supplemental_reps]`
> 
> ---
> 
> **ACCESSORY 1**`INPUT[text(placeholder(e.g. Barbell Rows)):lift_accessory_1]`
> **SETS X REPS**`INPUT[text(placeholder(e.g. 3x10)):lift_accessory_1_sets_reps]`
> 
> ---
> 
> **ACCESSORY 2**`INPUT[text(placeholder(e.g. Face Pulls)):lift_accessory_2]`
> **SETS X REPS**`INPUT[text(placeholder(e.g. 3x15)):lift_accessory_2_sets_reps]`
> 
> ---
> 
> **ACCESSORY 3**`INPUT[text(placeholder(e.g. Ab Wheel)):lift_accessory_3]`
> **SETS X REPS**`INPUT[text(placeholder(e.g. 3x12)):lift_accessory_3_sets_reps]`