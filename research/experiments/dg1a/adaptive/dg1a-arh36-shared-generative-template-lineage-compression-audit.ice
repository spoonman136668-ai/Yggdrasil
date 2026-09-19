TITLE: DG-1A-AR-H36 — Shared Generative Template / Lineage-Compression Scaling Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SHARED-GENERATIVE-COMPRESSION RESULT + FAMILY-MANIFOLD COLLISION LIMIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh35-nonstationary-lineage-retirement-regeneration-audit.ice

PURPOSE
H35 established that retired lineage capability can persist in compressed generative form rather than as a fully retained dormant instance.

H36 asks the scaling question:

CAN MANY RELATED RETIRED LINEAGES SHARE ONE COMPACT GENERATIVE BASIS

while retaining only a small lineage-specific residual/tombstone state?

The desired long-term pattern is:

RETIRED CAPABILITY COUNT
grows

while

PER-LINEAGE PERMANENT MEMORY
grows much more slowly.

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil lineage states lie on a low-rank manifold;
- freeze PCA/SVD as the generative mechanism;
- freeze rank = 3;
- authorize semantic lineage-family IDs;
- establish final storage units;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

PRIMARY RELATED-LINEAGE POPULATION
Lineages:
120.

Per-lineage state dimension:
12.

True shared latent generative rank:
3.

Lineage-specific residual noise SD:
0.08.

Retirement/template observation noise SD:
0.03.

Each lineage state is generated from:

3 shared latent coordinates

+
small lineage-specific residual.

No lineage semantic label is required for the single-family primary benchmark.

COMPARATORS

FULL TEMPLATE PER LINEAGE
Store all 12 state values per lineage.

Scalar-equivalent storage:

120 * 12
=
1440.

FAMILY MEAN ONLY
Store only one shared mean state.

This is maximally compressed
but loses lineage-specific generative identity.

LOW-RANK SHARED BASIS
Store:

shared 12-D mean

+
rank-R shared basis

+
R lineage coefficients per lineage.

Primary rank:

3.

Scalar-equivalent storage:

mean:
12

basis:
12 * 3
=
36

lineage coefficients:
120 * 3
=
360

total:
408.

This is:

71.7%

less scalar-equivalent storage than one full 12-D template per lineage.

PRIMARY CONFIRMATION
40 matched synthetic lineage populations.

MEAN-ONLY RECONSTRUCTION MSE

0.25105
SD:
0.01829.

RANK-2 SHARED BASIS

0.07135
SD:
0.00669.

RANK-3 SHARED BASIS

0.004831
SD:
0.000184.

RANK-4

0.004163
SD:
0.000150.

PRIMARY POSITIVE
The true rank-3 shared basis preserves almost all useful lineage variation while reducing permanent lineage-template storage by approximately:

71.7%.

The rank-2 over-compressed representation loses a large amount of lineage identity:

0.07135 MSE

vs

0.00483

at rank 3.

Thus:

SHARED COMPRESSION IS USEFUL

but

OVER-COMPRESSION CAUSES FUNCTION COLLISION.

RANK-4 RESULT
Rank 4 slightly lowers reconstruction error further in this synthetic population.

That extra dimension mostly captures additional lineage-specific residual variation.

This does NOT establish that rank 4 is preferable.

The structural cost/value tradeoff remains required.

SCALING RESULT
For one shared rank-3 family basis,
total scalar-equivalent storage is:

48
+
3N

for N retired lineages.

Full per-lineage templates require:

12N.

Thus asymptotic per-lineage storage tends toward:

3 scalars

instead of:

12.

At large N,
the shared representation approaches approximately:

75% lower per-lineage storage.

This is directly aligned with the north-star requirement:

capability count may grow faster than permanent detailed state.

OUT-OF-MANIFOLD LINEAGE STRESS
15% of lineages are given a novel component orthogonal to the learned family manifold.

Orthogonal novelty magnitude:

0.8 synthetic units.

60 matched populations.

RANK-3 RECONSTRUCTION

all lineages MSE:
0.01255.

in-family:
0.00509.

novel out-of-manifold:
0.05484.

PRIMARY NOVELTY NEGATIVE
A shared family template can become actively inadequate for a lineage outside its generative manifold.

This is the lineage-memory analogue of H7:

inherited low-rank memory should not assume it represents every future regime.

FIT RESIDUAL
Use reconstruction residual as a non-semantic model-fit signal.

Threshold:

95th percentile
of in-family residual
within the synthetic calibration population.

Novel-lineage detection:

true-positive:
100%.

in-family false-positive:
approximately 5.88%.

This is a diagnostic working point,
not a frozen threshold.

FIT-GATED FALLBACK
If a lineage is flagged as off-manifold,
do not force the shared family reconstruction.

Fallback to a generic/current-context reconstruction cue.

Synthetic fallback cue:

3 observations

with observation SD:
0.18.

RESULT

fit-gated overall MSE:
0.00596.

novel-lineage MSE:
0.01055.

This sharply improves novel-lineage reconstruction relative to forcing the stale family basis:

0.05484
->
0.01055.

PRIMARY FIT-GATING POSITIVE
A compressed family template should carry:

MODEL-FIT CONFIDENCE.

If a retired lineage no longer fits the shared generative manifold,
the system should reduce template authority and use a more generic/current-context reconstruction path.

