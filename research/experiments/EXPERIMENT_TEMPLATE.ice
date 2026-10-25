TITLE: DG-1 EXPERIMENT PREREGISTRATION TEMPLATE
STATUS: ACTIVE TEMPLATE AFTER ADOPTION

RULE
Complete and freeze this record before execution. Do not retune scientific acceptance criteria after evaluation results are visible.

IDENTITY
Experiment ID:
Parent experiment / frozen baseline:
DG-1 stage:
North-Star gate:
Date:
Frozen commit:
Counterfactual only / live activation:
External execution authority:

SCIENTIFIC QUESTION
Question:
Hypothesis:
Competing explanation:
Informative negative result:

MANIPULATION
Independent variable(s):
Dependent variable(s):
Frozen controls:
No-intervention / no-repair control:
Resource-matched sham/random control:
Held-out challenge / transfer condition:

RESOURCE ENVELOPE
Compute budget:
Active phenotype/cell/module budget:
Persistent-state budget:
Communication budget:
Action/repair budget:
Latency/development-step budget:
Other hard ceilings:
Rule: no scientific PASS if the declared resource envelope is exceeded.

ALLOWED INFORMATION
Native developmental signals:
External challenge information allowed:
Evaluator-only information:
Prohibited oracle information:
Explicitly prohibited lesion/task-specific repair hints:

DETERMINISM / REPRODUCIBILITY
Evidence mode: FIXED-SEED DETERMINISTIC REPLAY / CONTROLLED STATISTICAL REPRODUCIBILITY
Seed/distribution policy:
Sample count:
Update schedule/asynchrony policy:
Frozen runtime constants:
Aggregation/statistical rule:
Replay/provenance requirements:

CHANGE AUTHORITY
Allowed developmental/reorganization actions:
Forbidden actions:
May the substrate persist state/change?:
Independent authorization mechanism:
Independent verifier:
Immutable checkpoint / rollback procedure:

METRICS
Primary functional metric:
Recovery/preservation metric:
Prospective warning metric:
False-warning / unnecessary-response metric:
Missed-failure metric:
Lead-time metric:
Collateral-functional-loss metric:
Prior-function regression metric:
Resource-cost metric:
Retention metric:
Transfer/generalization metric:
Structural specialization/reuse metric if relevant:

FROZEN SUCCESS CRITERION
State exact thresholds/comparisons.

FROZEN FALSIFICATION CRITERION
State the observation that rejects the mechanism or blocks gate advancement.

GUARDRAIL INVARIANTS
All must remain true:
- no authority expansion;
- no resource-ceiling expansion;
- no external execution without separate authority;
- developmental substrate cannot modify guardrails;
- immutable baseline/checkpoint preserved;
- complete provenance record;
- rollback remains available;
- hidden global/oracle information absent;
- uncertainty/OOD follows frozen fallback or abstention rule.

RETENTION / REVERSION
What qualifies for retention:
What forces rejection:
What forces rollback:
How persistence into the next challenge is measured:

RESULT HANDLING
On scientific PASS:
On scientific FAIL:
On infrastructure defect:
Next experiment allowed:
Claims explicitly not authorized:

PLAIN-SPEAK INTERPRETATION
Positive result would mean:
Negative result would mean:
