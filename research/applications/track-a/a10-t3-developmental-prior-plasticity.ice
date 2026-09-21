TITLE: YGGDRASIL TRAINING TRACK T3 / APPLICATION A10 — Experience-Dependent Developmental Prior Plasticity
DATE: 2026-09-21
STATUS: PREREGISTERED / FIRST DEVELOPMENTAL-POLICY TRAINING GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T3 / APPLICATION-A
PARENT: A09 Distributed Cellular Training Memory
BRANCH: dg1a-ar

PURPOSE

A07-A09 established:

experience can produce a learned task program;
noisy experience can be provenance-qualified;
training memory can persist as distributed cell-local state;
learned program state can become hereditary without bypassing governance.

Those experiments changed what a role computes.

A10 asks the next question:

CAN EXPERIENCE CHANGE A BOUNDED DEVELOPMENTAL POLICY
THAT ALTERS HOW FUTURE / REPLACEMENT CELLS SPECIALIZE,
WHILE TASK PROGRAMS AND CONSTITUTIONAL SAFETY REMAIN FROZEN?

A10 does NOT change task semantics.

It learns one reversible developmental parameter:

the role-allocation prior used when a newly created replacement cell must choose its role.

BOUNDARY

Synthetic software only.
No production deployment.
No network exposure.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

T3 CLAIM

A10 is the first bounded developmental-policy plasticity test.

It does not claim:

open-ended self-modification;
arbitrary code generation;
mutation of constitutional rules;
mutation of governance thresholds;
mutation of provenance rules;
mutation of repair authority;
mutation of task-program semantics.

The only trainable developmental state is:

ROLE_PRIOR = (p0,p1,p2,p3).

ROLE-PRIOR CATALOG

Each prior is an integer quadruple satisfying:

p0+p1+p2+p3 = 12;
1 <= each pi <= 6;
max(pi)-min(pi) >= 2.

Sorted lexicographically.

Expected catalog size:

124.

The untrained baseline prior is:

(3,3,3,3).

No learned prior may equal the baseline prior.

DEVELOPMENTAL EFFECT

The role prior affects ONLY newly created clean replacement cells.

Existing cells do not change role because the prior changed.

For a new replacement cell:

1. inspect current healthy non-corrupted role counts;
2. compute deficit[r] = max(0, ROLE_PRIOR[r] - current_count[r]);
3. choose the role with largest deficit;
4. ties -> lowest role index;
5. if every deficit is zero:
   choose the role with smallest current count;
   ties -> lowest role index.

The new cell then inherits the current authoritative task program for that role
through the existing A06 hereditary program path.

Existing migration,
hibernation,
reactivation,
repair,
partition,
re-merge,
program authority,
and stale-program exclusion remain unchanged.

FROZEN PARENT

A09 source SHA-256:

9b508deb63c8c923b9ec300831446dcf68b2d9de6c9a76506449a277c7f72162.

A09 freeze F09:

db770987c53e623bb86ad229cac3252388f50cc2.

A09 memory-stress manifest:

8600dd8ff89d7190cf5f4c2c825442dc95e6c7f7803a759d8f8054e37510c6e7.

A09 accepted primary result:

1fa4b91eb629cc7a3757d3e6317b425981d5d709703369864029f8c772d0ec2b.

A08 experience-provenance rules,
A09 distributed-memory identity,
A06 program inheritance,
and the constitutional governance / registry path remain frozen.

POST-FREEZE LATENT DEVELOPMENTAL NICHE

No primary developmental prior may exist before A10 freeze.

Let F10 be the exact commit that freezes the A10 harness.

For scenario s:

derive:

SHA-256(
"YGG-A10-PRIOR|"
+ F10
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
).

Map deterministically into the 124-entry role-prior catalog.

Reject only:

(3,3,3,3)

which is not in the catalog under the max-min rule,
therefore the expected derivation counter is 0.

The selected latent prior is evaluator-hidden.

The organism never receives it directly.

TRAINING EXPERIENCE

Each scenario receives 64 developmental-observation epochs.

Each observation is a 12-request role-demand vector.

