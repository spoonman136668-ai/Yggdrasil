TITLE: DG-1A-AR-H11 — Temporal Persistence vs Global Common-Mode Artifact
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE MULTI-TIMESCALE FILTER + HARD TIMESCALE-IDENTIFIABILITY NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh10-correlated-noise-false-structural-growth-audit.ice

PURPOSE
H10 showed that source-family diversity removes family-specific shared noise,
but fails when every source contains the same global common-mode artifact.

H11 asks:

Can time-separated evidence distinguish:

slow reusable developmental structure

from

a globally shared measurement artifact?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil developmental signals have this temporal spectrum;
- freeze a temporal-lag threshold;
- solve a persistent artifact that evolves on the same timescale as true structure;
- replace functional/causal validation;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

TRUE DEVELOPMENTAL SIGNAL
Six-dimensional observation space.

True reusable rank:
1.

Signal variance:
0.20.

True latent developmental coefficient follows AR(1):

rho_signal:
0.95.

Thus real reusable structure changes slowly.

GLOBAL ARTIFACT
Every sensor/view contains the same global isotropic artifact.

Global artifact variance per dimension:
0.045.

Independent per-view noise variance:
0.045.

Total marginal measurement-noise variance:
0.09.

Artifact temporal persistence is swept:

0.00
0.30
0.60
0.80
0.90
0.95
0.99.

MEASUREMENT VIEWS
Two different sources are used.

Because the artifact is global,
source provenance cannot remove it.

SAME-TIME CROSS-SOURCE ESTIMATOR
Estimate reusable structure from:

view_A(t)
x
view_C(t).

This is the H10 global-common-mode failure case.

LAG-1 ESTIMATOR
Use:

view_A(t)
x
view_C(t-1).

Instantaneous global artifacts should disappear if they do not persist in time.

ZERO-vs-LAG5 PERSISTENCE ESTIMATOR
First obtain same-time candidate directions.

For each direction compare:

lag-5 cross-time support

to

zero-lag cross-source support.

Exploratory persistence criterion:

lag5 / zero
>
0.50.

The threshold is synthetic and not frozen.

STRUCTURAL THRESHOLD
Maximum tested structural rank:
3.

Candidate eigenvalue threshold:
0.019 synthetic units.

Task evaluation uses:
3-view cue noise
+
per-active-basis cost 0.015.

PRIMARY CONFIRMATION
20 matched seeds per persistence condition for the final persistence-ratio sweep.

SAME-TIME RESULT
The same-time estimator fails at EVERY tested artifact timescale,
including completely white artifact:

artifact rho 0.00:
mean rank 3
loss ~0.13502

rho 0.30:
rank 3
loss ~0.13503

rho 0.60:
rank 3
loss ~0.13506

rho 0.80:
rank 3
loss ~0.13510

rho 0.90:
rank 3
loss ~0.13518

rho 0.95:
rank 3
loss ~0.13528

rho 0.99:
rank 3
loss ~0.13548.

Reason:
the artifact is shared at the same instant,
so same-time agreement treats it as reusable structure.

TRUE required rank remains:
1.

LAG-1 RESULT

artifact rho 0.00:
rank 1
loss ~0.04504

rho 0.30:
rank 1
loss ~0.04506

rho 0.60:
rank 3
loss ~0.13505

rho 0.80:
rank 3
loss ~0.13509

rho 0.90:
rank 3
loss ~0.13519

rho 0.95:
rank 3
loss ~0.13532

rho 0.99:
rank 3
loss ~0.13549.

PRIMARY LAG-1 POSITIVE
Time separation completely removes the global artifact when the artifact is:
instantaneous
or
weakly persistent.

But one-step temporal evidence is insufficient once the artifact itself persists.

ZERO / LAG-5 PERSISTENCE RESULT

artifact rho 0.00:
rank 1
loss 0.04504
false extra-rank growth 0%.

rho 0.30:
rank 1
loss 0.04505
false growth 0%.

rho 0.60:
rank 1
loss 0.04509
false growth 0%.

rho 0.80:
rank 1
loss 0.04516
false growth 0%.

rho 0.90:
rank 3
loss 0.13518
false growth 100%.

rho 0.95:
rank 3
loss 0.13528
false growth 100%.

rho 0.99:
rank 3
loss 0.13548
false growth 100%.

