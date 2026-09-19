TITLE: DG-1A-AR-H94 — Self-Modeled Developmental Payback / Learned Commitment-Horizon Audit
DATE: 2026-09-19
STATUS: SYNTHETIC / MEASURED_SANDBOX POSITIVE DEVELOPMENTAL-SELF-MODEL RESULT + AUDIT-COST / SELF-KNOWLEDGE STALENESS TRADEOFF
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh93-option-space-transformation-audit.ice

PURPOSE
H93 gives the developmental controller:
a fixed assumed transition horizon.

H94 removes that privilege.

QUESTION
Can the organism learn:

HOW LONG
ITS OWN DEVELOPMENTAL CHANGE
TAKES

and therefore:

HOW LONG
A NICHE MUST REMAIN USEFUL
TO REPAY
THE DEVELOPMENTAL VALLEY?

A second question is critical:

if development becomes faster or slower,
how does the organism update its self-model
when it is no longer attempting development often enough to observe the change?

BOUNDARY
This is synthetic.

It does not:
- freeze a production self-model;
- freeze a 15% audit rate;
- prove real Yggdrasil developmental transitions have this structure;
- solve niche persistence forecasting;
- modify or execute STAB-18-R1.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

AFFORDANCE ECONOMY
Same H93 developmental geometry.

Undifferentiated value:
20 per step.

Developmental transition value:
8.

Mature specialized value:
32.

Thus:
development temporarily loses:

12 value units / step

before gaining:

12 value units / mature step.

Approximate break-even niche duration:

~2 * transition duration.

PHASES
150 synthetic developmental opportunities
per phase.

PHASE 1 — BASELINE

true transition duration:
approximately 5 steps.

mean niche duration:
approximately 14.

Development is usually worth:
attempting.

PHASE 2 — DAMAGE-SLOWED DEVELOPMENT

true transition:
approximately 9 steps.

same niche duration:
approximately 14.

Now:
development is usually NOT worth:
the transition cost.

PHASE 3 — REUSED / FACILITATED DEVELOPMENT

true transition:
approximately 3 steps.

mean niche duration:
approximately 8.

Development becomes:
useful again

despite:
the shorter niche.

The change in:
the organism's own transition dynamics
is not:
semantically labeled.

PERSISTENCE FORECAST
Each developmental opportunity receives:
a noisy local estimate
of:
how long the current niche will persist.

Prediction noise:
SD approximately 1.5 steps.

All non-oracle policies receive:
the same persistence signal.

COMPARATORS

FIXED SELF-MODEL

always assumes:
transition duration = 5.

LEARNED SELF-MODEL
NO AUDIT

EMA-updates:
transition-duration estimate

whenever:
development is actually attempted.

If:
the controller stops attempting development,
its self-model:
stops receiving evidence.

LEARNED SELF-MODEL
+
SPARSE DEVELOPMENTAL AUDIT

Same learned transition estimate.

But:
when ordinary policy says:
do not develop,

a small probability still attempts:
a developmental audit.

The audit has:
real transition cost.

It is not:
free observation.

ORACLE

knows:
the actual episode duration
and
actual developmental transition duration.

Diagnostic only.

PRIMARY CONFIRMATION
200 matched synthetic sequences.

PRIMARY RESULTS

FIXED SELF-MODEL

total functional value:
110,088.8.

regret vs oracle:
9,163.9.

overall commit fraction:
69.9%.

BASE PHASE

value:
327.64 / opportunity.

commit:
94.4%.

DAMAGE-SLOWED PHASE

value:
236.42.

commit:
94.5%.

PRIMARY FIXED-MODEL FAILURE
The old 5-step self-model causes:
massive overcommitment

when:
development has actually slowed to:
~9 steps.

The organism still behaves as if:
its body/runtime changes
at yesterday's speed.

REUSED-FAST PHASE

value:
169.86.

commit:
20.7%.

The same fixed model now:
undercommits

because:
real development has accelerated.

Thus:
developmental self-knowledge can become stale
in both directions.

LEARNED SELF-MODEL WITHOUT AUDIT

total:
114,537.4.

regret:
4,715.3.

BASE:
estimated transition ends near:
5.01.

DAMAGE-SLOWED:

commit:
14.2%.

estimated transition:
8.91.

value:
276.47.

PRIMARY LEARNED-SLOWDOWN POSITIVE
When development is still attempted enough to observe:
the slowdown,

the self-model adapts strongly.

But:

REUSED-FAST PHASE

commit:
0%.

estimated transition remains:
~8.90.

value:
159.53.

PRIMARY SELF-KNOWLEDGE STARVATION NEGATIVE
The controller correctly learned:

DEVELOPMENT IS TOO SLOW.

Then:
stopped developing.

When the organism later became:
developmentally faster,

the controller had:
no evidence
of that improvement.

Thus:

A POLICY CAN MAKE
ITS OWN SELF-MODEL
UNOBSERVABLE.

This is a new H94 failure mode.

SPARSE AUDIT
Primary working point:
6% audit probability

when:
ordinary policy would not develop.

total:
approximately 115,989
in the first primary matched run.

regret:
~3,322.