SPARSE RESIDUAL TOMBSTONE
A separate diagnostic stores:

rank-3 coefficients

+
two largest lineage residual coordinates.

This reduces out-of-manifold novel-lineage error to:

0.02534

and total error to:

0.00619.

This is better than plain rank-3 compression,
but worse than the tested fit-gated generic fallback on strongly novel lineages.

Interpretation:

small lineage-specific residuals can help,
but they should not be treated as universal protection against manifold shift.

MULTI-FAMILY COLLISION STRESS
A harder population contains two unrelated lineage families.

Each family:

rank 3

in the same 12-D state space.

The two family subspaces are constructed approximately orthogonal.

Total lineages:
120.

60 per family.

No candidate receives a semantic family label in the fit-selection comparator.

60 matched populations.

ONE GLOBAL RANK-3 BASIS

reconstruction MSE:
0.10216
SD:
0.00890.

HARD NEGATIVE
A single rank-3 basis cannot represent two genuinely distinct rank-3 lineage families.

The failure is not optimization noise.

The representation is under-capacity.

GLOBAL RANK-6 BASIS

MSE:
0.003440
SD:
0.000159.

This restores sufficient total representational capacity.

TWO FAMILY RANK-3 BASES
Diagnostic oracle family assignment:

MSE:
0.004702.

FIT-SELECTED FAMILY BASIS
For each lineage,
evaluate reconstruction residual under both stored family bases.

Choose the lower-residual basis.

No semantic family label is supplied.

MSE:
0.004702.

Correct family-basis selection:
99.83%.

PRIMARY FAMILY-MANIFOLD RESULT
Shared generative compression is safe only among lineages that actually share reusable structure.

One compact global basis is not automatically preferable to:
several small compatible basis families.

The architecture must distinguish:

SHARED GENERATIVE STRUCTURE

from

FORCED REPRESENTATIONAL MERGING.

GENERAL PRINCIPLE
Yggdrasil should aim for:

SHARED TEMPLATE WHERE STRUCTURE IS ACTUALLY SHARED

+

SMALL LINEAGE-SPECIFIC COORDINATES

+

FIT CONFIDENCE

+

GENERIC FALLBACK WHEN OUT-OF-MANIFOLD.

Do not assume:

ONE TEMPLATE
for
ALL RETIRED CAPABILITIES.

CURRENT RETIRED-LINEAGE MEMORY HIERARCHY
ACTIVE / DORMANT INSTANCE

->
COMPRESSED LINEAGE TOMBSTONE

->
SHARED GENERATIVE FAMILY BASIS
+
small lineage coordinates

->
GENERIC DEVELOPMENTAL TEMPLATE

->
no lineage-specific retained state.

Retirement depth and representation should depend on:

expected future value
+
recurrence urgency
+
manifold fit
+
storage price.

RELATION TO H7
H7 showed:
a small shared manifold can preserve multiple recurring priors,
but off-manifold regimes require fit gating.

H36 shows the same principle at lineage scale.

RELATION TO H35
H35 established:
instance memory can be deleted while generative capability survives.

H36 adds:
the generative memory itself can be shared across related lineages.

This allows:
retired capability count
to grow
without proportional full-template growth.

IMPORTANT LIMITATION
The true shared rank is known only to the synthetic generator.

Real Yggdrasil must learn:
- how many generative basis directions are worth their cost;
- whether two lineages should share one basis;
- when a lineage is sufficiently off-manifold to require another representation.

Those are now the next clean questions.

DECISION
AR-H36 is POSITIVE WITH A FAMILY-MANIFOLD COLLISION LIMIT.

Supported synthetically:

- many related retired lineages can share one compact generative basis;
- rank-3 compression reduces scalar-equivalent template storage by ~71.7% in the primary population;
- over-compression causes severe reconstruction error;
- out-of-manifold lineages require model-fit confidence and fallback;
- one global low-rank basis can catastrophically merge unrelated lineage families;
- multiple compact family bases can preserve distinct regenerative capabilities;
- family-basis selection can be driven by reconstruction fit rather than semantic lineage labels.

Not demonstrated:

- real Yggdrasil lineage manifolds;
- learned basis-family count;
- basis mutation across generations;
- online merge/split of template families;
- hardware-level memory savings;
- corruption resistance of shared templates.

NEXT CLEAN QUESTION
AR-H37 — ADAPTIVE GENERATIVE-FAMILY MERGE / SPLIT UNDER MEMORY PRESSURE

Question:

Can the organism decide when two retired-lineage template families should:

MERGE
to save permanent memory

or

SPLIT
because forced sharing causes regenerative interference?

Compare:

A.
one permanent template family per lineage cluster;

B.
global forced merge;

C.
memory-price-aware merge using held-out reconstruction / functional loss;

D.
automatic split when fit residual persists;

E.
family proliferation under noisy novelty.

Desired:

shared structure
->
merge and compress.

distinct structure
->
retain separate basis families.

transient noise
->
do not create permanent new family.

This should connect:

H36 lineage compression

with

H8-H15 structural growth / pruning

and

H26 resource pricing.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_lineages = 120
state_dimensions = 12
true_family_rank = 3
primary_confirmation_seeds = 40
novelty_stress_seeds = 60
multifamily_stress_seeds = 60
rank3_storage_scalar_equivalent = 408
full_template_storage_scalar_equivalent = 1440
