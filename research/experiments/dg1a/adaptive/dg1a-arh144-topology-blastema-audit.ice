TITLE: DG-1A-AR-H144 — Topology Blastema / De-Novo Re-Development Gate Audit Preregistration
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / UNEXECUTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh143-adaptive-topology-repair-audit.ice

PURPOSE

H143 separated two structural problems:

LOCAL TOPOLOGY ADAPTATION

from:

TOPOLOGY REGENERATION.

The frozen H143 incremental system could repair:
isolated persistent split
and:
isolated persistent merge.

It could not repair:
25% stored-membership damage.

Doubling evidence to:
4N pairs/episode

did not rescue that failure.

Yet:

de-novo relational reconstruction
using the same bounded evidence

recovered:

the correct number of groups
and:
ARI = 1.0

in the H143 exploratory damage probes.

Thus:

THE EVIDENCE
WAS PRESENT.

THE ACCEPTED TOPOLOGY
WAS THE BAD PRIOR.

H144 asks:

WHEN
SHOULD
THE ORGANISM
STOP
PATCHING
THE CURRENT SCAFFOLD

AND:

TEMPORARILY
RE-DEVELOP
TOPOLOGY
FROM
RELATIONAL EVIDENCE?

BOUNDARY

Synthetic research only.

The term:

BLASTEMA

is architectural shorthand for:

A TEMPORARY,
BOUNDED,
DE-NOVO
STRUCTURAL RECONSTRUCTION LANE.

It does not mean:
living tissue
or:
biological implementation.

H144 does not:
- implement biological tissue;
- claim biological equivalence;
- establish production topology thresholds;
- execute or modify STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

EVIDENCE CLASS TARGET

SYNTHETIC
MEASURED_SANDBOX
LONGITUDINAL

CORE ARCHITECTURE

NORMAL MODE

Use:
H143-style bounded incremental repair.

Allowed operations:

- reassign;
- split;
- merge;
- quarantine;
- candidate hibernation.

NORMAL MODE assumes:

MOST
OF THE
ACCEPTED TOPOLOGY
IS STILL USEFUL.

BLASTEMA MODE

Temporarily stop using accepted memberships as:
candidate-generation anchors.

Preserve:

- member identities;
- member state;
- decaying relational evidence;
- action history;
- old accepted topology as hibernating fallback.

Construct:

A DE-NOVO
CANDIDATE PARTITION

from:

RELATIONAL EVIDENCE ONLY.

No current membership assignment
may seed:
the scratch partition.

GROUP-COUNT INFERENCE

Primary de-novo candidate:

1. construct a confidence-weighted positive relational affinity graph;
2. compute the normalized graph Laplacian;
3. evaluate eigengaps over:
K = 3..8;
4. choose the largest admissible eigengap;
5. construct:
a spectral candidate partition.

No latent true K is supplied.

PRIMARY BLASTEMA TRIGGER

Enter blastema-candidate mode when ANY:

A.
quarantine fraction >= 0.35;

B.
weighted relational disagreement >= 0.25;

C.
UNKNOWN / erased stored membership fraction >= 0.10;

D.
incremental repair has remained alarmed
for >= 6 episodes
without:
>=0.05 ARI-equivalent relational-objective improvement.

Criterion D is evaluated only from:
observable relational objective,
not:
latent ARI.

TRIGGER HYSTERESIS

Blastema entry requires:

two consecutive trigger checkpoints

except:

UNKNOWN fraction >= 0.20

which may trigger immediately.

Trigger checkpoints:

every 3 episodes.

BLASTEMA ACTION BOUNDARY

While a de-novo candidate is immature:

family/subfamily broadcast is frozen.

Allowed:

- direct local action;
- evidence acquisition;
- candidate evaluation.

This intentionally trades:
coverage

for:
structural safety.

CANDIDATE VALIDATION

The scratch candidate does not gain authority
from:
its reconstruction score alone.

It must pass:
fresh post-construction pair evidence.

Primary validation window:

2 consecutive checkpoints.

At each checkpoint:

fresh pair evidence
not used to fit that checkpoint's candidate

must show:

candidate relational prediction error

at least:

0.08 absolute

better than:

the currently accepted topology.

Additional requirements:

- no candidate region smaller than 5;
- inferred K in:
3..8;
- candidate partition remains similar across the two checkpoints:
ARI(candidate_t, candidate_t+1) >= 0.90.

Only then:

PROMOTE
THE DE-NOVO TOPOLOGY.

Old topology becomes:
a hibernating fallback

for:
10 episodes.

