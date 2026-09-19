TITLE: DG-1A-AR-H39 — In-Manifold Slow Template Poisoning / Versioned Promotion Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SHADOW-PROMOTION RESULT + LEGITIMATE-DRIFT LATENCY TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh38-shared-template-update-poisoning-audit.ice

PURPOSE
H38 showed that large off-manifold lineage corruption can be quarantined using fit residuals,
but explicitly left open the harder case:

WHAT IF A BAD UPDATE STAYS INSIDE THE CURRENT FAMILY MANIFOLD?

Such an update can pass ordinary fit checks
while slowly biasing shared generative memory used by many retired lineages.

H39 tests:

LIVE IMMEDIATE TEMPLATE UPDATE

vs

SHADOW CANDIDATE VERSION
+
TRUSTED CANARY VALIDATION
+
BOUNDED PROMOTION.

BOUNDARY
This is synthetic.

It does not:
- freeze a production versioning protocol;
- prove current Yggdrasil has trusted recurrence canaries;
- establish cryptographic integrity;
- freeze promotion cadence or thresholds;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

REPRESENTATION
The family basis is assumed already learned.

The focused poisoning target is the shared generative coefficient prior / family center.

Latent coefficient dimensions:
3.

Clean family mean:
[0,0,0].

Within-family coefficient variance:
1 per dimension.

Because the poison remains inside the current basis,
ordinary reconstruction residual remains small.

Thus:
H38-style off-manifold rejection cannot detect it.

UPDATE STREAM
120 update blocks.

100 lineage updates per block.

Primary in-manifold poison:

+0.8 shift

along the first family coefficient dimension.

The poison is present in the update stream
but NOT in an independent trusted recurrence/functional canary stream.

This models:
- biased lineage observations;
- stale systematic coefficient updates;
- compromised local state that still looks geometrically in-family.

COMPARATORS

NAIVE LIVE UPDATE
Update the live shared family prior immediately after every block.

EMA rate:
0.08.

SHADOW VERSION
Maintain:

LIVE TEMPLATE

and

SHADOW CANDIDATE.

Incoming updates modify only the shadow.

Every:
5 blocks

evaluate live vs shadow on:

240 independent trusted canary lineage samples.

Promote shadow only if its canary reconstruction loss improves over live by more than:

0.002 synthetic loss units.

If validation fails:
discard/rebase the shadow to the current live template.

PRIMARY POISON CONFIRMATION
100 matched seeds.

NAIVE LIVE UPDATE

final excess family-center error:
0.21375

SD:
0.01078.

peak excess error:
0.231995.

SHADOW / CANARY PROMOTION

final excess error:
0.00552

SD:
0.01018.

median:
0.

95th percentile:
approximately 0.02649.

mean candidate promotions:
0.23
over the full 120-block poison stream.

mean rejected candidate validations:
23.77.

PRIMARY POSITIVE
The in-manifold poison passes ordinary family fit,
but fails independent recurrence/canary validation.

Immediate live updating accumulates a large shared bias.

Shadow promotion prevents that bias from entering the live family template in almost all tested runs.

Thus:

FIT TO CURRENT MANIFOLD
IS NOT
SUFFICIENT TEMPLATE-WRITE AUTHORITY.

A candidate shared-template update should prove itself against evidence that did not generate the update.

SHARED-MEMORY LEVERAGE RESULT
The point of versioning is not only local safety.

A family template may support many retired lineages.

Therefore one biased update stream can create:

MULTI-LINEAGE REGENERATIVE CORRUPTION.

The live template should be harder to mutate than one lineage's provisional state.

LEGITIMATE SLOW-DRIFT STRESS
Protection must not freeze real family evolution.

The true family coefficient mean now changes gradually.

Schedule:

blocks 0..19:
mean 0.

blocks 20..79:
linearly shifts first coefficient from:
0
to
0.8.

blocks 80..139:
stays at:
0.8.

Both:
update stream
and
trusted canary stream

reflect the legitimate new family state.

100 matched seeds.

NAIVE LIVE UPDATE

final excess mean error:
0.000424.

late stable-window error:
0.000485.

peak drift-period error:
0.01066.

SHADOW / CANARY VERSION

final excess error:
0.000833.

late stable-window error:
0.001283.

peak drift-period error:
0.01910.

Mean successful promotions:
13.26.

First post-drift-start promotion:

