TITLE: DG-1A-P0-STAB-18-R1 — Temporal Wound-Signal Feasibility Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / CODE-INFORMED PRE-EXECUTION AUDIT — NOT A CANDIDATE RESULT
TRACK: DG-1A
PARENT_CANDIDATE: CAUSAL-LATENT-DROPOUT25-PRUNE-T16-DOMAINSEP

PURPOSE
Test whether the current bounded local NCA architecture can, in principle, distinguish acute internal injury from ordinary stable organism boundaries without a privileged runtime damage flag or target geometry.

THIS RECORD DOES NOT
- alter or execute STAB-18-R1;
- select a STAB-19 candidate;
- reserve a hidden channel;
- change the NCA update rule;
- establish that the learned Yggdrasil state already contains wound memory;
- authorize a repair coefficient, decay rate, threshold, or signal duration.

FROZEN ARCHITECTURAL CONTEXT
The current NCA:
- state channels = 16;
- visible channels = 0..3;
- LIFE4 = hidden channel 4;
- remaining hidden channels = 5..15;
- local perception = identity + Sobel-x + Sobel-y over each channel;
- Moore-neighborhood liveness through 3x3 max pooling;
- shared local update rule;
- stochastic update fire rate = 0.5;
- no privileged global runtime state.

The hidden channels are recurrent cell state and can therefore, in principle, encode temporal memory.

LITERATURE MOTIVATION
Recent GNCA work reports:
- hidden channels functioning as structured internal state rather than disposable noise;
- mature spatially coherent cell-type organization;
- damage-driven latent-state reorganization and distributed repair information flow.

Biological wound repair likewise commonly begins with rapid local transient signals such as calcium, ROS, ATP, and bioelectric perturbations that distinguish an acute state change from stable tissue geometry.

These observations motivate a temporal local wound-signal hypothesis but do not establish it for Yggdrasil.

SYNTHETIC BODY FAMILY
40x40 lattice.
Filled disk organisms centered at lattice coordinate 20,20.
Radii chosen to span the frozen viable occupancy band:

radius | active cells
6      | 113
8      | 197
10     | 317
12     | 441
14     | 613
15     | 709
16     | 797

The canonical center lesion geometry was approximated exactly as the existing center_lesion contract:
- lesion height = 35% of live bounding-box height;
- lesion width = 35% of live bounding-box width;
- centered inside the current live bounding box.

TEMPORAL DETECTOR TOY
Each surviving cell is assumed to retain one-step memory of the previous number of live cells in its 3x3 neighborhood.

PreviousSupport = prior 3x3 hard-life count
CurrentSupport = current 3x3 hard-life count
SupportLoss = PreviousSupport - CurrentSupport

Diagnostic trigger:
SupportLoss >= 2

This is NOT a proposed exact runtime formula.
It is an information-feasibility test:
does temporal local state contain enough information to discriminate acute lesion boundaries?

CLEAN LESION DETECTION
A wound-boundary cell is a surviving cell whose 3x3 neighborhood touches at least one lesion-removed cell.

radius | active | removed | wound-boundary | triggered | boundary recall
6      | 113    | 25      | 24             | 20        | 83.33%
8      | 197    | 36      | 28             | 24        | 85.71%
10     | 317    | 49      | 32             | 28        | 87.50%
12     | 441    | 81      | 40             | 36        | 90.00%
14     | 613    | 100     | 44             | 40        | 90.91%
15     | 709    | 121     | 48             | 44        | 91.67%
16     | 797    | 144     | 52             | 48        | 92.31%

For this clean synthetic family:
- every triggered survivor is on the wound boundary;
- diagnostic precision = 100%.

The trigger therefore identifies a compact local wound ring rather than the whole organism.

MAINTENANCE-NOISE CONTROL
To test whether ordinary local loss could swamp the signal, a separate synthetic control independently removed 1% of active cells from an otherwise undamaged disk before evaluating the same two-neighbor support-loss trigger.

5000 deterministic trials per radius.

radius | lesion triggers | random-turnover false triggers mean | false-trigger p95 | lesion/mean-noise ratio
6      | 20              | 0.2314                              | 2                 | 86.43x
8      | 24              | 0.4252                              | 3                 | 56.44x
10     | 28              | 0.7062                              | 4                 | 39.65x
12     | 36              | 1.0520                              | 5                 | 34.22x
14     | 40              | 1.4892                              | 6                 | 26.86x
15     | 44              | 1.7174                              | 6                 | 25.62x
16     | 48              | 1.9288                              | 7                 | 24.89x

Interpretation:
Under this simplified turnover model, an acute canonical lesion produces a local temporal signal far larger than ordinary 1% stochastic cell loss.

This is not a measured false-positive rate for the trained NCA, whose natural LIFE4 turnover is presently unknown.

STATIC LOCAL-STATE AMBIGUITY CONTROL
A key question is whether temporal memory is actually necessary.

For the 709-cell disk after central lesion:
- ordinary outer-boundary surviving cells = 116;
- wound-boundary surviving cells = 48;
- unique binary 3x3 LIFE4 patterns at outer boundary = 36;
- unique binary 3x3 LIFE4 patterns at wound boundary = 16;
- all 16 wound-boundary pattern classes also occur at the ordinary outer boundary.

Therefore:
100% of wound-boundary cells have a current binary 3x3 LIFE4 pattern that is also observed somewhere on the normal exterior boundary.

