TITLE: DG-1A-AR-H7 — Bounded Multi-Regime Reconsolidation / Interference Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE-BUT-CAPACITY-LIMITED MULTI-REGIME MEMORY AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh6-stale-prior-suppression-slow-erase-audit.ice

PURPOSE
H5 established persistence-gated slow write.

H6 established that:
- fast suppression of inherited expression;
- slow rewrite of inherited state;

should operate on different timescales.

H7 asks the next distinct question:

Can a VERY SMALL slow-state budget preserve reusable developmental structure from multiple recurring regimes without:
- semantic regime IDs;
- one explicit memory slot per environment;
- unbounded state growth;
- or catastrophic overwrite?

BOUNDARY
This is synthetic.

It does not:
- implement a real Yggdrasil micro-genome;
- prove current Yggdrasil local signals lie on a low-dimensional memory manifold;
- freeze PCA/Oja/Sanger learning rules;
- authorize one prototype per regime;
- add semantic regime labels;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CORE HYPOTHESIS
Multiple recurring developmental priors may be compressible when they share a low-dimensional structure.

Instead of storing:

A SLOT FOR A
A SLOT FOR B
A SLOT FOR C

store:

ONE SLOW CENTER
+
A VERY SMALL SHARED BASIS.

Current local evidence selects a point on that shared developmental manifold.

This is closer to:
COMPOSITIONAL DEVELOPMENTAL BIAS

than:
episodic regime lookup.

REGIMES
Four-dimensional synthetic developmental optima.

A:
[0.25, 0.45, 0.25, 0.35]

B:
[0.20, 0.25, 0.80, 0.15]

C:
[0.65, 0.55, 0.30, 0.65]

The first three means necessarily lie in an affine subspace of rank <= 2.

A fourth stress regime D is deliberately given a component orthogonal to the A/B/C affine plane.

Primary D:
approximately

[0.32093, 0.16510, 0.40949, 0.53493]

Its orthogonal displacement magnitude is:
0.30 synthetic units.

OBSERVATION NOISE
Per local observation:

sigma = 0.16

All memory mechanisms see the same unlabeled noisy stream.

No mechanism receives:
- A/B/C/D identity;
- transition label;
- regime duration;
- semantic event type.

TRAINING STREAMS

THREE-REGIME STREAM:

A
B
A
C
B
A
C

repeated 18 times.

FOUR-REGIME STRESS STREAM:

A
B
A
C
B
A
D
C
B
A
D

repeated 18 times.

Each dwell is randomly varied from:
50 to 110 observations.

CONFIRMATION
16 matched seeds for the primary three-regime and four-regime comparisons.

RETRIEVAL CUE
At recall / developmental turnover,
the organism receives a short current local cue:

3 noisy observations
averaged together.

The cue is not a regime ID.

It is current local evidence.

The slow memory may bias or denoise that evidence.

COMPARATORS

RAW CUE
Use the short current cue directly.

This is the no-inherited-memory baseline.

SINGLE VECTOR
Maintain one slowly moving inherited vector.

No regime IDs.

This is the simplest slow-prior memory.

TWO PROTOTYPES
Maintain two unlabeled online centroids.

Current cue selects the nearest centroid.

This is bounded,
but still slot-like.

It cannot allocate one slot to every regime.

RANK-2 SHARED MANIFOLD
Maintain online:

- one 4D slow center;
- two 4D basis directions.

The basis is learned from the unlabeled stream using a bounded Sanger/Oja-style subspace update.

At recall:

prior =
center
+
projection of current cue onto the learned rank-2 subspace.

No regime ID exists.

State budget:

4 center scalars
+
8 basis scalars

plus minimal learning bookkeeping.

RANK-3 CAPACITY CONTROL
Same mechanism with three basis directions.

This tests whether failures of rank 2 are genuinely capacity related.

RESIDUAL / CONFIDENCE-GATED RANK-2
H6 says inherited structure should bias current behavior,
not override strong contradictory evidence.

Therefore H7 also tests a rank-2 prior whose influence is reduced by:

1.
OFF-MANIFOLD RESIDUAL

and

2.
AMOUNT OF CURRENT EVIDENCE.

Maintain one scalar EMA of rank-2 reconstruction residual.

For current cue:

projection_residual =
|| cue - rank2_projection ||^2

Exploratory memory weight:

w =
exp(
  - projection_residual
  /
  (2 * residual_ema)
)
/
(
  1 + 0.2 * (cue_count - 1)
)

Then:

final_prior =
cue
+
w * (rank2_projection - cue)

Thus memory influence is strongest when:
- current evidence is sparse;
- current cue lies close to the learned developmental manifold.

It weakens when:
- current evidence becomes strong;
- current cue lies off-manifold.

These constants are synthetic discriminating values only.

Do not freeze them for Yggdrasil.

PRIMARY RESULT — THREE RECURRING REGIMES
Cue count:
3