mean latency:
11.9 blocks.

median:
10 blocks.

5th–95th percentile:
approximately 5..15 blocks.

PRIMARY DRIFT POSITIVE
Versioned promotion does not permanently freeze legitimate family evolution.

When:
the update stream
and
independent canary evidence

both support the new family state,
candidate versions repeatedly promote.

PRIMARY DRIFT COST
The safety mechanism tracks legitimate drift more slowly than immediate live updating.

Late stable error remains small,
but transient drift error is higher:

peak:
0.01910
vs
0.01066.

Thus:

SHARED-TEMPLATE SAFETY
HAS A REAL ADAPTATION-LATENCY COST.

This is the same stability/plasticity tradeoff seen throughout Yggdrasil.

PROMOTION PRINCIPLE
A safe shared generative template should distinguish:

PROVISIONAL CHANGE

from

LIVE FAMILY AUTHORITY.

Incoming updates first create:

CANDIDATE TEMPLATE STATE.

Candidate state becomes live only after:

independent validation
+
sufficient improvement
+
bounded persistence.

This is analogous to:
H12 structural candidate validation;
H14 nomination vs permanent authority;
H25 capability state vs current authority.

ROLLBACK INTERPRETATION
Because the old live version remains intact during shadow evaluation,
failed candidate updates naturally roll back by:

discarding the shadow.

No reverse learning is required.

This is important when template updates affect many retired capabilities.

RELATION TO H38
H38 protects against:

OFF-MANIFOLD CORRUPTION

using:
fit gating
+
quarantine.

H39 protects against:

IN-MANIFOLD BIAS

using:
versioning
+
independent validation.

The two defenses address different attack/failure geometries.

CURRENT SHARED-TEMPLATE WRITE PIPELINE
LINEAGE UPDATE

->
CURRENT-FAMILY FIT CHECK.

IF OFF-MANIFOLD:

quarantine/cohort analysis
per H38.

IF IN-MANIFOLD:

update SHADOW family version,
not live template.

Then:

INDEPENDENT RECURRENCE / FUNCTIONAL CANARY

+
improvement margin
+
persistence

->

PROMOTE SHADOW
or
ROLL BACK.

GENERAL PRINCIPLE
SHARED STATE SHOULD HAVE
LOWER WRITE AUTHORITY
THAN LOCAL PROVISIONAL STATE.

The more capabilities a state influences,
the stronger the evidence required to rewrite it.

IMPORTANT LIMITATION
H39 assumes the canary stream is trustworthy and sufficiently independent from the update stream.

If the canary is:
- copied from the same corrupted source;
- globally confounded;
- stale;
- or itself compromised,

versioned promotion can still accept a bad candidate.

This is now the next clean failure.

DECISION
AR-H39 is POSITIVE WITH A LEGITIMATE-DRIFT LATENCY TRADEOFF.

Supported synthetically:

- in-manifold poisoning can evade residual-fit defenses;
- immediate live template updates accumulate large shared bias;
- shadow candidate versions plus independent validation strongly suppress that bias;
- failed candidate versions can be discarded without damaging live memory;
- legitimate slow family drift still promotes through the versioned path;
- safety introduces measurable adaptation latency.

Not demonstrated:

- real independent Yggdrasil canary source;
- provenance-safe validation;
- optimal promotion interval;
- multi-version distributed agreement;
- rollback under already-used bad versions;
- resistance when both update and validation evidence share corruption.

NEXT CLEAN QUESTION
AR-H40 — CANARY PROVENANCE / CORRELATED VALIDATION FAILURE

Question:

What happens when the template-update stream
and
the promotion canary

share the same corruption source?

Compare:

A.
single canary copied from update provenance;

B.
independent canary family;

C.
multiple provenance-diverse canaries;

D.
one corrupted canary among several;

E.
global common-mode corruption affecting all validation channels.

Desired:

candidate promotion confidence should depend on:

EFFECTIVE INDEPENDENT VALIDATION SOURCES

not:

raw number of agreeing canaries.

This should reuse the source-diversity principles from:
H10
H18
S8.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
coefficient_dimensions = 3
poison_blocks = 120
updates_per_block = 100
poison_shift = 0.8
shadow_alpha = 0.08
validation_interval_blocks = 5
canary_samples_per_validation = 240
poison_confirmation_seeds = 100
legitimate_drift_seeds = 100
