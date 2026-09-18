TITLE: DG-1A-P0-STAB-18-R1 — Synthetic Wound-Memory Repair Rollout Proof-of-Concept
DATE: 2026-09-18
STATUS: EXPLORATORY SYNTHETIC RECURRENT POC — NOT A YGGDRASIL CANDIDATE RESULT
TRACK: DG-1A
PARENT_CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Move beyond static wound-frontier classification and test whether the wound-memory representation can support an iterative LOCAL repair process that:
- recruits cells into an internal wound;
- does not expand an undamaged exterior boundary;
- generalizes to unseen body sizes and lesion sizes;
- exposes failure under weak maintenance perturbations rather than hiding it.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- implement this mechanism in Yggdrasil;
- select a STAB-19 candidate;
- authorize any trigger threshold, signal decay, classifier threshold, or memory rule;
- establish real NCA regeneration;
- claim that the hand-coded memory/signal propagation rule is biologically or computationally optimal.

RELATION TO PRIOR POC
The preceding actual-perception POC established that a small 6-feature -> 32-ReLU -> 1 local classifier can distinguish:
- dead wound frontier;
from
- ordinary exterior growth frontier

when given:
1. CurrentLife identity/Sobel-x/Sobel-y;
2. one hidden SupportMemory identity/Sobel-x/Sobel-y.

This recurrent POC freezes one such synthetic classifier and repeatedly applies its LOCAL decision to a changing damaged body.

CLASSIFIER TRAINING SPLIT
Training geometry deliberately excluded the canonical test combination.

Training radii:
6, 8, 10, 12, 14, 16

Training lesion fractions:
0.20, 0.25, 0.45, 0.50

Excluded from classifier fitting:
- radius 15;
- lesion fraction 0.35.

Network:
6 -> 32 -> ReLU -> 1

This remains smaller than Yggdrasil's existing 128-unit local update hidden width.

SYNTHETIC LOCAL STATE
Life:
binary occupancy.

SupportMemory:
pre-injury normalized 3x3 local support density retained by surviving cells.

Lesion:
zeros Life and SupportMemory in the destroyed region.

Candidate birth sites:
currently dead cells with at least one live Moore neighbor.

Classifier input:
actual Yggdrasil-style identity/Sobel perception of:
- CurrentLife;
- SupportMemory.

No target mask or global coordinate is supplied to the classifier.

EXPLORATORY MEMORY PROPAGATION RULE
The first recurrent toy propagated SupportMemory into newly repaired cells by taking the maximum local neighboring SupportMemory value.

This is a HAND-CODED diagnostic operator.
It is not present in Yggdrasil and is not proposed as the final mechanism.

The purpose is to determine whether local temporal context can sustain repair layer-by-layer after the originally surviving wound edge has been passed.

HELD-OUT CANONICAL GEOMETRY
Body:
radius 15 disk
709 cells

Lesion:
35% centered bounding-box lesion
121 removed body cells

Classifier never saw:
- radius 15 during training;
- lesion fraction 0.35 during training.

UNGATED REPAIR RESULT
Step 1:
- wound births: 40
- external births: 0

Step 2:
- wound births: 32
- external births: 0

Step 3:
- wound births: 24
- external births: 0

Step 4:
- wound births: 16
- external births: 0

Step 5:
- wound births: 8
- external births: 0

Step 6:
- births: 0

Final:
- 120 / 121 removed wound cells restored;
- repair fraction = 99.17%;
- external expansion = 0 cells;
- repair stopped autonomously under the fixed classifier once the stable exterior/wound geometry became non-recruiting.

The one unrepaired cell is a synthetic center-site edge case and was not patched or special-cased.

NOVEL-GEOMETRY ROLLOUT
The same frozen classifier and propagation rule were tested on body radii NEVER used for classifier training:
7, 9, 11, 13, 15

and lesion fractions:
0.30, 0.35, 0.40

These include lesion sizes also absent from classifier training.

15 held-out recurrent cases total.

Results:
- wound restoration fraction range: 96.0% .. 100%;
- external expansion: 0 cells in all 15 cases;
- repair termination: 3 .. 7 local recruitment steps.

Representative results:
radius 7, 30% lesion:
16 / 16 restored; 0 external; 3 steps.

radius 9, 35% lesion:
48 / 49 restored; 0 external; 4 steps.

radius 11, 35% lesion:
64 / 64 restored; 0 external; 5 steps.

radius 13, 40% lesion:
120 / 121 restored; 0 external; 6 steps.

radius 15, 40% lesion:
144 / 144 restored; 0 external; 7 steps.

STABLE UNDAMAGED CONTROL
Undamaged disks at radii 6 through 16 were presented to the same local classifier with their steady SupportMemory.

Every tested stable body produced:
0 exterior births.

This confirms that in the clean synthetic geometry, repair is not simply ordinary boundary expansion.

IMPORTANT NEGATIVE — RANDOM TURNOVER INSTABILITY
A stronger maintenance stress exposed a real defect.

Experiment:
- 709-cell undamaged body;
- independently drop 1% of body cells;
- retain survivor SupportMemory;
- use the same UNGATED iterative memory-propagation rule;
- 300 deterministic trials;
- up to 8 repair steps.

Result:
- mean repair of randomly dropped cells: approximately 15.84%;
- median repair fraction: approximately 14.29%;
- mean EXTERNAL expansion: 10.85 cells;
- 95th percentile external expansion: 45 cells;
- maximum observed external expansion: 88 cells.

This is a substantive failure of the ungated hand-coded mechanism.

Weak local disturbances can occasionally bootstrap the propagated memory context into an outward-growth cascade.

Therefore:
TEMPORAL MEMORY ALONE IS NOT SUFFICIENT.

This negative is retained as first-class mechanistic evidence.

