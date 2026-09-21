TITLE: YGGDRASIL TRAINING TRACK T8 / APPLICATION A16 — Hysteretic Working-State Plasticity Under Moving Developmental Drift
DATE: 2026-09-21
STATUS: PREREGISTERED / CONTINUOUS-DRIFT PLASTICITY GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T8 / APPLICATION-A
PARENT: A15 T7 Versioned Developmental-Context Revision
BRANCH: dg1a-ar

PURPOSE

A15 established that a known developmental context C can undergo one stable revision:

C-v1 -> C-v2,

while preserving ancestry,
keeping the context-slot count fixed,
and later selecting either historical version without retraining.

A15 preserves one major boundary:

CONTINUOUS / RAPID DRIFT.

A16 asks:

CAN YGGDRASIL TRACK A DEVELOPMENTAL NICHE
THAT MOVES THROUGH SEVERAL SMALL STABLE STEPS
WITHOUT CREATING A PERMANENT POLICY VERSION FOR EVERY STEP,
WITHOUT REACTING TO A SHORT-LIVED FLUCTUATION,
AND WITHOUT LOSING ITS DURABLE C-v1 / C-v2 HISTORY?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No production deployment.
No network exposure.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

T8 CLAIM

A16 introduces one bounded:

WORKING DEVELOPMENTAL PRIOR

for context lineage C.

The working prior is:

authorized;
restart-persistent;
used only for future clean replacement-cell specialization;
not a permanent C policy version;
not a new context slot;
not allowed to modify C-v1 or C-v2 history.

A16 does NOT permit:

C-v3 creation;
fourth context creation;
unbounded plastic state;
one-observation adaptation;
nearest-prior guessing;
constitutional self-modification;
task-program mutation;
governance mutation;
provenance mutation.

FROZEN PARENT

A15 accepted closure commit:

e4b47d26825fcb23c37126d49ec9d363e2c7e73a.

A15 source SHA-256:

4dfd8814c869380317bb90d8baf68f79f4c2ce9874db7bc9278546b56001c071.

A15 freeze F15:

dd9cd2cfee331d94631af17b0f0a61684e5091a4.

A15 versioned-drift manifest:

0e7d6c14cff50e8e8705cbf4082d5f333267b2e4646eea333559db4b4b28cef9.

A15 primary result:

494b3096e407790a341d66ee37833546b5ce50e2a88a2308a17c1c5bfb0941d3.

For each scenario,
A16 begins with the accepted A15 state:

context slots = A,B,C;
C history = [v1,v2];
C active durable version = v2;
working prior = C-v2.

DURABLE HISTORY INVARIANT

Throughout A16:

C durable history MUST remain byte-identical:

[v1,v2].

C-v3 creations:

0.

Context slot count:

3.

The working prior is separate from durable version history.

WORKING-STATE RECORD

The C working-state record contains:

context lineage = C;
durable anchor version = 2;
working prior;
working generation;
parent working digest;
working digest;
authorization epoch;
evidence-window digest.

Initial working state:

working prior = C-v2;
working generation = 0.

A successful plasticity update increments:

working generation += 1.

No working generation creates a durable policy version.

MOVING-DRIFT PATH

No primary moving-drift path may exist before A16 freeze.

Let F16 be the exact A16 harness freeze commit.

For each scenario,
let P0 = accepted C-v2 prior.

Build P1,P2,P3,P4 iteratively.

For step j = 1..4:

construct sorted lexicographic NEIGHBORS(P[j-1]) where candidate:

belongs to frozen 124-prior catalog;
candidate != prior_A;
candidate != prior_B;
candidate != C-v1;
candidate != P[j-1];
L1(candidate,P[j-1]) == 2.

If possible,
exclude P0..P[j-2]
to avoid immediate cycling.

Mechanically before freeze,
verify every parent scenario can construct four steps under this rule.

Derive index:

SHA-256(
"YGG-A16-PATH|"
+ F16
+ "|"
+ decimal(scenario)
+ "|"
+ decimal(step)
).

Map the first eight bytes modulo the current eligible-neighbor list length.

No performance shaping,
distance shaping beyond exact one-step adjacency,
or post-freeze replacement is allowed.

Thus:

P0 -> P1 -> P2 -> P3 -> P4

is a four-step local developmental drift path.

