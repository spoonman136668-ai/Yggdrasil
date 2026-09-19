TITLE: DG-1A-AR-H38 — Shared Template Update Poisoning / Robust Family Memory Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE ROBUST-UPDATE RESULT + STRICT-GATE FREEZE NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh37-adaptive-generative-family-merge-split-audit.ice

PURPOSE
H36-H37 established that many retired lineages can share one generative family basis
and that family count can merge/split under memory pressure.

Shared memory creates leverage:

ONE BAD LINEAGE UPDATE
CAN POTENTIALLY DAMAGE
MANY RETIRED CAPABILITIES.

H38 asks:

How should a shared generative template accept updates without:
- poisoning the family basis from isolated corrupt lineages;
- freezing legitimate family evolution;
- converting transient sensor failure into permanent regenerative damage?

BOUNDARY
This is synthetic.

It does not:
- freeze a production robust estimator;
- define an adversarial security model;
- prove real Yggdrasil corruption has this geometry;
- freeze a quarantine duration;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

BASE FAMILY
State dimensions:
12.

True shared rank:
3.

Base calibration lineages:
120.

Update lineages:
120.

Clean held-out lineages:
300.

Lineage residual SD:
0.08.

Template observation noise SD:
0.03.

BASE CLEAN-TEMPLATE HELD-OUT MSE
Across 60 matched seeds:

approximately:
0.005220.

CORRUPTION MODEL
A fraction of incoming lineage updates receive a strong component orthogonal to the current family basis.

Orthogonal corruption magnitude:
3.0 synthetic units.

This represents:
- broken local sensing;
- badly misfit lineage state;
- transient corrupted tombstone;
- or an update from a lineage that should not belong to this family.

The corrupt update is NOT semantically labeled.

COMPARATORS

NAIVE FAMILY REFIT
Refit the shared family basis using:
existing family memory
+
all incoming lineage updates.

FIT-GATED ADMISSION
Measure each incoming lineage's reconstruction residual under the current family basis.

Accept updates only if residual is below an exploratory:

99th-percentile
current-family fit threshold.

ROBUST RESIDUAL WEIGHTING
All updates remain visible,
but high-residual lineage updates receive sharply reduced statistical weight.

This is a diagnostic robust estimator,
not a frozen production formula.

PRIMARY CORRUPTION SWEEP
60 matched seeds per corruption fraction.

CORRUPTION = 0%

NAIVE:
held-out clean-family MSE
0.005122.

FIT-GATED:
0.005127.

ROBUST:
0.005151.

All three are effectively equivalent on clean updates.

CORRUPTION = 1%

NAIVE:
0.005183.

FIT-GATED:
0.005128.

ROBUST:
0.005152.

FIT-GATE corrupted-update admission:
0%.

CORRUPTION = 5%

NAIVE:
0.005468.

FIT-GATED:
0.005131.

ROBUST:
0.005155.

CORRUPTION = 10%

NAIVE:
0.005858.

FIT-GATED:
0.005133.

ROBUST:
0.005156.

CORRUPTION = 20%

NAIVE:
0.006751.

FIT-GATED:
0.005139.

ROBUST:
0.005160.

PRIMARY POISONING POSITIVE
Naive family memory becomes progressively damaged as corrupted lineage updates enter the shared basis.

At 20% corruption:

clean held-out reconstruction error rises from approximately:

0.00512
to
0.00675.

The fit-gated and robust estimators remain near:

0.00514
to
0.00516.

Thus:
isolated high-residual lineage updates should not receive immediate family-template write authority.

FIT-GATE ADMISSION
At tested corruption fractions:

1%
5%
10%
20%

the exploratory fit gate admitted:

0%

of the deliberately orthogonal corrupt updates.

Clean-update acceptance remains approximately:

97%
subject to the 99th-percentile calibration geometry and finite-sample refitting.

This is a strong synthetic working point,
not a guarantee for subtle poisoning.

PRIMARY DESIGN RULE
A lineage may exist
and
may be reconstructible

without automatically receiving:

SHARED TEMPLATE UPDATE AUTHORITY.

This mirrors earlier Yggdrasil distinctions:

source exists
!=
source is trusted.

candidate exists
!=
candidate deserves permanent structural write.

lineage exists
!=
lineage may rewrite family memory.

STRICT FIT-GATE FAILURE
A robust gate can become TOO conservative.

A legitimate family-wide developmental shift is introduced.

The entire family basis rotates by:

20 degrees.

This is not corruption.

It is a real persistent change in the generative family.

STRICT CURRENT-FIT GATE
Incoming shifted lineages are evaluated only against the old family template.

Because they are off-manifold,
the strict gate rejects the coherent new population.

100 matched persistent-shift streams.

EARLY POST-SHIFT MSE:

approximately:
0.03427.

LATE POST-SHIFT MSE:

approximately:
0.03428.

The family remains frozen near the obsolete basis.

HARD FREEZE NEGATIVE
A rule that says:

ONLY UPDATE FROM LINEAGES THAT FIT THE CURRENT TEMPLATE

cannot learn a legitimate new template manifold.

It protects memory by preventing adaptation.

QUARANTINE / PROVISIONAL UPDATE PATH
High-residual incoming lineages do NOT immediately alter the active family template.