TWO-STAGE HYPOTHESIS
The failure suggests a control decomposition:

STAGE 1 — INJURY DETECTION
require a sufficiently strong acute local support-loss event before repair propagation is licensed.

STAGE 2 — REPAIR PROPAGATION
once licensed, temporal context guides recruitment into the wound.

This resembles the biological distinction between:
- ordinary homeostatic fluctuations;
and
- thresholded acute damage signaling.

EXPLORATORY STRONG-INJURY CONTROL
A second synthetic toy added an explicit transient RepairSignal.

Initial RepairSignal source:
surviving cells whose retained support memory exceeded current local support by at least a diagnostic threshold.

Signal:
- propagates locally;
- decays geometrically;
- only licenses classifier births near active signal.

This is still a hand-coded exploratory control, not a proposed Yggdrasil mechanism.

A small threshold comparison was used diagnostically:
support-loss trigger >=2 versus >=3.

This comparison MUST NOT be interpreted as candidate parameter selection.

HELD-OUT CANONICAL RESULT WITH STRONGER TRIGGER
Using the stronger diagnostic trigger:
- radius 15;
- 35% lesion;
- 121 cells removed;

result:
- 120 / 121 restored;
- 99.17% repair;
- zero external expansion;
- six repair steps.

The stronger trigger therefore preserved the clean canonical repair behavior.

HELD-OUT GEOMETRY WITH STRONGER TRIGGER
Across the same 15 unseen radius/fraction recurrent cases:
- restoration remained 96% .. 100%;
- external expansion remained zero in every case;
- repair completed in 3 .. 7 recruitment steps.

Thus the strong-injury gate did not destroy the synthetic lesion-repair capability in this family.

1% TURNOVER STRESS COMPARISON
1000 deterministic turnover trials on the 709-cell body.

Diagnostic trigger >=2:
- mean external expansion: 1.355 cells;
- trials with any external expansion: 37 / 1000;
- maximum external expansion: 53 cells.

Diagnostic trigger >=3:
- mean external expansion: 0.034 cells;
- 95th percentile: 0;
- 99th percentile: 0;
- trials with any external expansion: 1 / 1000;
- maximum rare-tail external expansion: 34 cells.

Interpretation:
a stronger acute-damage gate suppressed most weak-turnover amplification while preserving large-wound repair in this toy.

The remaining rare large-tail failure is important.
The synthetic mechanism is NOT robust enough to promote as an implementation.

WHY THE TWO-STAGE RESULT MATTERS
The prior architecture audit found that LIFE4 currently has:
- explicit baseline floor control;
- explicit upper occupancy control;
- explicit causal downward pressure;
but no explicit distinction between ordinary fluctuation and injury-triggered recruitment.

The recurrent toy independently arrives at the same structural requirement:

ordinary local state fluctuation
must NOT automatically imply
growth.

Instead:
acute damage evidence
licenses
temporary repair behavior.

This is qualitatively different from raising the global LIFE4 floor.

SIGNAL TIMESCALE
The exploratory propagated signal used decay 0.9.
Without new source input, an amplitude of 1 falls below 0.1 after approximately 22 steps.

This was not optimized and is not proposed as a candidate value.

It demonstrates only that:
- a transient hidden repair state can outlast the 3..7-step synthetic wound-filling phase;
- then disappear well inside the canonical 96-step recovery window.

RESOURCE / ARCHITECTURAL IMPLICATION
The synthetic mechanism conceptually uses:
1. a local support-memory quantity;
2. a transient injury/repair-state quantity.

Yggdrasil already has eleven hidden channels beyond LIFE4.
No state-width increase is inherently required for such roles.

However, future work should prefer emergent/shared hidden representation rather than hard-reserving named channels unless a preregistered experiment requires explicit observability.

BIOLOGICAL ANALOGY — NOT DESIGN AUTHORITY
Real tissues often separate:
- stable homeostasis;
- rapid wound detection;
- propagating repair signals;
- proliferation/migration;
- termination after restoration.

Calcium waves, ATP/ROS signals, and wound electric fields are examples of transient local signals associated with injury responses.

The analogy motivates state-dependent repair but does not dictate the NCA implementation.

RELATION TO STAB-18-R1
Do not alter R1.

The current experimental decision tree becomes sharper:

If R1 improves maintenance occupancy and morphology but recovery remains weak:
- do not raise the global floor;
- investigate a separately preregistered injury-gated local repair mechanism.

If R1 collapses useful morphology:
- solve causal-credit geometry first.

If R1 itself restores valid damage/recovery:
- do not add wound memory or repair signal;
- replicate the simpler mechanism.

NEXT RESEARCH QUESTION
Before any future repair candidate, measure real trained-NCA maintenance turnover and wound-edge latent dynamics.

The synthetic stress test shows why this is necessary:
a mechanism that looks perfect on a clean central lesion can fail under small ordinary perturbations.

A future candidate must therefore include a no-spurious-growth maintenance control, not only a lesion-repair metric.

BOUNDARY
This is a hand-composed synthetic local CA/classifier experiment.
It does not reproduce:
- the full Yggdrasil continuous state dynamics;
- stochastic 0.5 fire masks;
- recurrent gradient training;
- irregular learned morphologies;
- causal pruning;
- real hidden-state noise.

The result is valuable as architecture discrimination:
- local temporal wound information CAN support selective layer-by-layer repair;
- ungated propagation CAN destabilize maintenance;
- separating injury detection from repair propagation materially improves the toy.

PROVENANCE
evidence_class = EXPLORATORY_SYNTHETIC_RECURRENT_REPAIR_POC
canonical_scientific_execution = false
new_yggdrasil_training_run = false
classifier_hidden_width = 32
synthetic_seed_family = 20260918/20260919