HYSTERETIC EVIDENCE BLOCK

One evidence block contains:

8 unique developmental observations

generated as four exact zero-mean pairs around one target prior.

The exact mean of one complete block equals that prior.

A working-prior update requires:

TWO consecutive complete evidence blocks

with the same exact candidate mean.

Therefore:

8 observations may nominate;

16 consistent observations may authorize a working-state update.

One block alone never changes the working prior.

TEMPORARY FLUCTUATION PHASE

Before gradual drift begins:

deliver exactly one 8-observation block around P1.

Required:

candidate P1 may be nominated;
working prior remains P0.

Then deliver one 8-observation block around P0.

Required:

pending P1 nomination clears;
working prior remains P0;
working generation remains 0.

This is the primary anti-overreaction test.

GRADUAL DRIFT PHASES

Then execute:

P1 for 16 observations;
P2 for 16 observations;
P3 for 16 observations;
P4 for 16 observations.

Each 16-observation phase consists of:

two independent 8-observation blocks
whose exact means both equal the phase target.

After block 1:

working prior MUST remain previous value.

After block 2:

working prior may update to the phase target
only through the authorization path below.

REVERSE / RECOVERY PHASES

After P4:

P3 for 16 observations;
P2 for 16 observations;
P0 for 16 observations.

This tests:

reversible tracking;
non-monotonic drift;
return to the durable v2 anchor.

On final P0 confirmation:

working prior = P0;
durable C history remains [v1,v2].

No retraining of durable C versions occurs.

OBSERVATION GENERATOR

For scenario s,
phase label q,
block b,
pair k:

derive distinct roles a,b from:

SHA-256(
"YGG-A16-OBS|"
+ F16
+ "|"
+ decimal(s)
+ "|"
+ phase_label
+ "|"
+ decimal(block)
+ "|"
+ decimal(k)
).

For target prior p:

delta[a]=+1;
delta[b]=-1.

Emit:

p+delta;
p-delta.

Every block therefore has exact mean p.

PROVENANCE-QUALIFIED EXPERIENCE

Carry forward A14/A15 observation provenance.

Roots:

O0 = 1 << 52.
O1 = 1 << 53.
O2 = 1 << 54.
O3 = 1 << 55.

Every unique observation requires:

two distinct observation roots;
same observation digest;
same demand vector.

Same-root fanout does not qualify.

Physical copies do not increase evidence weight.

Distributed memory remains cellular.

No hidden central restore.

WORKING-STATE LEARNERS

Two independent learner lineages:

DEV_LEARNER_A_ROOT = 1 << 50.
DEV_LEARNER_B_ROOT = 1 << 51.

For every 8-observation block,
each learner independently reconstructs the qualified unique observations
in a separately derived deterministic order
and computes exact block mean.

A block candidate is usable only if:

Learner A mean == Learner B mean;
candidate belongs to frozen prior catalog.

WORKING-STATE AUTHORIZATION

A working update from current W to candidate Q may occur only if:

current context lineage == C;
no context boundary occurred;
slot count == 3;
durable C history == [v1,v2];
working-state parent digest matches current working digest;
two consecutive qualified blocks both mean Q;
Q belongs to frozen prior catalog;
Q differs from A/B/C-v1;
L1(Q,W) == 2,
EXCEPT final return to P0 where the path must follow the preregistered reverse sequence;
learner roots independent;
existing organism governance qualified;
existing registry qualification qualified.

The update changes only:

working prior;
working generation;
working digest;
evidence-window digest.

It does NOT change:

C-v1;
C-v2;
C durable active-version record;
context slots;
task programs.

DEVELOPMENTAL EFFECT

Existing cells are never forcibly respecialized.

Only future clean replacement cells
while context lineage C is active
use the current authorized working prior.

HELD-OUT SERVICE EVALUATION

After every successful working-state update,
run:

8 held-out service epochs

around that phase's target prior.

Generate:

4 independently derived zero-mean pairs.

Replacement episodes:

service epoch 0;
service epoch 4.

Each replaces four clean cells.

Candidate:

uses current working prior.

BASELINE STALE-V2:

always uses durable C-v2 / P0.

ORACLE:

uses current phase target prior.

Evaluate updates at:

P1;
P2;
P3;
P4;
reverse P3;
reverse P2;
return P0.

Seven held-out evaluation phases per scenario.

PRIMARY USEFULNESS

Across all non-P0 moving-drift evaluations:

candidate aggregate first-four service
>
STALE-V2 baseline aggregate.

Candidate >= stale-V2 in at least:

60 / 72 non-P0 scenario-evaluations

if 6 non-P0 evaluations x 12 scenarios = 72.

Candidate oracle efficiency >=:

0.98.

At least one migration avoided relative to stale-v2.

For final P0 return:

candidate service must match the durable-P0 oracle.

No persistent penalty may remain after return.

HYSTERESIS REQUIRED COUNTS

12 / 12 transient P1 one-block excursions:

NO working-state update.

12 / 12 transient returns to P0:

working generation remains 0.

Every true drift step:

no update after first 8-observation block.

Every true drift step:

update after second consistent block.

Expected authorized working updates per scenario:

7.

Expected final working prior:

P0.

Expected final working generation:

7.

DURABLE-HISTORY REQUIRED COUNTS

12 / 12:

C durable history remains [v1,v2].

12 / 12:

C-v1 digest unchanged.

12 / 12:

C-v2 digest unchanged.

12 / 12:

context slot count remains 3.

C-v3 creations:

0.

new context-slot creations:

0.

RESTART

Run one restart per scenario:

after the first 8-observation block of P3 forward drift
and before the second block.

Required:

one-block pending candidate survives;
working prior remains P2;
no premature update;
second P3 block produces the same authorized P3 working update;
eventual working path;
held-out outputs;
final return to P0

match uninterrupted shadow.

Run a dedicated second restart probe:

after P4 working update.

Required:

working prior P4;
working generation;
working digest;
durable history [v1,v2]

all survive exactly.

DEDICATED T8 PROBES

P1 — SINGLE BLOCK FLUCTUATION

One block around neighbor Q.

Required:

nomination allowed;
no working update.

P2 — FLUCTUATION REVERSION

One Q block,
then one current-W block.

Required:

pending Q clears;
W unchanged.

P3 — TWO CONSISTENT BLOCKS

Two Q blocks,
Q one-step neighbor of W.

Required:

working update authorized.

P4 — SAME-ROOT FANOUT

Required:

block observation not qualified.

P5 — LEARNER DISAGREEMENT

Learners derive different block means.

Required:

no update.

P6 — STALE WORKING PARENT

Correct candidate,
stale working parent digest.

Required:

no update.

P7 — CONTEXT BOUNDARY

Same candidate blocks after explicit context boundary.

Required:

not eligible to mutate C working state;
ABSTAIN / UNATTRIBUTED_UNKNOWN.

P8 — OUT-OF-STEP JUMP

Two stable blocks around a valid catalog prior
not adjacent to current working state
and not the preregistered next reverse step.

Required:

no working update.

P9 — DURABLE HISTORY IMMUTABILITY

After all working updates:

C-v1 and C-v2 records byte-identical to pre-A16.

P10 — CLEAR WORKING OVERLAY

Evaluator-authorized safety probe.

Clear working state to durable C-v2 anchor.

Required:

working prior = P0;
working generation resets only through explicit clear record;
durable history unchanged.

NEGATIVE / LIMIT CONTROLS

N1 — UPDATE AFTER ONE BLOCK

Unsafe.

Expected transient fluctuation can move developmental policy.

N2 — CREATE DURABLE VERSION PER WORKING STEP

Unsafe.

Expected version explosion.

N3 — CREATE NEW CONTEXT PER WORKING STEP

Unsafe.

Expected context proliferation / capacity pressure.

N4 — FORCE NEAREST PRIOR ON LARGE JUMP

Unsafe.

Expected unrelated niche can corrupt C working state.

N5 — SILENT WORKING-PARENT BYPASS

Unsafe.

Expected stale update / causal regression reachable.

N6 — FORGED OBSERVATION ROOT IDENTITIES

Boundary.

N7 — DRIFT FASTER THAN TWO-BLOCK HYSTERESIS

Boundary.

If the niche changes again before two consistent blocks exist,
A16 intentionally abstains rather than chase it.

N8 — MULTI-DIMENSIONAL NONLOCAL DRIFT

Boundary.

A16 tracks only the frozen local one-step path family.

PRIMARY SIGNAL

A16_T8_HYSTERETIC_MOVING_DRIFT_SUCCESS

