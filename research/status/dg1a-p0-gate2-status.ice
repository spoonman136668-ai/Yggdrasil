TITLE: DG-1A-P0 Gate 2 Status
DATE: 2026-09-17
STATUS: SANDBOX NUMERICAL GATE MET — COMMIT-BOUND CONFIRMATION OPEN
TRACK: DG-1A
CONFIDENCE: SUPPORTED FOR REPLICATED SANDBOX BEHAVIOR; UNKNOWN FOR CONFIRMATORY ACCEPTANCE

CURRENT BRANCH
dg1a-p0

CURRENT SCIENTIFIC STATE
P0 scaffold: implemented.
P0 training/evidence path: implemented.
Equivalent reconstructed regression surface: 42 tests green.
Single-seed exploratory regeneration: observed.
Five-seed 0.50 lesion family: inconclusive because only 3/5 matched pairs passed the frozen lesion-validity gate.
Damage calibration: complete; 0.60 selected mechanically.
Five-seed 0.60 lesion family: numerical support rule met in sandbox.
Commit-bound confirmatory reproduction: OPEN.
Full-grid 40 x 40 CPU cost feasibility: measured and acceptable for bounded exploratory work.

CALIBRATED P0 DAMAGE PROTOCOL
Center lesion: 0.60 x 0.60 of active bounding box.
RelativeDamageEffect minimum: 0.10.
ActiveCellRemovalFraction minimum: 0.10.
Do not lower thresholds post hoc.

GATE 2 SANDBOX RESULT
Valid matched pairs: 4 / 5.
Valid matched pairs favoring regeneration: 4 / 4.
Median DeltaRecovery: +1.0.
Growth-only bounded recovery on valid pairs: 0.0.
Regeneration bounded recovery on valid pairs: 1.0.
Numerical support rule: MET.
Confirmatory H-P0-3 status: NOT YET PROMOTED because execution was not commit-bound.

CONTROL FAILURE KNOWLEDGE
Growth-only consistently expands toward the full 20 x 20 grid after valid damage while morphology error worsens. This failure is retained as negative control evidence and must not be hidden or repaired by weakening the evaluation.

REGENERATION KNOWLEDGE
Maturity-gated regeneration produces stable recovery behavior across all tested seeds. Seed 2 remains excluded from the primary Gate-2 comparison because its calibrated 0.60 lesion produces RelativeDamageEffect 0.09603, below the frozen 0.10 criterion.

FULL-GRID FEASIBILITY
40 x 40 / batch 8 / hidden 128 / float32:
- 64-step forward+backward: 0.96223 s measured;
- 96-step forward+backward: 1.39644 s measured;
- observed max RSS at 96 steps: approximately 1.4 GB;
- update-rule parameters: 8,320.

BOUNDARIES
No DG-1B claim.
No cognitive regeneration claim.
No ancestor-inheritance claim.
No general intelligence claim.
No consumer-hardware scaling advantage claim.
No Fibonacci mechanism inside P0.

FIBONACCI TRACK
DG-1A-FIB1 is documented separately on branch dg1a-fib1-plan as a future matched repair-scheduling ablation.
It remains blocked from modifying the canonical P0 control until P0 closeout.

NEXT BOUNDED WORK
1. Commit-bound reproduction of the calibrated five-seed P0 gate when an authorized exact-revision execution path is available.
2. Bounded 40 x 40 seed-0 exploratory growth/regeneration bring-up.
3. Add deterministic resume/checkpoint state only if needed to preserve long home-hardware runs without altering training semantics.
4. Do not widen to DG-1B or FIB1 implementation until the P0 closeout decision is explicit.