damage-slowed transition estimate:
~8.96.

fast reused phase:
estimated transition:
~3.12.

commit:
~36.8%.

value:
~171.86.

PRIMARY AUDIT POSITIVE
Occasional costly developmental experiments
allow the system to discover:

I HAVE BECOME
EASIER / FASTER
TO CHANGE.

This restores:
useful commitment.

AUDIT-PROBABILITY SWEEP
120 matched sequences
per point.

1%

total:
114,803.

regret:
4,614.

audits:
2.73.

fast-phase commit:
3.4%.

fast-phase value:
161.19.

final transition estimate:
7.27.

3%

total:
115,246.

regret:
4,080.

audits:
7.70.

fast commit:
15.0%.

value:
164.75.

final estimate:
4.65.

6%

total:
116,204.

regret:
3,212.

audits:
14.11.

fast commit:
38.2%.

value:
172.36.

final estimate:
3.14.

10%

total:
116,513.

regret:
2,830.

audits:
22.04.

fast commit:
53.1%.

value:
176.36.

final estimate:
3.00.

15%

total:
116,634.

regret:
2,795.

audits:
31.29.

fast commit:
62.6%.

value:
179.11.

final estimate:
2.99.

25%

total:
116,357.

regret:
3,090.

audits:
49.31.

fast commit:
72.3%.

value:
181.50.

final estimate:
2.99.

PRIMARY AUDIT-ECONOMY RESULT
More audit improves:
self-model refresh

and:
fast-phase exploitation.

But:
too much audit
wastes:
real developmental value

during:
periods when commitment remains unprofitable.

The tested total-value optimum lies near:
15%.

This number is:
not frozen.

The scientific point is:

SELF-KNOWLEDGE
HAS
AN EXPERIMENTAL MAINTENANCE COST.

RELATION TO H21 / H52 / H87
H21:
challenge context only when:
evidence value justifies cost.

H52:
scarcity challenge is:
value-gated.

H87:
cryptic variation is:
resource-budgeted.

H94:
self-model calibration
is also:
a value-of-information problem.

One generic evidence economy
may allocate:
self-experiments.

RELATION TO H73-H74
H73-H74 introduced:
adaptive plasticity / canalization.

H94 adds:
the controller must learn:
the actual dynamics
of that plasticity.

It should know:

HOW FAST DO I MELT?

HOW FAST DO I RECRYSTALLIZE?

HOW EXPENSIVE IS THE TRANSITION?

Those quantities can:
change over the organism's lifetime.

RELATION TO H79
Compiled program structure can make:
repeated transformations faster.

H94's phase-3 speedup can be interpreted as:
a synthetic analogue of:
developmental facilitation / compiled transition reuse.

Thus:
the organism's own change dynamics
are:
learnable state.

GENERAL PRINCIPLE
AN ADAPTIVE ORGANISM
SHOULD MODEL:

NOT ONLY
THE WORLD,

BUT ALSO:

THE DYNAMICS
OF ITS OWN
ADAPTATION.

And:

A SELF-MODEL
CAN BECOME STALE
WHEN
THE POLICY STOPS GENERATING
THE EXPERIENCES
NEEDED TO UPDATE IT.

DECISION
AR-H94 is POSITIVE WITH AN AUDIT-COST / SELF-KNOWLEDGE-STALENESS TRADEOFF.

Supported synthetically:

- fixed developmental-horizon assumptions fail when transition speed changes;
- empirical self-modeling adapts to developmental slowdown;
- policy-induced lack of experimentation can freeze stale self-knowledge;
- sparse developmental audits rediscover improved plasticity;
- audit frequency trades self-model freshness against real developmental cost;
- a bounded intermediate audit rate produces the best tested total value.

Not demonstrated:

- real developmental transition sensing;
- safe self-experiment design;
- learned niche-duration models;
- multi-dimensional self-models;
- self-model sharing across cells;
- offline rehearsal.

NEXT HIGH-VALUE MOVE
AR-H95 — SHADOW DEVELOPMENT / COUNTERFACTUAL REHEARSAL

H94 refreshes:
developmental self-knowledge

through:
real costly commitments.

A more radical question:

CAN THE ORGANISM
REHEARSE DEVELOPMENT
IN SHADOW

before:
changing live phenotype?

Candidate mechanism:

use:
generative lineage/template memory
+
current local resource model

to simulate:
a provisional developmental trajectory

without:
granting it live execution authority.

Compare:

A.
real developmental audits;

B.
shadow / model-based rehearsal;

C.
rehearsal with model error;

D.
occasional real calibration;

E.
model drift after damage;

F.
hallucinated cheap development.

Desired:

shadow rehearsal
reduces:
costly real audits

but:

MODEL PREDICTION
must never become:
self-validating authority.

Occasional real consequence
must:
calibrate
the shadow model.

This would connect:
H36-H40 generative memory
with:
H94 developmental self-model.

Do not execute STAB-18-R1 during this lane.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
canonical_r1_execution_spent = false
phases = 3
opportunities_per_phase = 150
matched_sequences_primary = 200
audit_sweep_sequences = 120
best_tested_audit_probability = 0.15
