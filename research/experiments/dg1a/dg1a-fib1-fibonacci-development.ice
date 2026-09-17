TITLE: DG-1A-FIB1 Fibonacci Development / Regeneration Ablation
DATE: 2026-09-17
STATUS: PLANNED — AFTER CANONICAL P0 BASELINE
TRACK: DG-1A / FOLLOW-ON ABLATION
CONFIDENCE: PLAUSIBLE

QUESTION
Can Fibonacci-structured developmental schedules improve resource efficiency, stability, topology distribution, or regeneration relative to matched linear, geometric, and learned schedules under equal hard resource budgets?

RATIONALE
Fibonacci/golden-ratio structure should not be assumed to improve intelligence. The scientifically useful hypothesis is narrower: staged capacity growth and irrational-angle/topological spacing may provide a compact prior for avoiding uncontrolled expansion, redundant overlap, and repair overshoot.

BOUNDARY
Do not modify canonical DG1A-P0 behavior or success criteria for this experiment.
DG1A-FIB1 begins only after a canonical P0 baseline is available.
No result from FIB1 may substitute for the P0 reproduction requirement.

HYPOTHESES
H-FIB1-A — GROWTH BUDGET
A Fibonacci capacity schedule can reach comparable task quality with lower developmental churn or lower peak active population than a matched linear or geometric schedule.
CONFIDENCE BEFORE RUN: SPECULATIVE.

H-FIB1-B — REGENERATION BUDGET
Fibonacci-staged repair can restore lost function with less repair work and less post-repair instability than matched linear or geometric repair schedules.
CONFIDENCE BEFORE RUN: PLAUSIBLE.

H-FIB1-C — TOPOLOGY PLACEMENT
Golden-angle/irrational-spacing placement may reduce redundant local overlap when later graph-based structural growth is enabled.
CONFIDENCE BEFORE RUN: SPECULATIVE.

H-FIB1-D — MODULE CAPACITY VOCABULARY
Constraining module-size choices to a Fibonacci family may reduce arbitrary capacity search while preserving useful specialization.
CONFIDENCE BEFORE RUN: SPECULATIVE.

PRIMARY EARLY EXPERIMENT
FIB1-R — REGENERATION SCHEDULING ABLATION
Use the same trained developmental organism and same damage family across schedules.

SCHEDULES
CONTROL-LINEAR
Increment available repair work by a fixed amount per repair stage.

CONTROL-GEOMETRIC
Increase repair budget geometrically under the same maximum total repair allowance.

CANDIDATE-FIBONACCI
Repair stage budgets follow a declared sequence such as:
1, 2, 3, 5, 8, 13, 21, ...
The sequence is a ceiling on new repair work, not a mandatory amount of growth.

ADAPTIVE-LEARNED
A bounded learned controller chooses the next repair budget under the same maximum total allowance.
This control is required before attributing benefit to Fibonacci specifically.

STOP CONDITION
After every repair stage, measure task/morphology recovery.
If the declared recovery criterion is achieved and remains stable for the confirmation window, further growth is not authorized.

MATCHING RULE
All schedule variants must have the same:
- maximum cumulative repair budget;
- maximum development steps;
- model/genome;
- damage severity family;
- evaluation horizon;
- random seed family;
- target/task;
- hard active-cell/resource ceiling.

PRIMARY METRICS
- final bounded recovery fraction;
- stable T50/T90;
- normalized recovery AUC;
- total developmental updates consumed;
- active cells per repair stage;
- peak active cells;
- resident bytes;
- wall-clock repair time;
- post-repair drift/relapse;
- amount of subsequently pruned repair structure when pruning is enabled.

FAILURE MODES TO DISTINGUISH
- schedule is merely slower;
- schedule wins only because it consumes more cumulative work;
- staged repair suppresses useful rapid recovery;
- apparent efficiency comes from under-damaging the model;
- geometric or learned schedules dominate Fibonacci;
- no meaningful difference exists.

GROWTH-BUDGET FOLLOW-ON
Once explicit structural replication exists, compare capacity ceilings:
LINEAR: 1,2,3,4,5,...
GEOMETRIC: 1,2,4,8,16,...
FIBONACCI: 1,2,3,5,8,13,...
LEARNED: bounded controller choice.

A capacity value is a maximum available population/module budget. Cells still require local utility/resource conditions to consume capacity.

TOPOLOGY FOLLOW-ON
When graph-based phenotype growth exists, test candidate placement/connection phases based on the golden angle approximately 137.507764 degrees or an equivalent irrational-spacing rule in the declared topology space.

This is not a claim that biological phyllotaxis is directly optimal for neural graphs. It is an ablation testing whether a low-complexity anti-overlap prior improves communication distribution under growth.

MODULE-SIZE FOLLOW-ON
When developmental neural modules replace latent cells, test a discrete module-capacity family such as:
3, 5, 8, 13, 21, 34, 55...
against unrestricted bounded integer sizes and a learned sizing controller.

EMERGENCE TEST
Separately from imposed Fibonacci schedules, record naturally learned population ratios, branching ratios, repair-stage ratios, and angular/topological spacing.
Do not label a pattern Fibonacci-like unless a preregistered quantitative fit supports that description.

SUCCESS CONDITION
Fibonacci-specific support requires replicated improvement over both linear and geometric matched controls on a declared efficiency/stability metric without worse primary task recovery, and must remain competitive with the bounded learned schedule.

A learned schedule independently converging near Fibonacci/phi-like ratios is stronger evidence for the developmental prior than success of a hand-imposed schedule alone.

DISPROOF / NEGATIVE RESULT
If Fibonacci schedules do not materially improve efficiency/stability under matched budgets, record the result and remove Fibonacci as a privileged design prior. The broader developmental thesis is unaffected.

DECISION
Preserve Fibonacci as a bounded experimental prior, not a core architectural axiom.
Canonical P0 remains unchanged.

NEXT EXPERIMENT
Complete DG1A-P0 baseline and regeneration-control evidence first. Then implement FIB1-R as the cheapest discriminating Fibonacci experiment before topology or module-sizing work.