Mean MSE across A/B/C,
16 matched seeds.

RAW CUE:
0.007815
std:
0.000091

SINGLE VECTOR:
0.040396
std:
0.000305

TWO PROTOTYPES:
0.018702
std:
0.002584

RANK-2:
0.004156
std:
0.000871

RESIDUAL-GATED RANK-2:
0.004894
std:
0.000313

RANK-3:
0.005887
std:
0.000127

PRIMARY POSITIVE
A bounded rank-2 shared developmental manifold preserves all three recurring synthetic priors far better than:
- one slow vector;
- two slot-like prototypes;
- or raw short-horizon evidence.

Relative to raw cue:

rank-2 reduces mean error by approximately:
46.8%.

WHY RANK-2 BEATS RANK-3 HERE
The A/B/C means occupy an affine rank-2 structure.

Rank-2 preserves the regime manifold while rejecting one additional noisy dimension.

Rank-3 admits more observation noise.

Thus:

MORE MEMORY DIMENSIONS
IS NOT AUTOMATICALLY BETTER.

The useful capacity is:
ENOUGH TO REPRESENT REUSABLE STRUCTURE
BUT NOT SO MUCH THAT NOISE IS PASSED THROUGH.

IMPORTANT NEGATIVE — SINGLE VECTOR
One slow vector cannot represent recurring separated regimes.

The stream causes continual compromise / reconsolidation.

Mean error:
0.040396

which is over five times the raw-cue error.

Therefore:

SLOW MEMORY
IS NOT USEFUL MERELY BECAUSE IT IS SLOW.

Representational geometry matters.

IMPORTANT NEGATIVE — TWO PROTOTYPES
Two unlabeled prototypes cannot reliably preserve three recurring modes.

Mean error:
0.018702.

In the primary run family,
one regime is commonly merged with another cluster and becomes poorly reconstructed.

This is a bounded-slot capacity failure.

FOURTH-REGIME CAPACITY STRESS
Introduce D with an explicit component outside the A/B/C rank-2 plane.

Mean MSE across A/B/C/D.

RAW CUE:
0.007855
std:
0.000073

SINGLE VECTOR:
0.034667
std:
0.000162

TWO PROTOTYPES:
0.020581
std:
0.001315

UNGATED RANK-2:
0.008371
std:
0.000320

RESIDUAL-GATED RANK-2:
0.006169
std:
0.000121

RANK-3:
0.005932
std:
0.000088

CAPACITY NEGATIVE
The ungated rank-2 prior becomes slightly WORSE than raw current evidence once the new regime contains enough off-manifold structure.

Relative to raw:

rank-2 is approximately:
6.6% worse.

This is the key H7 failure mode.

A compact inherited manifold can become actively harmful when it is treated as more complete than it really is.

RANK-3 CAPACITY CONTROL
Adding one more basis direction restores representational capacity.

Rank-3:
0.005932

which is approximately:
24.5% better than raw cue.

This confirms that the rank-2 failure is primarily a capacity / geometry mismatch rather than merely an optimization failure.

RESIDUAL-GATED RANK-2
Without increasing rank,
the residual/confidence gate reduces four-regime mean error to:

0.006169

approximately:
21.5% better than raw cue.

Thus:
a small memory can remain useful beyond its exact representational capacity
IF
it can recognize when current evidence does not fit its inherited manifold.

PER-REGIME FOUR-REGIME RESULT

RAW:

A:
0.008018

B:
0.007108

C:
0.008317

D:
0.007976

UNGATED RANK-2:

A:
0.004846

B:
0.004707

C:
0.008235

D:
0.015696

The D failure is explicit.

The low-rank prior strongly helps familiar in-manifold structure,
but badly misprojects the novel off-manifold regime.

RESIDUAL-GATED RANK-2:

A:
0.005064

B:
0.004716

C:
0.006523

D:
0.008372

The gate sacrifices some ideal in-manifold compression
but prevents the large D failure.

OFF-MANIFOLD DISTANCE SWEEP
A separate 8-seed stress varies only D's orthogonal displacement from the A/B/C plane.

Cue count:
3.

ORTHOGONAL DISPLACEMENT = 0.0

RAW:
0.007970

RANK-2:
0.004024

GATED RANK-2:
0.004948

DISPLACEMENT = 0.1

RAW:
0.007958

RANK-2:
0.004482

GATED:
0.005116

DISPLACEMENT = 0.2

RAW:
0.007920

RANK-2:
0.005935

GATED:
0.005569

DISPLACEMENT = 0.3

RAW:
0.007852

RANK-2:
0.008344

GATED:
0.006185

DISPLACEMENT = 0.4

RAW:
0.007785

RANK-2:
0.010974

GATED:
0.006836

PRIMARY CAPACITY PRINCIPLE
As the new regime moves farther outside the inherited manifold:

UNGATED MEMORY
crosses from:
useful
to
harmful.

RESIDUAL-GATED MEMORY
degrades much more gracefully.