The hidden prior determines the mean role demand.

For training-pair index k = 0..31:

derive two distinct roles a,b from:

SHA-256(
"YGG-A10-TRAIN-PAIR|"
+ F10
+ "|"
+ decimal(s)
+ "|"
+ decimal(k)
).

Epoch 2k:

start from latent prior;
if prior[a] > 1 and prior[b] < 6:
move one request a -> b;
otherwise use the first lexicographically valid distinct role pair.

Epoch 2k+1:

apply the exact inverse perturbation b -> a.

Therefore each two-epoch pair has mean exactly equal to the hidden latent prior.

Across all 64 training epochs:

the exact arithmetic mean role demand equals the latent prior.

The learner sees only the 64 observed demand vectors.

It does not receive:

latent prior;
pair identity;
future evaluation demands;
future replacement targets;
oracle allocation.

DISTRIBUTED EXPERIENCE MEMORY

Each training demand vector becomes one unique developmental-observation shard.

Shard identity includes:

scenario;
training epoch;
demand vector;
causal event id.

A09 storage rules apply:

two-neighborhood physical replication;
copy identity != evidence identity;
no central ledger restore;
restart persistence;
physical copy fanout does not increase effective observation count.

Exactly 64 unique developmental observation shards must exist per scenario.

DEVELOPMENTAL LEARNERS

Two learner lineages:

DEV_LEARNER_A_ROOT = 1 << 50.
DEV_LEARNER_B_ROOT = 1 << 51.

Each learner independently reconstructs the 64 unique training observations
from distributed cell memory in a separately derived deterministic order.

For learner L:

order key =
SHA-256(
"YGG-A10-LEARNER-ORDER|"
+ F10
+ "|"
+ decimal(s)
+ "|"
+ learner_id
+ "|"
+ decimal(training_epoch)
).

Each learner computes:

role_total[r] = sum observed demand[r] across 64 unique observations.

candidate_prior[r] = role_total[r] / 64.

A candidate is valid only if:

every role_total[r] is divisible by 64;
the resulting tuple belongs to the frozen 124-prior catalog.

No rounding is allowed.

Thus duplicate physical copies cannot bias the learned prior.

AUTHORIZATION

A developmental-prior candidate may become authoritative only if:

Learner A candidate == Learner B candidate;
learner roots are pairwise disjoint;
candidate belongs to frozen role-prior catalog;
candidate differs from current authoritative prior;
parent developmental-policy digest matches current authoritative developmental policy;
developmental-policy version increments exactly by one;
existing organism governance passes;
existing registry qualification passes.

The developmental-policy record contains:

version;
role prior;
parent digest;
policy digest;
commit epoch.

The commit is versioned and reversible.

No constitutional rule is modified.

TRAIN / EVALUATION SEPARATION

Training uses 64 observation epochs.

Held-out evaluation uses a separately derived 64-epoch sequence.

For evaluation-pair index k = 0..31:

derive a,b independently from:

SHA-256(
"YGG-A10-EVAL-PAIR|"
+ F10
+ "|"
+ decimal(s)
+ "|"
+ decimal(k)
).

Use the same balanced inverse-pair construction around the latent prior.

Therefore:

evaluation mean == latent prior

but

exact evaluation sequence is never observed during training.

No evaluation observation may enter learner memory before policy commit.

DEVELOPMENTAL TURNOVER TEST

After successful developmental-policy commit,
run four replacement episodes during the 64-epoch held-out evaluation.

Replacement episode starts:

0;
16;
32;
48.

At each episode:

replace exactly four deterministic cells.

Replacement target order is derived post-freeze from:

SHA-256(
"YGG-A10-REPLACEMENT|"
+ F10
+ "|"
+ decimal(s)
+ "|"
+ decimal(episode)
).

Replacement cells are CLEAN NEW CELLS:

no inherited role;
no inherited training-memory shards;
no governance slot;
no stale task program.

Each receives:

new lineage root;
role selected by current authoritative ROLE_PRIOR;
current authoritative task program for that selected role.

