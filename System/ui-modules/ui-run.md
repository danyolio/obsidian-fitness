> [!quick-run]+ Run
> **Type** `INPUT[inlineSelect(option(Easy), option(Interval), option(Tempo), option(Long), option(Race), option(Imported)):run_type]`
>
> **Distance** `INPUT[number(placeholder(KM)):run_distance_km]`
>
> **Time** `INPUT[text(placeholder(MM:SS)):run_time]`
>
> **Effort** `INPUT[inlineSelect(option(1), option(2), option(3), option(4), option(5), option(6), option(7), option(8), option(9), option(10)):run_perceived_effort]`

> [!heart|optional]- Heart
> **Avg HR** `INPUT[number(placeholder(AVG BPM)):run_avg_hr]`
>
> **Zone 2** `INPUT[number(placeholder(Z2 MIN)):run_zone2_time_min]`
>
> **Zone 4+** `INPUT[number(placeholder(Z4 MIN)):run_zone4_time_min]`
