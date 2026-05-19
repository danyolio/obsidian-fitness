function getAdvice(s1, s2, s3) {
    const total = (Number(s1) || 0) + (Number(s2) || 0) + (Number(s3) || 0);
    if (total >= 24) return "3x8 achieved! Level up progression next session.";
    return "Target: 3 sets of 5 - 8 reps";
}

module.exports = async (tp) => {
    // 1. Initialize the global data bridge
    tp.w = {}; 

    const d = window.moment();
    tp.w.dateStr = d.format("YYYY-MM-DD");
    tp.w.day = d.format("dddd");

    // 2. Prompt for Workout Type
    const allTypes = ["Run", "Lift", "Calisthenics", "KOT", "Climb", "Swim", "Yoga", "Sauna", "Cardio"];
    const typeLabels = ["🏃 Run", "🏋️ Lift", "💪 Calisthenics", "🦵 Knees Over Toes", "🧗 Climb", "🏊 Swim", "🧘 Yoga", "🔥 Sauna", "⚽ Cardio"];
    const wt = await tp.system.suggester(typeLabels, allTypes, false, "Which workout?");
    
    // If the user cancels the menu, stop the script
    if (!wt) return; 
    tp.w.wt = wt;

    if (wt === "Lift") {
        tp.w.liftEx = await tp.system.suggester(["Deadlift", "Squat", "Bench", "OHP"], ["deadlift", "squat", "bench", "ohp"], false, "Which lift?");
        if (!tp.w.liftEx) {
            tp.w.wt = "";
            return;
        }
    }

    let cfg = {};
    const cfgFile = app.vault.getAbstractFileByPath("System/settings.md");
    const cachedCfg = cfgFile ? app.metadataCache.getFileCache(cfgFile)?.frontmatter : null;
    if (cachedCfg) {
        cfg = {...cachedCfg};
    }
    const dv = app.plugins.plugins.dataview?.api;
    if (dv) {
        const cfgPage = dv.page("System/settings") || dv.page("System/settings.md") || dv.page('"System/settings"');
        if (cfgPage) {
            for (const [key, value] of Object.entries(cfgPage)) {
                if (cfg[key] === undefined) cfg[key] = value;
            }
        }
    }
    tp.w.cfg = cfg;

    // 3. Global Math
    const cleanSetting = value => String(value || "").trim();
    const cleanOverride = value => {
        const text = cleanSetting(value);
        return ["auto", "last logged", "null", "none"].includes(text.toLowerCase()) ? "" : text;
    };
    const hemisphere = cleanSetting(cfg.hemisphere).toLowerCase().startsWith("n") ? "Northern" : "Southern";
    const defaultProgramStart = `${d.format("YYYY")}-${hemisphere === "Northern" ? "09" : "03"}-01`;
    const startDateRaw = cfg.program_start_date?.toISODate?.() || cfg.program_start_date || defaultProgramStart;
    const startDate = window.moment(startDateRaw.toString().slice(0, 10), "YYYY-MM-DD", true);
    const validStartDate = startDate.isValid() ? startDate : window.moment(defaultProgramStart);
    const daysDiff = d.diff(validStartDate, 'days');
    tp.w.weekNum = Math.max(1, Math.floor(daysDiff / 7) + 1);
    const derivedBlock = Math.min(4, Math.floor((tp.w.weekNum - 1) / 12) + 1);
    const configuredBlock = Number(cfg.current_block);
    tp.w.blockNum = configuredBlock >= 1 && configuredBlock <= 4 ? configuredBlock : derivedBlock;
    const blockNames = {1: "Endurance", 2: "Strength", 3: "Muscle", 4: "Resilience"};
    tp.w.blockName = cleanSetting(cfg.block_name) || blockNames[tp.w.blockNum] || "Off-Season";

    // 4. LIFT ENGINE
    if (wt === "Lift") {
        tp.w.liftTM = cfg[`tm_${tp.w.liftEx}`] || 100;
        tp.w.liftWeek = 1;
        
        if (dv) {
            const pastLifts = dv.pages('"Workouts"').where(p => p.workout_type === "Lift" && p.lift_exercise === tp.w.liftEx && p.file.name !== tp.file.title).sort(p => p.date, 'desc');
            const lastLiftSession = pastLifts.length > 0 ? pastLifts[0] : null;
            if (lastLiftSession && lastLiftSession.lift_week) tp.w.liftWeek = (lastLiftSession.lift_week % 4) + 1;
        }

        if (tp.w.liftWeek === 1) { tp.w.phaseName = "3x5"; tp.w.s1Pct = 0.65; tp.w.s2Pct = 0.75; tp.w.s3Pct = 0.85; tp.w.s1Target = "5"; tp.w.s2Target = "5"; tp.w.s3Target = "5+"; } 
        else if (tp.w.liftWeek === 2) { tp.w.phaseName = "3x3"; tp.w.s1Pct = 0.70; tp.w.s2Pct = 0.80; tp.w.s3Pct = 0.90; tp.w.s1Target = "3"; tp.w.s2Target = "3"; tp.w.s3Target = "3+"; } 
        else if (tp.w.liftWeek === 3) { tp.w.phaseName = "5/3/1"; tp.w.s1Pct = 0.75; tp.w.s2Pct = 0.85; tp.w.s3Pct = 0.95; tp.w.s1Target = "5"; tp.w.s2Target = "3"; tp.w.s3Target = "1+"; } 
        else { tp.w.phaseName = "Deload"; tp.w.s1Pct = 0.40; tp.w.s2Pct = 0.50; tp.w.s3Pct = 0.60; tp.w.s1Target = "5"; tp.w.s2Target = "5"; tp.w.s3Target = "5"; }

        tp.w.s1Weight = Math.round((tp.w.liftTM * tp.w.s1Pct) / 2.5) * 2.5;
        tp.w.s2Weight = Math.round((tp.w.liftTM * tp.w.s2Pct) / 2.5) * 2.5;
        tp.w.s3Weight = Math.round((tp.w.liftTM * tp.w.s3Pct) / 2.5) * 2.5;
        tp.w.liftTopWeight = tp.w.s3Weight; 
        
        const suppPct = tp.w.liftWeek === 1 ? 0.65 : tp.w.liftWeek === 2 ? 0.70 : tp.w.liftWeek === 3 ? 0.75 : 0.40;
        tp.w.liftSupplementalWeight = Math.round((tp.w.liftTM * suppPct) / 2.5) * 2.5;
        
        if (tp.w.liftWeek === 1) new Notice(`Week 1 of 5/3/1! Make sure you updated your ${tp.w.liftEx} TM in settings.md!`, 5000);
    }

    // 5. CALISTHENICS ENGINE
    if (wt === "Calisthenics") {
        tp.w.calisVariant = await tp.system.suggester(["Recommended (Full 45m)", "Minimal (20m)"], ["recommended", "minimal"], false, "Which Calisthenics variant?");
        if (!tp.w.calisVariant) {
            tp.w.wt = "";
            return;
        }

        if (dv) {
            const pastWorkouts = dv.pages('"Workouts"').where(p => p.workout_type === "Calisthenics" && p.file.name !== tp.file.title).sort(p => p.date, 'desc');
            const pastSessions = typeof pastWorkouts.array === "function" ? pastWorkouts.array() : Array.from(pastWorkouts);
            const lastSession = pastSessions.length > 0 ? pastSessions[0] : null;

            const getRep = (ex, set) => lastSession && lastSession[`rr_${ex}_s${set}_reps`] ? lastSession[`rr_${ex}_s${set}_reps`] : "";
            const getWeight = (ex) => lastSession && lastSession[`rr_${ex}_weight`] ? lastSession[`rr_${ex}_weight`] : "";
            const getProgression = (ex) => {
                const field = `rr_${ex}_progression`;
                const session = pastSessions.find(p => cleanSetting(p[field]));
                return session ? cleanSetting(session[field]) : "";
            };

            tp.w.prev = {
                pushup: { progression: getProgression('pushup'), s1: getRep('pushup', 1), s2: getRep('pushup', 2), s3: getRep('pushup', 3), w: getWeight('pushup') },
                row:    { progression: getProgression('row'),    s1: getRep('row', 1),    s2: getRep('row', 2),    s3: getRep('row', 3),    w: getWeight('row') },
                dip:    { progression: getProgression('dip'),    s1: getRep('dip', 1),    s2: getRep('dip', 2),    s3: getRep('dip', 3),    w: getWeight('dip') },
                pullup: { progression: getProgression('pullup'), s1: getRep('pullup', 1), s2: getRep('pullup', 2), s3: getRep('pullup', 3), w: getWeight('pullup') },
                pike:   { progression: getProgression('pike'),   s1: getRep('pike', 1),   s2: getRep('pike', 2),   s3: getRep('pike', 3) },
                squat:  { progression: getProgression('squat'),  s1: getRep('squat', 1),  s2: getRep('squat', 2),  s3: getRep('squat', 3),  w: getWeight('squat') },
                hinge:  { progression: getProgression('hinge'),  s1: getRep('hinge', 1),  s2: getRep('hinge', 2),  s3: getRep('hinge', 3),  w: getWeight('hinge') }
            };
        } else {
            const def = { progression: "", s1: 5, s2: 5, s3: 5, w: 0 };
            tp.w.prev = { pushup: def, row: def, dip: def, pullup: def, pike: def, squat: def, hinge: def };
        }

        const progressionFor = ex => cleanOverride(cfg[`rr_${ex}`]) || tp.w.prev[ex]?.progression || "";
        tp.w.calisProgression = {
            pushup: progressionFor("pushup"),
            row: progressionFor("row"),
            dip: progressionFor("dip"),
            pullup: progressionFor("pullup"),
            squat: progressionFor("squat"),
            hinge: progressionFor("hinge")
        };

        tp.w.getAdvice = getAdvice;
    }

    // 6. KOT ENGINE
    if (wt === "KOT") {
        if (dv) {
            const pastKOT = dv.pages('"Workouts"')
                .where(p => (p.workout_type === "KOT" || p.workout_type === "Knees Over Toes") && p.file.name !== tp.file.title)
                .sort(p => p.date, 'desc');
            const pastSessions = typeof pastKOT.array === "function" ? pastKOT.array() : Array.from(pastKOT);
            const getProgression = field => {
                const session = pastSessions.find(p => cleanSetting(p[field]));
                return session ? cleanSetting(session[field]) : "";
            };
            tp.w.kotProgression = {
                locomotion: cleanOverride(cfg.kot_locomotion) || getProgression("kot_locomotion_prog"),
                tibialis: cleanOverride(cfg.kot_tibialis) || getProgression("kot_tib_prog"),
                fhlCalf: cleanOverride(cfg.kot_fhl_calf) || getProgression("kot_fhl_prog"),
                atgSplit: cleanOverride(cfg.kot_atg_split) || getProgression("kot_atg_prog"),
                stepup: cleanOverride(cfg.kot_stepup) || getProgression("kot_stepup_prog"),
                nordic: cleanOverride(cfg.kot_nordic) || getProgression("kot_nordic_prog"),
                seatedGm: cleanOverride(cfg.kot_seated_gm) || getProgression("kot_gm_prog")
            };
        } else {
            tp.w.kotProgression = {
                locomotion: cleanOverride(cfg.kot_locomotion),
                tibialis: cleanOverride(cfg.kot_tibialis),
                fhlCalf: cleanOverride(cfg.kot_fhl_calf),
                atgSplit: cleanOverride(cfg.kot_atg_split),
                stepup: cleanOverride(cfg.kot_stepup),
                nordic: cleanOverride(cfg.kot_nordic),
                seatedGm: cleanOverride(cfg.kot_seated_gm)
            };
        }
    }

    // 7. Final UI Helper
    tp.w.durationField = "";
    if (wt === "Calisthenics") tp.w.durationField = "rr_duration_min";
    else if (wt === "KOT") tp.w.durationField = "kot_duration_min";
    else if (wt === "Climb") tp.w.durationField = "climb_duration_min";
    else if (wt === "Swim") tp.w.durationField = "swim_duration_min";
    else if (wt === "Yoga") tp.w.durationField = "yoga_duration_min";
    else if (wt === "Sauna") tp.w.durationField = "sauna_duration_min";
    else if (wt === "Cardio") tp.w.durationField = "cardio_duration_min";
};