TRUE iff:

12 / 12 single-block transient P1 excursions do not update
AND
12 / 12 transient P0 returns leave working generation 0
AND
all true drift steps abstain after block 1
AND
all true drift steps update after block 2
AND
all scenario working paths equal P0->P1->P2->P3->P4->P3->P2->P0
AND
final working prior == P0 in all scenarios
AND
final working generation == 7 in all scenarios
AND
C durable history remains [v1,v2] byte-identically in all scenarios
AND
context slot count remains 3
AND
C-v3 creations == 0
AND
new context-slot creations == 0
AND
candidate moving-drift aggregate service > stale-v2 aggregate
AND
candidate >= stale-v2 in at least 60 / 72 non-P0 evaluations
AND
candidate oracle efficiency >= 0.98
AND
at least one migration avoided
AND
final P0 service matches P0 oracle
AND
TASK_ACCURACY == 1.0
AND
incorrect served == 0
AND
stale-program served == 0
AND
all restart comparisons equivalent
AND
all P1..P10 probes pass
AND
N1..N5 expose unsafe shortcuts
AND
all existing constitutional safety totals remain zero.

N6..N8 are separately reported boundaries.

REPRODUCIBILITY

Two complete deterministic A16 primary sweeps.

Serialized outputs must be byte-identical.

Post-freeze:

P1..P4 path priors;
all evidence blocks;
attestation roots;
learner orders;
held-out moving-drift sequences;
replacement targets;
restart details

must be manifest-bound before primary execution.

NO POST-RESULT TUNING

After F16 exists,
do not alter:

- local path construction;
- 8-observation block size;
- two-block hysteresis;
- working-state authorization;
- working-parent digest rule;
- durable-history separation;
- service evaluations;
- stale-v2 baseline;
- oracle;
- thresholds;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A15 showed that Yggdrasil can save a stable revision as C version 2.

But a real environment may keep moving.

If Yggdrasil created:

C-v3,
C-v4,
C-v5

for every small change,
its memory would explode.

If it reacted to every brief fluctuation,
it would thrash.

A16 adds a smaller working memory for development.

A short-lived change is watched,
but does not immediately change how new cells develop.

If the same changed pattern persists for two evidence blocks,
the working developmental prior may move one bounded step.

That working state can keep following a gradual path
without creating another permanent context version.

The durable history stays:

C-v1;
C-v2.

Then the environment moves backward.

The working state must follow it back.

Finally the original C-v2 niche returns,
and the working state must land exactly back on the durable anchor.

So A16 tests:

STABLE MEMORY
->
TEMPORARY FLUCTUATION
->
DO NOT OVERREACT
->
SUSTAINED LOCAL DRIFT
->
BOUNDED WORKING-STATE ADAPTATION
->
REVERSE DRIFT
->
RETURN TO DURABLE ANCHOR

without context growth,
version explosion,
or historical erasure.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-IMPLEMENTATION PARENT-ANCHOR NORMALIZATION 01

DATE:
2026-09-21.

STATUS:
RECORDED BEFORE ANY A16 HARNESS COMMIT,
FREEZE,
PRIMARY MANIFEST,
OR PRIMARY EXECUTION.

The original preregistration references the first valid A15 closure commit:

e4b47d26825fcb23c37126d49ec9d363e2c7e73a.

A second append-only A15 closure was subsequently recorded at:

1bea52944ed3b836c6dc6612c73e5e430b69bd2d.

Both record the same accepted frozen A15 scientific result:

A15 source SHA-256:
4dfd8814c869380317bb90d8baf68f79f4c2ce9874db7bc9278546b56001c071;

F15:
dd9cd2cfee331d94631af17b0f0a61684e5091a4;

manifest:
0e7d6c14cff50e8e8705cbf4082d5f333267b2e4646eea333559db4b4b28cef9;

primary result:
494b3096e407790a341d66ee37833546b5ce50e2a88a2308a17c1c5bfb0941d3.

For sequence provenance,
A16 uses the latest accepted closure commit:

1bea52944ed3b836c6dc6612c73e5e430b69bd2d.

This normalization changes no T8 scientific question,
moving-drift path,
threshold,
probe,
control,
or primary signal.

No A16 scientific result has been observed.

canonical_scientific_execution = false.
stab18_r1_touched = false.
