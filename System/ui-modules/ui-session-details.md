> [!abstract|optional]- Notes
> **Workout Date**`INPUT[date:date]`
>
<%* if (tp.w.durationField !== "") { -%>
<%* if (!["Run", "Cardio", "Climb", "Swim", "Yoga", "Sauna"].includes(tp.w.wt)) { -%>
>
> **Duration (min)**`INPUT[number:<% tp.w.durationField %>]`
>
<%* } -%>
<%* } -%>
> **Notes**`INPUT[textArea:notes]`