Normal governance-slot repair / reassignment may occur through existing rules.

No hidden evaluator state is copied into replacement cells.

BASELINES

BASELINE A — UNTRAINED DEVELOPMENTAL PRIOR

Use:

(3,3,3,3).

Same evaluation demand.
Same replacement targets.
Same task programs.
Same migration rules.
Same faults / resource rules if present.

BASELINE B — NO DEVELOPMENTAL LEARNING

Keep the original authoritative prior for all replacement events.

ORACLE

Evaluator-only.

Uses the hidden latent prior directly for replacement role choice.

Oracle is a ceiling,
not organism authority.

PRIMARY DEVELOPMENTAL METRICS

Per scenario report:

latent prior;
learner A prior;
learner B prior;
learner agreement;
training observation count;
distributed-memory copy statistics;
policy commit result;
developmental policy version / digest;
replacement cell ids;
assigned replacement roles;
post-replacement first-epoch served requests;
post-replacement 4-epoch served requests;
role migrations triggered after replacement;
migration service-cost epochs;
candidate service total;
baseline service total;
oracle service total;
task accuracy;
stale-program service;
restart equivalence.

PRIMARY REQUIRED LEARNING SIGNALS

12 / 12 Learner A exact latent prior.

12 / 12 Learner B exact latent prior.

12 / 12 learner agreement.

12 / 12 developmental-policy commits.

64 / 64 unique developmental observations reconstructed per scenario.

Physical replication never changes the arithmetic mean.

DEVELOPMENTAL EFFECT SIGNAL

For every replacement episode:

the four newly created cells must receive roles using the committed developmental prior.

At least one replacement role assignment across the family must differ from the untrained (3,3,3,3) baseline.

At least one post-replacement migration must be avoided relative to baseline.

USEFULNESS SIGNAL

Across all scenarios and replacement episodes:

candidate first-4-epoch served requests
>
untrained baseline first-4-epoch served requests.

Candidate must beat or equal baseline in at least:

10 / 12 scenarios.

No scenario may have:

incorrect served requests > 0.

Report any scenario where candidate service is below baseline.

Candidate must reach at least:

0.97

of oracle first-4-epoch service.

The oracle uses only the hidden prior for replacement role assignment;
normal migration cost still applies afterward.

PERSISTENCE

Restart once after developmental-policy commit and before the second replacement episode.

Required:

authoritative developmental-policy version / digest;
replacement-role decisions;
service outputs;
and cumulative metrics

match uninterrupted shadow exactly.

HEREDITARY / CELLULAR MEMORY

A replacement cell must not inherit old training-memory shards.

Distributed developmental-experience memory persists only through surviving legitimate shard copies.

The authoritative developmental prior persists through its versioned policy record,
not by copying evaluator state into new cells.

DEDICATED T3 PROBES

P1 — DUPLICATE MEMORY BIAS

Replicate one developmental observation shard to all 12 cells.

Required:

learned prior unchanged.

P2 — INCOMPLETE TRAINING MEMORY

Remove every physical copy of one not-yet-consumed training observation.

Required:

learner cannot produce a complete 64-observation mean;
developmental-policy commit abstains.

P3 — LEARNER DISAGREEMENT

Feed Learner B one forged unique developmental observation.

Required:

candidate priors disagree;
no commit.

P4 — GOVERNANCE UNAVAILABLE

Both learners derive the same correct prior,
but governance / registry is unavailable.

Required:

no developmental-policy commit.

P5 — CLEAN REPLACEMENT CELL

Replace a shard-bearing cell.

Required:

new cell starts with no old training memory;
role comes only from authoritative developmental prior;
task program comes only from current authoritative role program.

P6 — POLICY ROLLBACK

Evaluator-controlled safety probe.

Commit version 1,
then apply an authorized rollback to version 0.

Required:

future replacement cells again use baseline prior;
existing cells are not forcibly re-specialized.

This proves bounded reversibility.

NEGATIVE / LIMIT CONTROLS

N1 — DIRECT LATENT-PRIOR INJECTION

Unsafe control.

Give the learner the hidden prior directly.

