TITLE: DG-1A-AR-H16 — Delayed Structural Confirmation / Nomination-Credit Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE PROVENANCE RESULT + CREDIT-FRESHNESS TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh15-nomination-trust-adaptive-search-width-audit.ice

PURPOSE
H15 established reversible trust over structural nomination/search mechanisms.

But H15 implicitly assumes causal confirmation arrives soon enough to update the nomination mechanism that actually generated the candidate.

H16 introduces delayed structural confirmation.

QUESTION
When functional confirmation arrives much later than nomination,
can the organism update the correct nomination/search mechanism
without rewarding whichever heuristic happens to be active when the delayed result finally arrives?

BOUNDARY
This is synthetic.

It does not:
- prove real Yggdrasil structural confirmation has these delays;
- freeze an eligibility horizon;
- define a production trust update;
- solve delayed target-free consequence;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

META-CONTROLLER TOY
Two anonymous nomination mechanisms:

A
and
B.

PRE-TOPOLOGY-SHIFT confirmation probabilities:

A:
0.90

B:
0.20.

POST-SHIFT:

A:
0.10

B:
0.85.

Thus the useful nomination mechanism changes from:

A
->
B.

No semantic topology-change label is supplied.

STREAM
1200 structural opportunities.

Topology shift:
600.

Trust update:
EMA alpha 0.05.

Exploration:
10%.

At each opportunity:

1.
choose one nomination mechanism from current trust;

2.
generate a candidate;

3.
causal structural confirmation outcome is determined;

4.
confirmation is delivered only after a delay.

COMPARATORS

EXACT NOMINATION PROVENANCE

Each pending structural confirmation retains:

which nomination mechanism generated it.

When consequence arrives,
update that original mechanism.

NAIVE CURRENT-STATE CREDIT

When confirmation arrives,
credit whichever nomination mechanism happens to be active NOW.

This intentionally destroys causal provenance.

BOUNDED ELIGIBILITY / CREDIT HORIZON

Retain original nomination identity,
but discard confirmation if it arrives after a finite eligibility horizon.

This tests whether:
old-but-correctly-attributed credit
can itself become stale after topology change.

FIXED-DELAY SWEEP
200 matched seeds per condition.

Metrics:

PRE:
fraction selecting correct A in stable pre-shift window.

EARLY POST:
fraction selecting correct B in first 150 post-shift opportunities.

LATE:
fraction selecting B in final 250 opportunities.

REGRET:
sum of lost expected confirmation probability relative to choosing the currently better mechanism.

SWITCH LATENCY:
first post-shift point where B is chosen in >=80% of a 20-opportunity window.

DELAY = 0

EXACT and NAIVE are identical.

pre:
0.9492

early post:
0.7662

late:
0.9504

regret:
65.36

median switch latency:
26.

This is the no-credit-delay control.

DELAY = 5

EXACT:

pre:
0.9492

early:
0.7322

late:
0.9505

regret:
70.76

latency:
32.

NAIVE CURRENT CREDIT:

pre:
0.9042

early:
0.6876

late:
0.8856

regret:
119.87

latency:
35.5.

mean misattributed confirmations:
168.5.

PRIMARY PROVENANCE POSITIVE
Even a short delay makes current-state credit measurably corrupt trust.

The result belongs to:
the mechanism that generated the candidate,

not:
the mechanism active at feedback time.

DELAY = 20

EXACT:

pre:
0.9492

early:
0.6307

late:
0.9503

regret:
86.83

latency:
49.

NAIVE:

pre:
0.8727

early:
0.5448

late:
0.8907

regret:
169.35

latency:
52.

mean misattributions:
209.2.

DELAY = 50

EXACT:

pre:
0.9489

early:
0.4389

late:
0.9503

regret:
117.91

latency:
80.

NAIVE:

pre:
0.8258

early:
0.3610

late:
0.8482

regret:
268.57

latency:
108.

mean misattributions:
285.0.

DELAY = 100

EXACT:

pre:
0.9491

early:
0.1366

late:
0.9501

regret:
168.81

latency:
131.

NAIVE:

pre:
0.6702

early:
0.2927

late:
0.7170

regret:
375.43

latency:
167.

mean misattributions:
381.1.

PRIMARY DELAY RESULT
Exact provenance prevents identity corruption,
but it does not remove delay itself.

Long-delayed feedback means the controller continues trusting the old nomination mechanism after topology changes because new evidence has not arrived yet.

Thus:

CREDIT IDENTITY
and
CREDIT LATENCY

are separate problems.

OUT-OF-ORDER / VARIABLE-DELAY STRESS
Base delay:
50.

Uniform jitter:
+/-40.

Therefore confirmations arrive with ages approximately:

10 through 90 opportunities.

200 matched seeds.

EXACT PROVENANCE:

pre:
0.9503

early:
0.3990

late:
0.9484

regret:
114.44

median switch latency:
87.

NAIVE CURRENT CREDIT:

pre:
0.8366

early:
0.4445

late:
0.8375

regret:
228.42

latency:
78.5.