This yields a direct developmental-memory rule:

INHERITED STRUCTURE SHOULD CARRY A MODEL-FIT CONFIDENCE.

Not only:

HOW STRONG IS THIS MEMORY?

but:

HOW WELL DOES CURRENT EVIDENCE FIT THE STRUCTURE THIS MEMORY CAN REPRESENT?

RELATION TO H3 / H6
H3:
current utility should override inherited bias.

H6:
stale inherited expression should be suppressible before slow memory is erased.

H7 adds:

STRUCTURAL MISFIT
is another reason to reduce inherited influence.

A slow prior may be:
- historically useful;
- still stored;
- not globally stale;

and yet:
not expressive enough for the current regime.

Therefore inherited expression trust should consider at least:

1.
local causal usefulness;

2.
stale-prior evidence;

3.
representation residual / off-manifold novelty;

4.
strength of current direct evidence.

CURRENT MEMORY STACK
FAST ROLE
current reversible function.

CURRENT EVIDENCE CONFIDENCE
how much local evidence is available now?

INHERITED MANIFOLD
compact shared developmental structure.

MANIFOLD-FIT CONFIDENCE
does current evidence fit what inherited structure can represent?

EXPRESSION TRUST
should inherited structure bias the phenotype now?

WRITE CONFIDENCE
has persistent useful adaptation earned slow storage?

STALE-PRIOR CONFIDENCE
has stored structure remained harmful long enough to rewrite?

SLOW RECONSOLIDATION
update the shared low-dimensional structure without allocating one permanent slot per regime.

IMPORTANT LIMITATION 1
The primary rank-2 test is favorable because three 4D regime means are intrinsically representable in an affine rank-2 manifold.

This is not evidence that real Yggdrasil regimes are low-rank.

That must be measured.

IMPORTANT LIMITATION 2
The Sanger/Oja-style learning rule is only a bounded synthetic learner.

No claim is made that it is the right biological or computational mechanism.

IMPORTANT LIMITATION 3
Current local cue observations still contain target-correlated synthetic information.

Real Yggdrasil target-free local semantic / causal credit remains unresolved.

IMPORTANT LIMITATION 4
The memory budget counted here is slow representational state,
not the full implementation cost of learning the basis.

Real resource accounting remains future work.

IMPORTANT LIMITATION 5
The current synthetic regimes are stationary within each dwell.

Drifting manifolds,
branching regimes,
and adversarial novelty are not solved.

DECISION
AR-H7 is POSITIVE-BUT-CAPACITY-LIMITED.

Supported synthetically:

- one slow vector is insufficient for multiple recurring developmental regimes;
- a tiny shared low-rank structure can preserve multiple priors without semantic regime IDs;
- bounded prototype slots scale poorly when regimes outnumber slots;
- correct low-rank capacity can denoise sparse current evidence;
- insufficient low-rank capacity can make inherited memory harmful;
- off-manifold residual can serve as a compact expression-trust signal;
- current evidence confidence should reduce reliance on inherited structure as direct evidence strengthens.

Not demonstrated:

- real Yggdrasil low-dimensional developmental manifold;
- real online manifold-fit signal;
- real target-free multi-regime memory;
- optimal rank;
- optimal memory budget;
- optimal residual gate;
- catastrophic-interference behavior over many more regimes;
- structural memory under active cell birth/death.

CLEAN SCIENTIFIC PAUSING POINT
H5 + H6 + H7 now form a coherent first-order inheritance sequence:

H5:
PERSISTENT USEFULNESS
->
SLOW WRITE.

H6:
CONTRADICTION
->
FAST EXPRESSION SUPPRESSION
->
SLOW REWRITE ONLY IF PERSISTENT.

H7:
MULTIPLE RECURRING PRIORS
->
SHARED BOUNDED STRUCTURE
+
MODEL-FIT CONFIDENCE
+
CURRENT-EVIDENCE CONFIDENCE.

Do not extend H7 merely by adding more basis ranks or more synthetic regimes without introducing a new scientific question.

NEXT HIGH-VALUE INHERITANCE QUESTION
A clean future H8 would be:

STRUCTURAL GROWTH / PRUNING UNDER A HARD MEMORY BUDGET.

Question:

Can the organism decide locally when one additional slow structural degree of freedom is worth its permanent resource cost,
and when an unused degree should be pruned?

This would connect inheritance directly to:
AR-U13 evidence budgets
and
AR-U14 value-of-information.

However:
the preferred next cross-lane experiment remains:

AR-U15 — LEARNED LOCAL VALUE-OF-INFORMATION

because U14 currently assumes known stake and known noise.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
state_dimensions = 4
primary_confirmation_seeds = 16
off_manifold_sweep_seeds = 8
observation_noise_sigma = 0.16
cue_observations = 3
rank2_center_scalars = 4
rank2_basis_scalars = 8
rank2_extra_fit_state = 1 residual_ema_scalar