If:
new topology immediately fails its relational validation

during fallback window:

revert
and:
remain local.

PRIMARY POLICIES

A — INCREMENTAL-ONLY

H143 REGENERATIVE comparator.

Never performs:
scratch reconstruction.

B — PERIODIC-SCRATCH

Every 6 episodes:

build:
a de-novo candidate

whether needed or not.

Uses:
the same validation gate.

This is:
the active-compute comparator.

C — SCRATCH-WITHOUT-HOLDOUT

Uses the blastema trigger

but:
promotes a scratch candidate from:
fit evidence only

without:
fresh validation.

Negative comparator for:
structural overfitting.

D — TRIGGERED-BLASTEMA

Normal mode:
H143 DUAL/HYSTERETIC incremental repair.

When the frozen blastema trigger fires:

- freeze broad action;
- build de-novo candidate;
- validate on fresh evidence;
- promote only after two consistent passing checkpoints;
- retain old topology as bounded fallback.

E — ORACLE-DAMAGE-MODE-SWITCH

Synthetic reference only.

Enters blastema mode exactly when:

stored topology damage is injected.

Still must:
infer K
and:
pass candidate validation.

This is not deployable.

It measures:
the cost of imperfect trigger detection.

PRIMARY ECOLOGY

Family size:
60..100.

Initial true subfamilies:
4..6.

Initial stored-label corruption:
10%.

Episode horizon:
80.

Active fraction:
20%..50% per episode.

Primary pair-evidence budget:
2N observations/episode.

Sensor error:
5%.

Evidence decay:
0.92.

PRIMARY REGIMES

R0 — STABLE

No structural event.

R1 — ISOLATED SPLIT

Episode 21:
real near-equal split.

R2 — ISOLATED MERGE

Episode 21:
real merge.

R3 — DAMAGE-10

Episode 21:
10% stored membership damage.

R4 — DAMAGE-25

Episode 21:
25% stored membership damage.

R5 — DAMAGE-40

Episode 21:
40% stored membership damage.

R6 — TRANSIENT FALSE SHIFT

Episodes 21..25:
observation process mimics:
a split or merge.

True topology remains unchanged.

R7 — STACKED

Same hard sequence as H143:

episode 21:
real split.

episode 36:
25% stored topology damage.

episode 51:
real merge.

episodes 66..70:
transient false shift.

PRIMARY CONFIRMATION SIZE

48 held-out worlds per regime.

8 regimes.

384 primary worlds.

COMMON-WORLD DISCIPLINE

Within each world:

all policies receive:

- the same true structural events;
- the same active schedule;
- the same potential sensor outcomes for identical queried pairs.

Policies may query different pairs
because:
their topology state differs.

PRIMARY METRICS

1. ARI / partition agreement;
2. pairwise partition accuracy;
3. quarantined fraction;
4. active safe-action coverage;
5. cross-boundary false-promotion proxy;
6. blastema-entry rate;
7. false blastema-entry rate;
8. de-novo candidate promotion rate;
9. candidate rejection rate;
10. promotion latency after damage;
11. structural recovery latency;
12. scratch candidate-build count;
13. active topology compute;
14. dormant fallback storage;
15. rollback rate;
16. false structural promotion under transient shift.

PRIMARY ACCEPTANCE SHAPE

The topology-blastema thesis is supported if:

- TRIGGERED-BLASTEMA materially outperforms INCREMENTAL-ONLY after DAMAGE-25;
- DAMAGE-25 mean ARI returns to >=0.75 within 20 post-damage episodes in a majority of TRIGGERED-BLASTEMA worlds;
- DAMAGE-40 shows substantial recovery rather than permanent collapse;
- STACKED final ARI is materially above the H143 REGENERATIVE reference:
0.303;
- quarantine after damage is materially lower than H143 REGENERATIVE;
- stable/split/merge regimes do not cause frequent unnecessary blastema promotion;
- transient false shift does not produce >5% harmful de-novo promotions;
- scratch candidate validation materially reduces false promotion relative to SCRATCH-WITHOUT-HOLDOUT;
- TRIGGERED-BLASTEMA performs materially fewer scratch builds than PERIODIC-SCRATCH;
- no latent K or original membership labels are used for reconstruction;
- primary recovery remains possible at <=2N pair evidence/episode.

FAILURE CONDITIONS

Treat H144 as mixed/negative if:

- de-novo recovery requires latent K;
- trigger misses most real damage;
- trigger fires constantly during ordinary split/merge adaptation;
- blastema becomes a permanently active parallel topology engine;
- fresh validation does not protect against transient false shifts;
- inferred K becomes unstable;
- scratch promotion frequently fragments or merges the wrong regions;
- broad action freeze produces persistent coverage collapse after correct reconstruction;
- recovery only works because old labels leak into candidate generation.