Instead they enter a provisional quarantine buffer.

The controller asks:

IS THIS MISFIT:
isolated
or
population-wide and persistent?

Structural decision block:
80 lineage observations.

Coherent-shift persistence:
4 consecutive high-misfit blocks.

After four persistent blocks:

fit a provisional candidate basis
from the quarantined population.

Promote only if the candidate basis reduces current-population reconstruction error by more than:

50%

relative to the old basis.

These constants are synthetic discriminating values only.

PERSISTENT 20-DEGREE SHIFT RESULT
100 matched streams.

Candidate family basis promoted in:

100 / 100.

Promotion latency:

exactly 4 structural blocks
in this working point.

EARLY POST-SHIFT MSE:

approximately:
0.02701.

LATE POST-SHIFT MSE:

0.005127.

Thus the quarantine path returns reconstruction quality to the clean-family range.

PRIMARY ADAPTATION POSITIVE
The safe update rule needs TWO paths:

NORMAL IN-FAMILY UPDATE

and

PROVISIONAL OFF-MANIFOLD COHORT.

An off-manifold sample should initially lose shared-template write authority.

But repeated coherent off-manifold evidence can nominate:

THE FAMILY ITSELF MAY HAVE CHANGED.

TRANSIENT-CORRUPTION PROTECTION
The same persistence logic means:
one or two anomalous blocks

do not promote a new family template.

This is the update-level analogue of H37's split persistence.

Therefore:

TRANSIENT MISFIT
->
QUARANTINE.

PERSISTENT COHERENT POPULATION MISFIT
->
CANDIDATE FAMILY UPDATE.

Then:

HELD-OUT / FUNCTIONAL VALIDATION
->
PROMOTION.

CORRUPTION vs EVOLUTION
The key distinction is not:

GOOD SAMPLE
vs
BAD SAMPLE.

It is:

ISOLATED / INCOHERENT MISFIT

vs

PERSISTENT / POPULATION-COHERENT MISFIT.

The second may represent real developmental evolution.

CURRENT SHARED-TEMPLATE UPDATE LIFECYCLE
INCOMING LINEAGE UPDATE

->
FIT TO CURRENT FAMILY

IF GOOD FIT:

bounded normal family update.

IF POOR FIT:

no direct family-write authority
+
quarantine/provisional state.

Then inspect:

persistence
+
cohort coherence
+
held-out reconstruction
+
eventually functional consequence.

If evidence matures:

candidate family update
or
family split.

If evidence disappears:

discard provisional corruption state.

RELATION TO H37
H37 controls:
family merge/split identity.

H38 controls:
who may update the content of a shared family template.

These are distinct authority questions.

A family can remain one family
while its basis slowly evolves.

RELATION TO H12-H15
The pattern repeats:

CHEAP / WEAK EVIDENCE
may nominate a change.

PERMANENT SHARED STATE
requires:
persistent
and
validated
evidence.

Shared generative memory should not be easier to rewrite
than other slow hereditary state.

SECURITY INTERPRETATION
H38 is not a cryptographic security result.

However the architecture naturally gains resistance to:
- accidental corruption;
- broken sensor bursts;
- isolated outlier lineages;
- misrouted tombstones.

A compromised lineage has limited direct authority over shared generative memory.

IMPORTANT LIMITATION
The tested corruption is large and orthogonal.

Subtle in-manifold poisoning can evade residual gates.

That is now a distinct unresolved risk.

DECISION
AR-H38 is POSITIVE WITH A STRICT-GATE FREEZE LIMIT.

Supported synthetically:

- naive shared-template refitting propagates corrupted lineage updates into family memory;
- fit-gated admission strongly protects clean-family reconstruction against large off-manifold corruption;
- robust residual weighting provides similar protection;
- strict fit gating can permanently freeze legitimate family evolution;
- quarantine plus persistence distinguishes isolated misfit from coherent family shift;
- a persistent legitimate shift can be promoted after bounded provisional evidence.

Not demonstrated:

- subtle in-manifold poisoning resistance;
- real online family-basis update;
- optimal quarantine size;
- functional validation of candidate family updates;
- version rollback;
- distributed template consensus across cells.

NEXT CLEAN QUESTION
AR-H39 — IN-MANIFOLD SLOW TEMPLATE POISONING / VERSIONED PROMOTION

Question:

What if a bad update stays INSIDE the current family manifold
and therefore passes residual fit checks,
but slowly biases the shared generative coefficients or basis?

Compare:

A.
immediate live-template updates;

B.
shadow candidate version;

C.
held-out / recurrence canary validation;

D.
bounded promotion + rollback;

E.
legitimate slow family drift.

Desired:

subtle cumulative poisoning
->
candidate version fails validation
without corrupting live regenerative memory.

legitimate slow drift
->
candidate version eventually promotes.

This is a stronger test than H38's off-manifold corruption.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
state_dimensions = 12
family_rank = 3
base_lineages = 120
update_lineages = 120
heldout_lineages = 300
corruption_confirmation_seeds = 60
persistent_shift_streams = 100
persistent_shift_angle_deg = 20
quarantine_persistence_blocks = 4