PRIMARY POSITIVE
A multi-timescale persistence check substantially expands the range of global artifacts that can be rejected.

Same-time:
fails immediately.

Lag-1:
works only for low persistence.

Zero-vs-lag5:
retains correct rank through artifact persistence 0.80 in this synthetic working point.

WHY IT WORKS
True developmental structure has:

rho_signal = 0.95.

A transient artifact has rapidly decaying temporal support.

Structural evidence can therefore ask:

DOES THIS APPARENT DIMENSION SURVIVE ACROSS THE TIMESCALE EXPECTED OF SLOW DEVELOPMENTAL MEMORY?

This is stronger than:

DO MULTIPLE SENSORS AGREE RIGHT NOW?

HARD NEGATIVE
When artifact persistence approaches the developmental signal timescale:

measurement statistics become insufficient.

At artifact rho 0.90:
the lag-5 artifact still retains enough temporal covariance to pass the exploratory persistence criterion.

At rho 0.95:
the artifact and true signal explicitly occupy the same AR(1) timescale.

No purely temporal persistence rule can reliably distinguish them in this benchmark.

Thus:

TEMPORAL PERSISTENCE
CAN CREATE INDEPENDENCE FROM FAST ARTIFACTS,

but

IT CANNOT MANUFACTURE IDENTIFIABILITY
WHEN SIGNAL AND ARTIFACT SHARE THE SAME TEMPORAL STATISTICS.

This is the temporal analogue of:

consensus cannot manufacture source independence.

STRUCTURAL EVIDENCE HIERARCHY
H8-H11 now produce a progressively stronger filter:

RAW VARIANCE
unsafe.

TWO-VIEW CROSS-COVARIANCE
safe only for independent noise.

CROSS-FAMILY COVARIANCE
rejects family-specific shared noise.

MULTI-TIMESCALE PERSISTENCE
rejects globally shared but faster-changing artifacts.

But if a global artifact is:
source-shared
and
temporally matched to true structure,

passive observation remains under-identified.

NEXT IDENTIFIABILITY SOURCE
The remaining candidate is:

FUNCTIONAL / CAUSAL CONSEQUENCE.

A real structural dimension should not merely:
repeat
and
persist.

Representing it should improve local functional consequence.

A persistent measurement artifact may look structurally real,
but allocating a basis direction to it should not causally improve the underlying task.

This motivates the next experiment.

RELATION TO S7-S9
S7-S9 established:

correlation is not causal value;
valid controls need action decoupling;
control trust must be reversible.

H11 reaches the same point from slow memory:

persistent observational structure
is not enough.

Structural growth eventually needs:
CAUSAL UTILITY CREDIT.

CURRENT STRUCTURAL-GROWTH CONFIDENCE

off-manifold residual

+

persistence

+

cross-source repeatability

+

source-family diversity

+

multi-timescale temporal support

+

permanent structural cost

+

eventually:
functional causal consequence

->

slow structural growth.

DECISION
AR-H11 is POSITIVE with a hard temporal-identifiability limit.

Supported synthetically:

- time-separated evidence removes instantaneous global common-mode artifacts;
- longer persistence tests reject more slowly changing artifacts;
- multi-timescale evidence is stronger than same-time agreement;
- temporally matched global artifacts remain indistinguishable from true slow structure by observation alone.

Not demonstrated:

- real Yggdrasil signal persistence;
- optimal lags;
- learned timescale selection;
- functional causal validation of candidate structural dimensions;
- robustness to non-AR artifacts.

NEXT
AR-H12 — FUNCTIONALLY GROUNDED STRUCTURAL GROWTH

Question:

Can a candidate slow basis direction be validated by whether temporarily expressing that direction causally improves local function?

Test two equally persistent candidates:

A.
true task-relevant developmental dimension.

B.
persistent global measurement artifact.

Both pass:
source agreement
and
temporal persistence.

Compare:

observational structural growth

vs

small randomized basis-expression microprobes
+
local consequence credit.

Desired:

true structural dimension
->
positive repeated causal utility
->
slow structural write.

persistent artifact
->
no causal improvement
->
no permanent growth.

This experiment remains synthetic until a real target-free local consequence signal exists.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
true_signal_rank = 1
true_signal_rho = 0.95
global_artifact_variance_per_dimension = 0.045
independent_noise_variance_per_view = 0.045
final_persistence_confirmation_seeds = 20