ROBUSTNESS

Evidence budget:
0.5N,
N,
2N,
4N.

Sensor error:
1%,
5%,
10%,
20%.

Damage:
10%,
25%,
40%,
60%.

True K:
3..8.

Unequal region sizes:
low,
medium,
high imbalance.

Relational graph sparsity:
uniform,
active-biased,
quarantine-biased.

Blastema trigger thresholds:
one-at-a-time sensitivity only.

Candidate validation margin:
0.04,
0.08,
0.12.

Candidate stability requirement:
one,
two,
three checkpoints.

OUT-OF-BOX EXTENSION

The architectural analogy is:

PATCH MODE

versus:

RE-DEVELOPMENT MODE.

A system should not assume:

THE STRUCTURE
USED TO INTERPRET EVIDENCE

IS ALWAYS
THE STRUCTURE
THAT SHOULD
BE REPAIRED.

At high enough scaffold distrust:

THE SCAFFOLD ITSELF
MUST BECOME
A HYPOTHESIS.

This produces:

MEMBER STATE
+
RELATIONAL EVIDENCE

as:
the regenerative substrate,

while:

TOPOLOGY

becomes:
a replaceable developmental phenotype.

FROZEN BEFORE EXECUTION

Blastema meaning,
normal mode,
scratch reconstruction rule,
K inference,
triggers,
promotion validation,
fallback behavior,
policies,
ecology,
regimes,
primary confirmation size,
metrics,
acceptance shape,
and failure conditions above

are fixed before synthetic execution.

Do not execute STAB-18-R1 during this lane.

PROVENANCE

evidence_class_target = SYNTHETIC_MEASURED_SANDBOX_LONGITUDINAL
canonical_scientific_execution = false
canonical_r1_execution_spent = false
preregistered_from_head = e65e5d12b10dbeee4434203420cba5233b1700d2


IMPLEMENTATION FREEZE — BEFORE H144 EXECUTION

The following previously-unspecified mechanics are fixed before any H144 primary result is accepted.

NORMAL-MODE INCREMENTAL LANE

Reuse the frozen H143 DUAL/HYSTERETIC mechanics unchanged:

- evidence decay 0.92;
- <=2N pair observations/episode;
- H143 pair-sampling mixture;
- H143 reassign/split/merge candidate thresholds;
- three candidate checkpoints for incremental structural acceptance;
- five-episode incremental cooldown;
- bounded one-candidate hibernation.

INITIAL / DAMAGE REALIZATION

Initial stored topology:
10% membership corruption.

Damage events reuse the H143 realization:

selected stored memberships are:
- erased to UNKNOWN for approximately one-third;
- reassigned to an incorrect known region otherwise.

RELATIONAL AFFINITY FOR SCRATCH RECONSTRUCTION

For pair i,j:

p_ij =
decayed observed same-family mass
/
decayed total observation mass.

c_ij =
1 - exp(-total_mass / 3).

Positive affinity:

A_ij =
max(0, 2*(p_ij - 0.5)) * c_ij.

Diagonal:
1.

Unobserved pairs:
0 off-diagonal affinity.

K INFERENCE

Construct normalized Laplacian from:
A.

For K = 3..8:

compute:
lambda_(K+1) - lambda_K

using ascending Laplacian eigenvalues.

Choose:
the K with the largest admissible eigengap.

Then:

spectral clustering
with:
the inferred K

constructs the scratch candidate.

No accepted membership label:
seeds
or:
constrains
this clustering.

BLASTEMA TRIGGER IMPLEMENTATION

At every third episode:

measure:

Q =
current quarantine fraction.

D =
current weighted relational disagreement.

U =
current UNKNOWN membership fraction.

Maintain:
alarm episode count.

A checkpoint is trigger-positive when:

Q >= 0.35
OR
D >= 0.25
OR
U >= 0.10
OR
the lane has remained H143-alarmed for >=6 consecutive episodes
without at least 0.05 reduction in weighted relational disagreement.

Ordinary trigger-positive state must persist for:
two consecutive checkpoints.

If:
U >= 0.20

blastema mode may enter immediately.

FRESH VALIDATION BUFFER

Once a scratch candidate is built:

ordinary post-build queried pair observations are copied into:
a validation-only buffer

before:
those later observations may influence the next scratch candidate.

For each fresh observation:

candidate error =
1
when:
candidate same/different prediction
disagrees with:
fresh observed relation;

else:
0.

Accepted-topology error:
same definition.

A checkpoint passes the validation margin when:

accepted_error
-
candidate_error
>= 0.08.

No pre-build pair observation can count as:
fresh validation evidence.

TWO-CHECKPOINT PROMOTION

At checkpoint t:

build:
candidate C_t.

At checkpoint t+3:

1. score C_t on fresh validation evidence;
2. build:
new scratch candidate C_(t+3);
3. require:
ARI(C_t, C_(t+3)) >= 0.90.

This can produce:
validation pass 1.

At checkpoint t+6:

repeat with:
C_(t+3).

Promotion requires:
two consecutive validation/stability passes.

Thus:
minimum ordinary blastema maturation time
after first candidate construction

is:
6 episodes.

MINIMUM VALIDATION SUPPORT

A validation checkpoint is informative only when:

at least:
20 fresh pair observations

are present.

Otherwise:
no pass is awarded.

SCRATCH-WITHOUT-HOLDOUT

Uses the same:
trigger
and:
scratch construction.

It promotes:
the first admissible scratch candidate immediately

without:
fresh validation.

PERIODIC-SCRATCH

Attempts scratch reconstruction every:
6 episodes

while not already validating a candidate.

It uses:
the same two-checkpoint validation gate.

ORACLE-DAMAGE-MODE-SWITCH

Enters blastema mode:
at the exact synthetic damage event.

It receives:
no latent K
and:
no original labels.

ROLLBACK

After scratch promotion:

retain old accepted topology for:
10 episodes.

At each third-episode checkpoint during fallback:

use fresh post-promotion validation evidence.

Rollback occurs if:

old_topology_error
+
0.08
<=
new_topology_error.

After rollback:

remain local
until:
a new blastema candidate independently matures.

ACTION-COVERAGE ACCOUNTING

While blastema candidate is immature:

broad action is frozen.

For coverage accounting:

one active triggering member
may be resolved locally.

Thus blastema immature coverage is:

1 / current_active_count.

After promotion or in normal mode:

use:
the H143 quarantine-defined action core.

ACTIVE TOPOLOGY COMPUTE

One unit:

one H143 incremental candidate-generation pass.

One scratch-build unit:

one full affinity + eigengap + spectral candidate reconstruction.

These are recorded separately.

Primary comparison of:
TRIGGERED-BLASTEMA
versus:
PERIODIC-SCRATCH

uses:
scratch-build count

as the main re-development compute metric.

PRIMARY EXECUTION SEEDS

Each regime uses:
48 held-out worlds.

No H143 primary,
control,
or exploratory seed
is reused.

No trigger,
affinity,
validation,
promotion,
or rollback threshold
will change after H144 primary execution begins.


IMPLEMENTATION FREEZE ADDENDUM — CANDIDATE ABANDONMENT

Harness-only validation exposed a lifecycle ambiguity:

a scratch candidate that is merely:
equivalent to
an already-good accepted topology

cannot satisfy:
the frozen +0.08 validation improvement margin.

Without an explicit exit rule,
PERIODIC-SCRATCH could remain:
indefinitely frozen

despite:
no evidence of structural damage.

The following lifecycle rule is fixed before primary execution.

VALIDATION FAILURE COUNT

A blastema candidate accrues:
one failure

when a validation checkpoint is informative
but fails either:

- +0.08 fresh-error improvement;
- ARI(candidate_t, candidate_t+1) >=0.90 stability.

After:
2 consecutive informative failures

the current scratch candidate is:
REJECTED.

PERIODIC-SCRATCH

After rejection:

exit blastema mode immediately.

Return to:
normal incremental mode.

The next periodic attempt may occur:
no earlier than 6 episodes later.

TRIGGERED-BLASTEMA

After rejection:

if the blastema trigger has cleared:
exit to normal mode.

If the trigger remains positive:
remain local,
discard the failed candidate,
and begin a fresh scratch-candidate cycle
at the next checkpoint.

ORACLE-DAMAGE-MODE-SWITCH

After rejection:

remain local
and:
begin one new scratch cycle.

If the second oracle-triggered cycle also fails:
exit to local-only mode
for the remainder of that damage event.

This addendum changes:

candidate lifecycle only.

It does NOT change:

- blastema trigger thresholds;
- scratch reconstruction;
- K inference;
- +0.08 validation margin;
- two-checkpoint promotion requirement;
- action freeze boundary;
- rollback rule;
- primary acceptance criteria.

Harness-only worlds remain excluded from H144 primary evidence.