Expected:

trivial success;
invalid as training evidence.

N2 — COPY-COUNT AVERAGING

Unsafe control.

Let physical replicas contribute repeatedly to the arithmetic mean.

Expected:

replication can bias learned developmental policy.

N3 — AUTO-COMMIT ONE LEARNER

Unsafe control.

Allow one learner candidate to update developmental policy.

Expected:

single-lineage false policy authority reachable under one forged observation.

N4 — NONSTATIONARY NICHE

Boundary.

Training mean prior and held-out evaluation mean prior are intentionally different.

Expected:

the learned prior may become maladaptive.

This defines the first T3 stationarity boundary.

N5 — CONSTITUTIONAL SELF-MODIFICATION

Forbidden control.

No experiment path may alter:

governance threshold;
registry threshold;
provenance identity;
repair authority;
stale-program exclusion;
partition / re-merge rules.

PRIMARY SIGNAL

A10_T3_DEVELOPMENTAL_PRIOR_LEARNING_SUCCESS

TRUE iff:

12 / 12 Learner A exact priors
AND
12 / 12 Learner B exact priors
AND
12 / 12 learner agreement
AND
12 / 12 developmental-policy commits
AND
all 64 unique developmental observations per scenario are reconstructed
AND
physical memory replication never changes learned evidence weight
AND
candidate first-4-epoch post-replacement service > baseline aggregate
AND
candidate >= baseline in at least 10 / 12 scenarios
AND
candidate oracle efficiency >= 0.97
AND
at least one baseline migration is avoided
AND
TASK_ACCURACY == 1.0
AND
incorrect served requests == 0
AND
stale-program served requests == 0
AND
all restart comparisons are equivalent
AND
all P1..P6 probes pass
AND
N1..N3 expose unsafe shortcuts
AND
all existing constitutional safety totals remain zero.

N4 is reported separately as a stationarity boundary.

REPRODUCIBILITY

Two complete deterministic A10 primary sweeps.

Serialized result SHA-256 must match exactly.

Post-freeze latent-prior,
training-pair,
evaluation-pair,
learner-order,
and replacement manifests
must match exactly.

NO POST-RESULT TUNING

After F10 exists,
do not alter:

- 124-prior catalog;
- 64 training observations;
- inverse-pair generator;
- 64 held-out evaluation observations;
- developmental learner roots;
- exact-mean learner;
- developmental-policy authorization;
- birth-role assignment rule;
- four replacement episodes;
- baseline;
- oracle;
- usefulness thresholds;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

Up to A09,
Yggdrasil learned what a job should compute.

A10 changes something deeper.

The organism watches what kinds of jobs its environment repeatedly needs.

From that experience,
it learns a developmental bias for how many cells of each role are usually useful.

That learned bias does not rearrange the current population by decree.

Instead,
it changes how future replacement cells develop.

When a clean new cell appears,
the organism asks:

"given what we learned about this environment,
which role is this new cell most needed for?"

The future test sequence is withheld during training.

If the learned developmental prior is useful,
new cells should be born into better roles,
reducing the amount of later role migration needed after turnover.

The task programs themselves do not change.

The governance rules do not change.

The repair rules do not change.

Only one bounded,
versioned,
reversible developmental parameter is allowed to learn.

That makes A10 the first test of:

EXPERIENCE
->
PERSISTENT CHANGE IN HOW FUTURE CELLS DEVELOP.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-IMPLEMENTATION PREREGISTRATION CORRECTION 01 — EXACT ZERO-MEAN DEMAND PAIRS

DATE:
2026-09-21.

STATUS:
CORRECTED BEFORE ANY A10 HARNESS COMMIT,
FREEZE,
MECHANICAL PRIMARY,
OR SCIENTIFIC EXECUTION.

ISSUE

The original pair wording said:

epoch 2k:
move one request a -> b;

epoch 2k+1:
apply the exact inverse perturbation b -> a.

Read literally as a sequential operation,
the second epoch would return to the latent prior.

The two-epoch arithmetic mean would therefore not equal the latent prior,
contradicting the explicit preregistered invariant.