mean misattributed confirmations:
267.2.

IMPORTANT INTERPRETATION
Naive credit can sometimes appear to switch earlier by accidentally assigning old outcomes to the new active mechanism.

That is not valid adaptation.

Its late-state trust remains substantially worse.

Therefore:

FAST APPARENT RESPONSE
CAN BE
MISATTRIBUTED CREDIT.

BOUNDED ELIGIBILITY HORIZON
Keep exact nomination provenance,
but discard structural confirmation if:

confirmation_age
>
eligibility_horizon.

Same variable-delay stress.

HORIZON = 10

pre:
0.9335

early:
0.0738

late:
0.4210

regret:
394.29

stable-switch recovery:
62.5%.

mean dropped confirmations:
1135.4.

HARD NEGATIVE
An eligibility horizon that is too short starves the trust learner.

Most valid structural confirmations expire before they can be used.

HORIZON = 20

pre:
0.9503

early:
0.1591

late:
0.9484

regret:
152.27

median switch latency:
139.

dropped:
988.7.

HORIZON = 40

pre:
0.9503

early:
0.4221

late:
0.9484

regret:
112.07

latency:
82.

dropped:
701.6.

HORIZON = 60

pre:
0.9503

early:
0.4573

late:
0.9484

regret:
107.88

latency:
76.

dropped:
418.0.

HORIZON = 80

pre:
0.9503

early:
0.4234

late:
0.9484

regret:
111.69

latency:
83.

dropped:
138.4.

HORIZON = 120

equivalent to accepting the full tested delay range.

pre:
0.9503

early:
0.3990

late:
0.9484

regret:
114.44

latency:
87.

dropped:
0.

PRIMARY CREDIT-FRESHNESS POSITIVE
At this synthetic working point,
a moderate eligibility horizon:

60

outperforms both:

accept every delayed confirmation forever

and

expire feedback very quickly.

Reason:

some extremely delayed pre-shift confirmations are correctly attributed
but no longer useful for CURRENT trust after the causal topology has changed.

Thus:

CORRECTLY ATTRIBUTED
DOES NOT AUTOMATICALLY MEAN
CURRENTLY RELEVANT.

RELATION TO S6
S6 showed delayed consequence can make local value-of-information learning continue operating on obsolete resource economics.

H16 shows the same problem in slow structural search:

delayed confirmation preserves old nomination authority after its validity has changed.

RELATION TO S9 / H15
S9:
control trust must be recency-sensitive.

H15:
nomination search authority must be reversible.

H16 adds:

the CREDIT EVENTS that update trust need:
- provenance;
- eligibility;
- freshness.

CURRENT NOMINATION-CREDIT OBJECT
A pending structural nomination should conceptually carry:

NOMINATION IDENTITY / TYPE

+

LOCAL CONTEXT / GENERATION FINGERPRINT

+

CREATION TIME

+

CANDIDATE IDENTITY

+

SEARCH COST SPENT

+

ELIGIBILITY / CREDIT AGE

until causal structural consequence arrives.

Then:

confirmation
updates
THE NOMINATION THAT GENERATED IT,

not:
whatever mechanism happens to be active later.

GENERAL PRINCIPLE
Yggdrasil needs provenance not only for:

SENSOR EVIDENCE

and

CAUSAL CONTROLS,

but also for:

DELAYED ADAPTIVE DECISIONS.

The object receiving delayed credit must remain identifiable across time.

DECISION
AR-H16 is POSITIVE WITH A CREDIT-FRESHNESS TRADEOFF.

Supported synthetically:

- delayed structural confirmation corrupts trust when credit is assigned to current state rather than original nomination;
- exact nomination provenance fixes that identity error;
- long delay still creates adaptation lag even with correct provenance;
- very old correctly attributed feedback can become stale after topology change;
- a bounded eligibility horizon can improve post-shift trust adaptation;
- an overly short horizon destroys useful learning.

Not demonstrated:

- real Yggdrasil structural-confirmation latency;
- optimal eligibility lifetime;
- local context fingerprinting;
- revival/reuse of old delayed credit after regime recurrence;
- delayed credit under overlapping structural candidates;
- distributed confirmation across cell lineages.

NEXT CLEAN QUESTION
AR-H17 — CONTEXT-GENERATION / SIMILARITY-GATED DELAYED CREDIT

A fixed age horizon is crude.

Question:

Can delayed structural confirmation be accepted or routed according to whether:

the current local causal context
still resembles
the context in which the nomination was created?

Desired:

same-context delayed confirmation
->
update current trust.

changed-context confirmation
->
do not overwrite current trust.

recurring old context
->
possibly route confirmation into retained context-specific evidence
without allocating one permanent semantic regime ID.

This would replace:
AGE ALONE

with:

AGE
+
CONTEXT SIMILARITY
+
CAUSAL PROVENANCE.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
trust_streams_per_condition = 200
stream_opportunities = 1200
topology_shift = 600
trust_update_alpha = 0.05
exploration_fraction = 0.10
variable_delay_base = 50
variable_delay_jitter = 40
