TITLE: DG-1A-AR-H4 — Temporary Repair Niche / Heritable-Write Gating Audit
DATE: 2026-09-18
STATUS: SYNTHETIC / MEASURED_SANDBOX REPAIR-INHERITANCE AUDIT
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh3-inherited-prior-fast-utility-audit.ice

PURPOSE
Test whether an acute repair state can recruit strong fast adaptation
without becoming a persistent inherited lineage identity after the injury disappears.

Question:
WHEN SHOULD A TEMPORARY FUNCTIONAL NICHE BE ALLOWED TO WRITE INTO SLOW HERITABLE STATE?

BOUNDARY
This is synthetic.

It does not:
- implement genomic inheritance in Yggdrasil;
- imply biological epigenetic machinery;
- modify or execute STAB-18-R1;
- authorize injury-triggered mutation.

EVIDENCE
SYNTHETIC
MEASURED_SANDBOX

REGIMES

MAINTENANCE OPTIMUM M:
[0.25, 0.45, 0.25, 0.35]

REPAIR OPTIMUM R:
[0.20, 0.25, 0.80, 0.15]

Population:
512

Fast role state:
4 dimensions

Slow micro-genome:
4 dimensions

Episodes:
200 maintenance
+
D repair
+
200 maintenance

Repair duration D:
20
50
100
150

Fast role learning:
always active.

Fast evidence noise:
sigma 0.16

Fast role eta:
0.14

Reproduction:
every 10 episodes

Micro-genome mutation:
0.025

Parent retention:
0.97

Selection strength:
28

Birth expression:
uses the H3-style novelty-gated inherited prior.

STRATEGIES

A. UNCONDITIONAL SLOW WRITE
Micro-genome selection/mutation continues through maintenance and repair.

B. PERSISTENCE-CONFIRMATION HOLDOFF
After any regime change:
slow inherited-state rewriting is suppressed for 50 episodes.

Fast role adaptation remains active.

If the new regime persists beyond the holdoff:
slow inheritance is permitted again.

This is a synthetic persistence-control mechanism,
not a frozen production timer.

C. NO-REPAIR-WRITE ORACLE
Slow inheritance is never changed during the repair phase.

This is an oracle upper-bound control for preserving maintenance lineage state.

It is not a deployable mechanism because it knows the semantic phase label.

SEEDS
10 fresh seeds per primary condition.

PRIMARY RESULTS

D = 20

UNCONDITIONAL
repair-phase mean loss:
0.010553

first 50 post-repair loss:
0.007650

micro-genome distance to M at repair end:
0.026164

micro-genome distance to R:
0.036861

HOLDOFF
repair:
0.010292

post50:
0.007618

g-distance M:
0.025887

g-distance R:
0.036810

NO-REPAIR-WRITE
repair:
0.010639

post50:
0.007260

g-distance M:
0.024774

g-distance R:
0.038507

At short injury duration,
slow inheritance provides little value.

D = 50

UNCONDITIONAL
repair:
0.009380

post50:
0.007988

g-distance M:
0.029194

g-distance R:
0.034952

HOLDOFF
repair:
0.009425

post50:
0.007727

g-distance M:
0.025887

g-distance R:
0.036810

NO-REPAIR-WRITE
repair:
0.009648

post50:
0.007276

g-distance M:
0.024774

g-distance R:
0.038507

At a repair duration equal to the synthetic holdoff,
the slow layer is still largely protected.

D = 100

UNCONDITIONAL
repair:
0.008780

post50:
0.008472

g-distance M:
0.033751

g-distance R:
0.032020

HOLDOFF
repair:
0.008959

post50:
0.008215

g-distance M:
0.029980

g-distance R:
0.034625

NO-REPAIR-WRITE
repair:
0.009275

post50:
0.007265

g-distance M:
0.024774

g-distance R:
0.038507

Longer repair begins to make adaptation of the slow prior useful during repair,
but that benefit carries a post-repair cost.

D = 150

UNCONDITIONAL
repair:
0.008401

post50:
0.008884

g-distance M:
0.038312

g-distance R:
0.028943

