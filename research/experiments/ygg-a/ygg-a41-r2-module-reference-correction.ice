YGG-A41 R2 IMPLEMENTATION CORRECTION — PRE-SCIENTIFIC-EXECUTION
Failed run: 36277245385.
Failure occurred before any YGG-A41 scientific arm executed and before any result JSON was produced.
Defect: implementation referenced lu.t.make_arrivals, but the bound A-lane t alias is already module lu2t_task4_exact_parent_feasibility_v1; the frozen helper is t.make_arrivals directly.
Correction: replace only lu.t.make_arrivals references with lu.make_arrivals. No scientific arm, hybrid construction rule, classification, threshold, population, mode, target, or validity criterion changes.
Original preregistration remains controlling: 7f667e5360ab502312bc29d13b5fe9c378fcb879.
Rerun exact frozen design after correction.
