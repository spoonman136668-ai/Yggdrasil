TITLE: DG-1A-AR-H19 — Temporal Continuity / Change-Point Confidence for Context Fingerprints
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE SHORT-ARTIFACT FILTER + HARD PERSISTENT-CONTEXT IDENTIFIABILITY NEGATIVE
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh18-provenance-diverse-context-fingerprint-audit.ice

PURPOSE
H18 established that provenance-aware source diversity improves context fingerprints under family-specific corruption,
but globally coherent context corruption remains under-identified.

H19 asks:

Can temporal continuity reject brief globally coherent false-context bursts
without making genuine sustained context transitions too slow?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil contexts follow this binary geometry;
- freeze a smoothing constant or persistence count;
- establish a production change-point detector;
- solve persistent common-mode false context;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

CONTEXT STREAM
1500 opportunities.

True context sequence:

A:
0..499

B:
500..999

A:
1000..1499.

Numeric latent context:

A = -1
B = +1.

The controller sees only a noisy provenance-aware aggregate context cue.

Primary cue noise SD:

0.45.

GLOBAL COHERENT ARTIFACT
A brief artifact replaces the entire context cue with the opposite context mean.

Thus:
all context sources agree
and
all context sources are wrong

during the artifact.

Artifact-start probability per opportunity:

0.006.

Tested artifact burst lengths:

1
3
5
10
20.

COMPARATORS

INSTANTANEOUS

Use:
sign(current context cue).

EMA CONTINUITY

Exponential moving context estimate:

alpha = 0.08.

Route according to the sign of the smoothed estimate.

SIX-VOTE PERSISTENCE GATE

Maintain current accepted context.

Switch only after:

6 consecutive local context votes

support the opposite state.

This is an exploratory discriminating mechanism.

Do not freeze six as a biological constant.

PRIMARY CONFIRMATION
300 matched seeds per burst length.

Metrics:

STABLE WRONG-ROUTING FRACTION
fraction of stable-context opportunities routed to the wrong context.

ARTIFACT WRONG-ROUTING FRACTION
fraction of artifact opportunities that are actually allowed to control routing.

TRUE-SWITCH DETECTION LATENCY
opportunities after a genuine transition until the new context is routed correctly for 10 consecutive opportunities.

BRIEF ARTIFACT LENGTH = 1

INSTANT

stable wrong:
0.01896

artifact accepted as context:
0.99017

true-switch latency:
approximately 1.06 opportunities.

EMA

stable wrong:
0

artifact accepted:
0.01563

true-switch latency:
approximately 7.93.

PERSISTENCE-6

stable wrong:
0

artifact accepted:
0.00844

true-switch latency:
approximately 5.37.

PRIMARY SHORT-BURST POSITIVE
A small temporal persistence requirement rejects almost all one-step globally coherent context corruption.

This creates useful independence from:
instantaneous common-mode artifact.

ARTIFACT LENGTH = 3

INSTANT

stable wrong:
0.03030

artifact accepted:
0.98994

latency:
approximately 1.23.

EMA

stable wrong:
0

artifact accepted:
0.01779

latency:
approximately 8.10.

PERSISTENCE-6

stable wrong:
0.00028

artifact accepted:
0.01202

latency:
approximately 5.45.

ARTIFACT LENGTH = 5

INSTANT

stable wrong:
0.04128

artifact accepted:
0.99000

latency:
approximately 1.37.

EMA

stable wrong:
0.00048

artifact accepted:
0.03234

latency:
approximately 8.35.

PERSISTENCE-6

stable wrong:
0.00102

artifact accepted:
0.01599

latency:
approximately 5.56.

PRIMARY OPERATING RESULT
At artifact durations shorter than the persistence requirement,
the persistence gate keeps wrong-context routing near zero
while detecting real sustained transitions after roughly:

5 to 6 observations.

EMA is even smoother against very short corruption,
but responds approximately:

8 observations

after true transitions.

Thus temporal continuity creates a real:

ARTIFACT REJECTION
vs
TRANSITION LATENCY

tradeoff.

ARTIFACT LENGTH = 10

INSTANT

stable wrong:
0.06781

artifact accepted:
0.98923

EMA

stable wrong:
0.02261

artifact accepted:
0.28172

PERSISTENCE-6

stable wrong:
0.05616

artifact accepted:
0.49535.

INTERPRETATION
Once the coherent artifact persists longer than the change-point gate,
the gate begins accepting it as a legitimate context transition.