This establishes an information limitation for LIFE4-only memoryless local wound detection:
current local alive/dead geometry alone cannot universally distinguish an acute internal boundary from a stable external boundary.

The full NCA state may contain visible/hidden positional or cell-type context that breaks this ambiguity.
The result does NOT claim current-state wound detection is impossible using all channels.

It does show that temporal state change provides exactly the missing discriminator in the LIFE4-only case.

PROPAGATION-DISTANCE AUDIT
Using an 8-neighbor graph over the synthetic original body, distance was measured from the initial surviving wound boundary.

radius | active | maximum distance to any body cell | maximum depth into removed region
6      | 113    | 3                                 | 3
8      | 197    | 5                                 | 3
10     | 317    | 6                                 | 4
12     | 441    | 7                                 | 5
14     | 613    | 9                                 | 5
15     | 709    | 9                                 | 6
16     | 797    | 10                                | 6

Consequences:
- a signal capable of moving one Moore-neighborhood cell per NCA step can reach every cell of these bounded disk organisms within at most 10 steps;
- it can reach the deepest point of the canonical central wound within at most 6 steps.

This is comfortably inside:
- the existing ATTRACT auxiliary horizon of 16 steps;
- the normal training rollout range of 64..96 steps.

Thus the current local receptive field does not create a fundamental horizon barrier for a wound signal at this morphology scale.

MEMORY-PERSISTENCE DIAGNOSTIC
As an information-timescale toy only, suppose stored local support memory relaxes toward the new current support with update fraction beta per step.

For an initial two-neighbor support loss, time above a one-neighbor-equivalent signal threshold is approximately:
beta = 0.20 -> 4 steps
beta = 0.15 -> 5 steps
beta = 0.10 -> 7 steps
beta = 0.08 -> 9 steps
beta = 0.05 -> 14 steps
beta = 0.03 -> 23 steps

For an initial three-neighbor loss:
beta = 0.20 -> 5 steps
beta = 0.15 -> 7 steps
beta = 0.10 -> 11 steps
beta = 0.08 -> 14 steps
beta = 0.05 -> 22 steps
beta = 0.03 -> 37 steps

No beta or threshold is selected by this audit.

The diagnostic only demonstrates that a short-lived local memory trace can plausibly persist long enough to cover the 6-step lesion depth and, for moderate retention, the <=10-step organism-wide communication distance.

REPAIR-FOOTPRINT IMPLICATION
At near-STAB-16 occupancy:
- synthetic active cells = 709;
- canonical lesion removes 121;
- initial two-neighbor temporal detector activates 44 surviving wound-edge cells;
- deepest removed cell is six local steps from the initial wound boundary.

A repair mechanism therefore does not need to globally raise the LIFE4 floor for hundreds of cells.
A moving local recruitment frontier could, in principle, rebuild the lesion layer-by-layer from a compact wound-edge signal.

This is mechanistically distinct from FRONTIER-FLOOR-113:
- the floor is global-count conditioned;
- when total LIFE4 remains above 113 after lesion, it is silent;
- a temporal wound signal is state-change conditioned and can remain active even when the organism is globally viable.

TRAINING / RUNTIME AUTHORITY BOUNDARY
The existing training pipeline already knows when it applies a synthetic lesion.
A future experiment could use that intervention knowledge as teacher-only supervision while retaining a completely autonomous local NCA at inference.

However, such a design must prove that:
- no damage flag is inserted into runtime state;
- no target geometry is supplied at inference;
- the learned local rule responds to endogenous state patterns / memory;
- undamaged stable boundaries do not continuously trigger repair growth.

No such candidate is selected here.

POTENTIAL ARCHITECTURAL READING
The current evidence supports a three-mode resource-control decomposition:

1. MAINTENANCE
   economical, causally useful LIFE4 support.

2. WOUND DETECTION / REPAIR
   local temporal change creates a transient repair signal;
   useful LIFE4 recruitment can occur even while total LIFE4 remains above 113.

3. CONTRACTION
   once the transient signal disappears, causal/occupancy pressures return the substrate toward economical maintenance.

This resembles biological regeneration more closely than a permanently elevated global life floor:
damage generates a transient local signal rather than redefining normal homeostasis.

RELATION TO STAB-18-R1
Do not alter R1.

R1 must first establish whether maintenance-stage global causal pruning improves the surviving substrate.

If R1:
- improves occupancy/morphology but recovery remains recruitment-poor:
  temporal local wound signaling becomes a high-priority next seam.
- collapses useful morphology under prune pressure:
  solve causal-credit localization first.
- succeeds on recovery too:
  do not add wound memory; replicate the simpler result.

BOUNDARY OF EVIDENCE
This audit uses idealized binary disk geometry and explicit one-step support memory.
It does not demonstrate learned wound detection in the real trained NCA.
Real Yggdrasil phenotypes are irregular, continuous, stochastic, and use all state channels.
Natural maintenance turnover may exceed the 1% synthetic control.

The result is therefore:
FEASIBILITY + INFORMATION-STRUCTURE EVIDENCE,
not a candidate performance result.

PROVENANCE
evidence_class = SYNTHETIC_TEMPORAL_SIGNAL_AUDIT
canonical_scientific_execution = false
new_training_run = false
synthetic_random_seed_family = 20260918