HOLDOFF
repair:
0.008678

post50:
0.008576

g-distance M:
0.033395

g-distance R:
0.032403

NO-REPAIR-WRITE
repair:
0.009160

post50:
0.007255

g-distance M:
0.024774

g-distance R:
0.038507

PRIMARY RESULT
Under unconditional slow adaptation,
a sufficiently long repair interval shifts the inherited micro-genome from a maintenance-biased prior toward the repair optimum.

That improves repair-phase performance,
but worsens the first post-repair interval.

This is a synthetic form of:
REPAIR CANALIZATION.

PRIMARY NEGATIVE
Do not let:

acute injury
->
immediate heritable rewrite.

Fast repair specialization and slow inherited adaptation serve different timescales.

FAST ROLE LAYER
should respond immediately to:
- injury evidence;
- local damage;
- predictive error.

SLOW HERITABLE LAYER
should require:
- persistence;
- repeated useful consequence;
- or another stronger stability criterion

before shifting its prior.

PERSISTENCE-CONFIRMATION RESULT
The 50-episode holdoff is not globally optimal and is not proposed as a fixed Yggdrasil constant.

Its scientific use is discriminating:

it reduces:
- micro-genome movement toward temporary repair;
- post-repair inherited hangover;

while still allowing a sufficiently persistent changed regime to begin influencing the slow state.

This establishes the desired qualitative behavior.

WHY THE ORACLE MATTERS
The no-repair-write control shows the maximum maintenance-memory preservation possible in this toy.

It has worse repair-phase performance at long D,
but consistently lower post-repair cost.

Thus there is a genuine trade:

adapt slow state to prolonged injury

vs

preserve pre-injury developmental prior.

No single semantic rule:
"never inherit repair"
or
"always inherit useful repair"

is universally correct.

PREFERRED ARCHITECTURAL PRINCIPLE
SLOW WRITE SHOULD REQUIRE PERSISTENCE.

Conceptually:

FAST:
role expression changes immediately.

MEDIUM:
confidence / novelty estimates whether the new regime is transient.

SLOW:
micro-genome write occurs only after sustained evidence.

This fits the emerging timescale stack from U13/H1-H3.

REPAIR-SPECIFIC CONSEQUENCE
A repair function should normally be:

TRANSIENTLY EXPRESSIBLE

without automatically becoming:

LINEAGE-DEFINING.

This matters for regeneration.

Otherwise an organism repeatedly injured in one region could produce descendants permanently biased toward repair at the expense of normal function.

PERSISTENT ENVIRONMENT EXCEPTION
If the changed condition remains for many slow cycles,
it may no longer be an injury transient.

It becomes a real niche/environmental regime.

Then slow inheritance can be useful.

Therefore the distinction is not:

repair
vs
non-repair.

It is:

TRANSIENT
vs
PERSISTENT USEFUL STRUCTURE.

CONFIDENCE / NOVELTY CONNECTION
U13 established:
one shared novelty magnitude can gate how much adaptation is recruited,
while typed residuals preserve event identity.

H4 suggests a second use:

novelty/persistence can gate:
whether fast adaptation is allowed to WRITE SLOW STATE.

Do not collapse:
fast-role activation
and
slow-write authorization.

They are separate decisions.

NEXT
AR-H5 — HERITABLE WRITE CREDIT

Remove the synthetic oracle notion of regime persistence.

Question:
Can the slow layer decide to retain a developmental bias using only:
- repeated local causal consequence;
- confidence/freshness;
- time-integrated eligibility;

without knowing whether the event is semantically:
repair,
season,
or niche change?

Desired rule:

repeated useful local consequence
+
persistent context
->
slow retention

short-lived useful consequence
->
fast role adaptation only.

This is the natural bridge between:
AR-U causal credit
and
AR-H inheritance.

PROVENANCE
evidence_class = SYNTHETIC_MEASURED_SANDBOX
canonical_scientific_execution = false
new_yggdrasil_training_run = false
canonical_r1_execution_spent = false
population = 512
primary_seeds = 10
repair_durations = 20,50,100,150