CORRECTED FROZEN PAIR RULE

For every training or evaluation pair,
derive two DISTINCT role indices a,b.

Let p be the latent prior.

Define delta:

delta[a] = +1;
delta[b] = -1;
all other components = 0.

The two demand vectors are:

v_even = p + delta.

v_odd = p - delta.

Because every latent-prior component is in 1..6:

every generated demand component lies in 0..7.

Both vectors still sum to:

12.

And exactly:

(v_even + v_odd) / 2 = p.

No fallback role-pair substitution is required.

Role-pair derivation remains post-freeze and deterministic.

This correction changes no:

catalog;
learner;
authorization rule;
replacement rule;
baseline;
oracle;
threshold;
probe;
control;
or primary signal.

No A10 result has been observed.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A10 T3 DEVELOPMENTAL PRIOR PLASTICITY

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A10 LATENT PRIOR,
TRAINING SEQUENCE,
EVALUATION SEQUENCE,
LEARNER ORDER,
OR REPLACEMENT PLAN.

IMPLEMENTATION COMMIT

bc2bfd0456b475f081950305b8cd6c075dfedb4d.

SOURCE BUNDLE

Loader:

research/applications/track-a/a10_t3_developmental_prior_v1.py

Loader Git blob:

f62c1ffadc384b8746269f1a52cafb7b1906bbb1.

Payload:

research/applications/track-a/a10_t3_developmental_prior_v1.py.gz

Payload Git blob:

bcbb0e864d5acb71025c3fcb92bfb38d3c64f20c.

Compressed payload SHA-256:

7c655aa5910e0645d3bea880dae215107b0e5ec986613706661873bc420fa248.

Compressed payload bytes:

8199.

Decompressed exact source SHA-256:

d27d0074f08b6ae613e72a03d018af6b4bda9fd7dffb9615c687c286aca5e73e.

Decompressed source bytes:

26838.

FROZEN PARENT

A09 source SHA-256:

9b508deb63c8c923b9ec300831446dcf68b2d9de6c9a76506449a277c7f72162.

A09 freeze:

db770987c53e623bb86ad229cac3252388f50cc2.

A09 memory-stress manifest:

8600dd8ff89d7190cf5f4c2c825442dc95e6c7f7803a759d8f8054e37510c6e7.

A09 accepted primary result:

1fa4b91eb629cc7a3757d3e6317b425981d5d709703369864029f8c772d0ec2b.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Role-prior catalog size:

124.

Mechanical manifest SHA-256:

1d3e0ffba65c9755bcb610c5419e9753926d4714f686103a4f6525e866ff9c19.

Exact zero-mean training pairs:

PASS.

Exact zero-mean held-out evaluation pairs:

PASS.

64 training observations per scenario:

PASS.

64 held-out evaluation observations per scenario:

PASS.

Distributed developmental-memory reconstruction:

PASS.

Mechanical full T3 smoke used only:

MECHANICAL-NONPRIMARY-FREEZE.

Mechanical smoke summary:

12 / 12 Learner A exact developmental priors;
12 / 12 Learner B exact developmental priors;
12 / 12 learner agreement;
12 / 12 developmental-policy commits;
1977 candidate first-four-epoch served requests;
1893 untrained-baseline first-four-epoch served requests;
1977 evaluator-oracle first-four-epoch served requests;
candidate >= baseline in 11 / 12 scenarios;
24 baseline migrations avoided;
candidate incorrect = 0;
stale-program served = 0;
all restart checks equivalent;
all T3 probes PASS;
all unsafe controls exposed;
all existing constitutional safety totals = 0.

These results use the literal fake mechanical freeze label.

They are implementation checks only.

They are NOT A10 scientific evidence.

PRIMARY STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting commit SHA of this freeze update be F10.

Only after F10 exists may the harness derive:

- 12 latent developmental priors;
- 12 x 64 training demand observations;
- 12 x 64 held-out evaluation demands;
- learner A / B observation orders;
- four replacement target sets per scenario.

No primary developmental prior or evaluation sequence has been observed.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