ARTIFACT LENGTH = 20

INSTANT

stable wrong:
0.11783

artifact accepted:
0.98789

EMA

stable wrong:
0.09844

artifact accepted:
0.64554

PERSISTENCE-6

stable wrong:
0.10820

artifact accepted:
0.74228.

PRIMARY NEGATIVE
Temporal continuity does not determine whether a persistent context transition is real.

It only asks:

DID THE NEW CONTEXT LAST LONG ENOUGH?

A sufficiently persistent false context therefore passes.

PERSISTENT FALSE-CONTEXT HARD STRESS
The true causal context remains:

A

for the entire stream.

At opportunity:
500

every context observation switches coherently to an apparent:

B

and remains there permanently.

No context-only observation distinguishes this from a genuine A -> B transition.

300 matched seeds.

TIME TO FALSE B ACCEPTANCE

INSTANT

median:
0 opportunities.

EMA

median:
8.

mean:
7.74.

PERSISTENCE-6

median:
5.

mean:
5.30.

HARD IDENTIFIABILITY NEGATIVE
All context-only temporal methods eventually accept the persistent false context.

Persistence changes:

WHEN

the system becomes wrong.

It does not determine:

WHETHER

the context is causally real.

If false context and real context have the same:
- source agreement;
- persistence;
- temporal statistics;

then context observation alone is under-identified.

RELATION TO H10 / H11
H10/H11 reached the same boundary for slow structural memory.

Source diversity rejected family-specific corruption.

Temporal persistence rejected faster common-mode artifacts.

But globally shared artifacts with matched timescale remained indistinguishable from true structure.

H19 shows the same hierarchy for context routing.

RELATION TO H18
H18 gives:

PROVENANCE DIVERSITY.

H19 adds:

TEMPORAL CONTINUITY.

The combined context-confidence stack can reject:

family-local corruption

and

brief global corruption.

It still cannot reject:

persistent globally coherent false context.

CURRENT CONTEXT-ROUTING CONFIDENCE
A stronger context fingerprint now conceptually contains:

SOURCE / FAMILY PROVENANCE

+

EFFECTIVE INDEPENDENT SOURCE COUNT

+

INTER-SOURCE AGREEMENT

+

TEMPORAL CONTINUITY

+

CHANGE-POINT PERSISTENCE

+

FRESHNESS.

But these remain observational confidence signals.

They do not establish causal reality.

NEXT IDENTIFIABILITY SOURCE
The remaining clean source is:

FUNCTIONAL / CAUSAL VALIDATION OF THE CONTEXT TRANSITION.

If context says:

THE LOCAL CAUSAL REGIME CHANGED,

then the policies / controls / nomination mechanisms predicted to be useful in that context should actually show changed functional consequence.

This motivates H20.

DECISION
AR-H19 is POSITIVE for short-artifact rejection,
with a HARD NEGATIVE for persistent false context.

Supported synthetically:

- temporal continuity rejects brief coherent false-context bursts;
- a persistence gate can outperform instantaneous routing by orders of magnitude on 1-5-step artifacts;
- the cost is bounded genuine-transition latency;
- longer false-context bursts eventually defeat temporal gating;
- a persistent false context is observationally indistinguishable from a genuine sustained transition in this benchmark.

Not demonstrated:

- real Yggdrasil context timescales;
- optimal persistence window;
- adaptive change-point threshold;
- causal validation of context transitions;
- context tracking under more than two overlapping regimes.

NEXT
AR-H20 — FUNCTIONALLY GROUNDED CONTEXT CHANGE VALIDATION

Question:

When context observations indicate a persistent transition,
can the organism use a small bounded causal challenge to ask:

DID THE LOCAL CAUSAL ECONOMY ACTUALLY CHANGE?

Compare:

A.
context-only acceptance;

B.
temporal persistence only;

C.
persistent context proposal + randomized functional challenge;

D.
genuine context transition;

E.
persistent global false context.

Desired:

real causal transition
->
context switch accepted.

persistent false context
with unchanged causal consequences
->
context switch rejected or held low-confidence.

This should remain local,
bounded,
and non-semantic.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
primary_context_noise_sd = 0.45
artifact_start_probability = 0.006
confirmation_seeds_per_burst = 300
tested_burst_lengths = 1,3,5,10,20
persistence_gate_votes = 6
ema_alpha = 0.08
persistent_false_context_seeds = 300
