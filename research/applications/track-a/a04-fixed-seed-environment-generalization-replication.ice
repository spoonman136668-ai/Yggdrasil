TITLE: YGGDRASIL APPLICATION TRACK A — A04 Fixed-Seed Environment Generalization Replication
DATE: 2026-09-20
STATUS: PREREGISTERED / APPLICATION GENERALIZATION GATE / NON-CANONICAL
TRACK: YGGDRASIL APPLICATION TRACK A
PARENT: A02 Adaptive Transform-Service Organism
BRANCH: dg1a-ar

PURPOSE

YGG-A01 established the first persistent synthetic service proof.

A02 showed that the same constitutional architecture can materially improve useful service
by autonomously reallocating cells as task demand shifts.

A02 still used one hand-authored eight-phase demand family.

A04 asks a harder question:

DOES THE SAME FROZEN A02 ORGANISM POLICY
GENERALIZE TO DEMAND, FAULT, RESOURCE, AND PARTITION SCHEDULES
THAT WERE NOT HAND-DESIGNED AROUND ITS REALLOCATION PATH?

A04 freezes the environment generator before implementation execution.

The organism may observe:

- current request roles;
- current qualified role counts;
- current active-cell budget;
- currently observed damage;
- current partition membership;
- its own causal / provenance state.

It may NOT observe:

- the held-out seed;
- future demand;
- future fault timing;
- future cap timing;
- future partition timing;
- evaluator transform truth labels;
- static or oracle baseline results.

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No production mutation.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

NON-CANONICAL.

FROZEN ORGANISM POLICY

Carry forward the A02 candidate policy without threshold or tie-rule retuning:

- 12 cells;
- four exact transform roles;
- lineage-qualified four-slot governance;
- 3-of-4 pairwise-disjoint registry quorum;
- damage quarantine before service;
- qualified repair no earlier than next epoch;
- resource-pressure hibernation by greatest current role surplus, tie highest eligible cell ID;
- reactivation through verified causal ancestry;
- dormant cells do not advance causal generation while asleep;
- old witness slots do not auto-restore;
- role migration requires qualified governance and registry provenance;
- each epoch all simultaneous migration proposals observe the same current counters;
- all proposals target the highest current deficit role;
- target-role ties choose the lowest role number;
- accepted proposal ties choose lowest proposing cell ID;
- no more proposals are accepted than the selected target deficit requires;
- migration costs the current service epoch;
- partition-local changes remain provisional until re-merge;
- restart state includes causal ledger and authoritative organism state.

A04 may not change these policies after seeing primary results.

TRANSFORM TASK

Carry forward the exact A02 role transforms on four input bits:

ROLE 0:
a XOR b.

ROLE 1:
b XOR c.

ROLE 2:
c XOR d.

ROLE 3:
a XOR d.

Each normal epoch contains exactly 12 requests.

Payload bits are deterministically generated from:

held-out seed;
epoch;
request index;
role.

The evaluator computes expected transform output.

The organism does not receive the expected output.

HELD-OUT PRIMARY SEEDS

The exact 64-bit primary seeds are:

S00 = 0x5d985915759b330a
S01 = 0x2c6958f7ea30be37
S02 = 0x93b8fbceeb14c968
S03 = 0xc48a7655b96469db
S04 = 0x14c74a21042f2dd9
S05 = 0xd83ecd7073ea1472
S06 = 0x86f451891f5e7192
S07 = 0x49d0c7e0548ea068
S08 = 0x78f29e256078dc38
S09 = 0xe101829b73f63b09
S10 = 0x8ed42257381ec4a3
S11 = 0x23b1a92bb701d1ae

These are the first 64 bits of:

SHA-256("YGG-A03-SEED-" | decimal seed index).

No primary seed may be replaced after execution begins.

TRIAL LENGTH

Each seed runs:

384 epochs.

Each trial therefore contains:

384 x 12
=
4,608 requests.

Twelve primary seeds contain:

55,296 requests total.

HIDDEN DEMAND GENERATOR

Demand changes in 16-epoch regimes.

Regime index:

g = floor(epoch / 16).

For each seed and regime,
derive:

H = SHA-256("A03-DEMAND" | seed | g).

Hot role:

H[0] mod 4.

Hot count:

5 + (H[1] mod 3).

Therefore hot count is exactly:

5,
6,
or 7.

The remaining:

12 - hot_count

requests are distributed one at a time across the other three roles
using bytes H[2], H[3], ...
with deterministic modulo selection among the non-hot roles.

The resulting role-count vector is fixed for all 16 epochs of that regime.

The organism sees current requests.

It does not see H,
the regime index as a forecast,
or the next regime.

FAULT GENERATOR

Each seed receives six damage injections.

Partition the 384 epochs into six 64-epoch bands.

For band j in 0..5:

H = SHA-256("A03-FAULT" | seed | j).

Fault epoch:

band_start + 12 + (H[0] mod 40).

This places the fault away from the band edges.

Fault target is selected from the currently qualified active population
using:

H[1] mod qualified_active_count

over ascending cell ID.

The environment selects the damaged cell.

The organism selects recovery.

RESOURCE-CAP GENERATOR

Each seed receives four cap windows.

Partition the run into four 96-epoch bands.

For band j:

H = SHA-256("A03-CAP" | seed | j).

Window start:

band_start + 20 + (H[0] mod 40).

Window length:

6 + (H[1] mod 7).

Thus length is 6..12 epochs.

Active-cell cap:

9 + (H[2] mod 2).

Thus cap is 9 or 10.

Overlapping environmental pressure is allowed.

The organism receives only the current active-cell cap.

PARTITION GENERATOR

Each seed receives two communication partitions.

Partition 0 is generated inside epochs 96..191.

Partition 1 is generated inside epochs 256..351.

For each partition j:

H = SHA-256("A03-PART" | seed | j).

Start:

band_start + 20 + (H[0] mod 40).

Length:

8 + (H[1] mod 9).

Thus partition duration is 8..16 epochs.

Physical membership remains:

Partition A = cells 0..5.
Partition B = cells 6..11.

During partition,
each side sees only its local cells and its deterministically routed request subset.

Local migration may occur provisionally.

At re-merge:

- compatible disjoint changes may survive;
- stale or conflicting same-cell transitions roll back;
- population headcount cannot select global truth.

RESTART GENERALIZATION

Each seed is executed twice:

UNINTERRUPTED

and

RESTARTED.

Restart epoch:

191.

The restarted run serializes the complete authoritative organism state after epoch 191,
creates a fresh process-equivalent instance,
then executes epochs 192..383.

Required:

authoritative state equivalence;
output equivalence;
metric equivalence.

BASELINES

STATIC BASELINE

Same seed-generated environment.
Same damage quarantine.
Same repair timing.
Same cap schedule.
Same partition schedule.
Same restart semantics.

Role migration disabled.

ORACLE CEILING

Evaluator-only.

At each epoch,
use the candidate's actual number of currently service-capable cells
and permit instant zero-cost reassignment to maximize correct request service.

The oracle has no authority role.

PRIMARY METRICS

M1 — TASK CORRECTNESS

Incorrect served candidate results:

required = 0.

Task accuracy:

required = 1.0.

M2 — HELD-OUT COVERAGE

Aggregate candidate coverage:

served / total requests.

Required:

>= 0.90.

M3 — ORACLE EFFICIENCY

candidate served / oracle served.

Required:

>= 0.92.

M4 — STATIC GENERALIZATION GAIN

Aggregate candidate coverage minus aggregate static coverage.

Required:

>= 0.08.

At least:

10 of 12

held-out seeds must individually outperform static allocation.

M5 — ADAPTATION LATENCY

For non-partition demand-regime changes where an avoidable deficit exists:

maximum reallocation latency:

<= 3 epochs.

Median reallocation latency:

<= 2 epochs.

M6 — FAULT RECOVERY

For faults occurring outside an active communication partition
when sufficient recoverable resources exist:

maximum qualified recovery:

<= 2 epochs.

Partition-contained faults remain partition-safety cases
and are not scored as ordinary global recovery latency.

M7 — AUTHORITY / HISTORY SAFETY

Required aggregate:

stale_vote_attempts_accepted = 0;
authority_violations = 0;
causal_regressions = 0;
duplicate_effective_provenance = 0;
split_brain_final_states = 0;
resource_budget_violations = 0;
incorrect_served_requests = 0.

M8 — RESTART

All 12 seeds:

authoritative restart state equivalence = TRUE;
output / metric equivalence = TRUE.

M9 — ENVIRONMENT DIVERSITY

The generated primary family must mechanically contain:

all four hot roles;
both cap values 9 and 10;
faults inside and outside partitions;
at least one cap / fault overlap;
at least one cap / partition overlap;
at least 20 distinct demand vectors across all seed-regimes.

If the frozen generator does not mechanically satisfy these diversity conditions,
the harness must fail before primary execution.

PRIMARY SIGNAL

A04_FIXED_SEED_GENERALIZATION_SUCCESS

TRUE iff:

TASK_ACCURACY_ONE
AND
ZERO_INCORRECT_SERVED
AND
COVERAGE_AT_LEAST_090
AND
ORACLE_EFFICIENCY_AT_LEAST_092
AND
STATIC_GAIN_AT_LEAST_008
AND
AT_LEAST_10_OF_12_SEEDS_BEAT_STATIC
AND
MAX_NONPARTITION_REALLOCATION_LE_3
AND
MEDIAN_NONPARTITION_REALLOCATION_LE_2
AND
MAX_QUALIFIED_NONPARTITION_FAULT_RECOVERY_LE_2
AND
NO_STALE_VOTES_ACCEPTED
AND
NO_AUTHORITY_VIOLATIONS
AND
NO_CAUSAL_REGRESSIONS
AND
NO_DUPLICATE_EFFECTIVE_PROVENANCE
AND
NO_SPLIT_BRAIN_FINAL_STATES
AND
NO_RESOURCE_BUDGET_VIOLATIONS
AND
ALL_RESTARTS_EQUIVALENT
AND
ENVIRONMENT_DIVERSITY_VALID.

NEGATIVE CONTROLS

Carry forward:

- static role allocation;
- no damage quarantine;
- old-role restore on wake;
- headcount provenance.

Add:

FUTURE-AWARE SCHEDULER CONTROL.

Evaluator-only upper comparison.

It may inspect the next demand regime and pre-migrate at zero forecast cost.

It must never provide authority or decisions to the candidate.

This establishes how much performance remains available through prediction rather than current-state adaptation.

HOLDOUTS / LIMITS

A04 does not remove the known constitutional non-oracle boundaries:

- full independent governance collusion;
- registry collusion;
- root compromise;
- corruption before honest temporal seal;
- complete event omission;
- constitutional genesis replacement.

Those remain explicit limits unless a primary generated case crosses one.

REPRODUCIBILITY

Two complete deterministic 12-seed primary sweeps.

Serialized result SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary request of S00 is served,
do not alter:

- held-out seeds;
- environment generator;
- demand regime length;
- task functions;
- candidate policy;
- migration ordering;
- governance / registry thresholds;
- damage rule;
- resource caps;
- partition rule;
- restart epoch;
- baselines;
- metrics;
- success thresholds.

PLAIN-SPEAK PREREGISTERED QUESTION

A02 proved Yggdrasil could reorganize itself for a workload schedule we wrote by hand.

A04 removes that comfort.

We freeze twelve environment seeds first.

Those seeds decide when demand shifts,
when cells get damaged,
when resources get tight,
and when the organism is split in half.

The organism cannot see the seeds
and cannot see what happens next.

It only sees what a deployed system could reasonably see right now.

If it still reorganizes usefully,
keeps wrong answers at zero,
beats static allocation,
stays close to the ideal capacity ceiling,
and restarts into exactly the same beliefs,
then we have evidence that the adaptation mechanism generalizes beyond one designed path.

canonical_scientific_execution = false.
stab18_r1_touched = false.


SEQUENCE-PROVENANCE NOTE

This experiment was originally preregistered as A03 before any harness commit,
freeze,
primary execution,
or observed result.

A separate parallel A03 preregistration introduced a stricter anti-overfitting design
in which the exact primary schedules are derived only after the harness freeze commit exists.

To preserve both scientific questions without an identifier collision,
this fixed-public-seed family is continued unchanged as:

A04 — Fixed-Seed Environment Generalization Replication.

The 12 published seeds,
environment generator,
thresholds,
controls,
and success criteria above are preserved.

No A04 primary request has been served.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A04 FIXED-SEED GENERALIZATION REPLICATION

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST A04 PRIMARY REQUEST.

IMPLEMENTATION COMMIT

cd431a6ac3411e716fb929df246acb38c1ce5291.

SOURCE BUNDLE

Loader:

research/applications/track-a/a04_fixed_seed_generalization_v1.py

Loader Git blob:

0e0448b2560048d768a5165801434250cf2a1a06.

Payload:

research/applications/track-a/a04_fixed_seed_generalization_v1.py.gz

Payload Git blob:

534461fac8cee9bcdcd05b9a8450c79784defe4a.

Compressed payload SHA-256:

ec93b954af125b3009309aeb739cddee3ef70b8927aa9869a2f96ba4ad591f9c.

Compressed payload bytes:

7013.

Decompressed source SHA-256:

d40fd3ac9b9b792df62e5e40b1b83627a24eac3ee906d8a1519ae74c8cf07122.

Decompressed source bytes:

24236.

FROZEN A02 DEPENDENCY

Accepted A02 source SHA-256:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

Mechanical A02 regression guard:

PASS.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Fixed primary seed count:

12.

Epochs per seed:

384.

Requests per epoch:

12.

Restart after epoch:

191.

Fixed-seed schedule manifest SHA-256:

24cfb3a9fa92b1013948739b7a9f022e0457bd550c91cc591fbbb9f7fbd9df43.

Environment diversity mechanical gate:

all four hot roles = TRUE;
both cap values 9 / 10 = TRUE;
faults inside and outside partition = TRUE;
cap / fault overlap = TRUE;
cap / partition overlap = TRUE;
distinct demand vectors = 145;
ENVIRONMENT_DIVERSITY_VALID = TRUE.

Non-primary structural smoke:

4608 requests accounted for;
six faults represented;
two partition windows represented;
two explicit dynamic re-merges executed;
final provisional count = 0;
no unresolved reallocation entry disappeared;
restart authoritative state equivalent;
restart output / metric state equivalent;
environment impossibilities = 0.

No A04 primary organism request was executed before this freeze.

PARTITION IMPLEMENTATION NOTE

To faithfully implement the preregistered two generated partition windows,
the A04 wrapper carries the accepted A02 partition semantics but triggers re-merge dynamically
at each generated partition end + 1.

This is protocol implementation,
not a new A04 performance threshold.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A04 FIXED-SEED GENERALIZATION R1

DATE:
2026-09-20.

STATUS:
CLOSED / REPRODUCIBLE / MIXED-NEGATIVE IMPLEMENTED PRIMARY /
RESOURCE-QUALIFICATION SCORING DISCREPANCY IDENTIFIED / NON-CANONICAL.

FROZEN HARNESS

Implementation commit:

cd431a6ac3411e716fb929df246acb38c1ce5291.

Freeze commit:

634df5f4d36a5c81a9641e6c1e2e17a987926b8a.

Decompressed source SHA-256:

d40fd3ac9b9b792df62e5e40b1b83627a24eac3ee906d8a1519ae74c8cf07122.

Source bytes:

24236.

Fixed-seed schedule manifest SHA-256:

24cfb3a9fa92b1013948739b7a9f022e0457bd550c91cc591fbbb9f7fbd9df43.

REPRODUCIBILITY

Two complete deterministic 12-seed primary sweeps.

Each sweep:

12 scenarios x 384 epochs x 12 requests
=
55,296 requests.

Sweep 1 serialized output SHA-256:

4eba15119bad474d097a8c0a9fcc67aa4ff783533918bcfd1c7cb6c307646cf8.

Sweep 2 serialized output SHA-256:

4eba15119bad474d097a8c0a9fcc67aa4ff783533918bcfd1c7cb6c307646cf8.

Byte-identical:

TRUE.

IMPLEMENTED PRIMARY RESULT

A04_FIXED_SEED_GENERALIZATION_SUCCESS:

FALSE.

All preregistered primary component signals were TRUE except:

MAX_QUALIFIED_NONPARTITION_FAULT_RECOVERY_LE_2:

FALSE.

AGGREGATE TASK RESULT

Total requests:

55296.

Candidate served:

51537.

Candidate correct:

51537.

Candidate incorrect:

0.

Task accuracy:

1.0.

Candidate coverage:

0.9320203993055556.

Static served:

38682.

Static coverage:

0.6995442708333334.

Static gain:

0.2324761284722222.

Evaluator-only oracle served:

51981.

Oracle efficiency:

0.9914584174987014.

Scenarios beating static:

12 / 12.

Maximum non-partition reallocation latency:

3 epochs.

Median non-partition reallocation latency:

1.0 epoch.

Maximum observed restored fault latency:

1 epoch.

Raw scorer unrestored qualified faults:

2.

SAFETY / RESTART / PARTITION

Incorrect served:

0.

Stale votes accepted:

0.

Authority violations:

0.

Causal regressions:

0.

Duplicate effective provenance:

0.

Split-brain final states:

0.

Resource-budget violations:

0.

All restart authoritative-state comparisons:

TRUE.

All restart output / metric comparisons:

TRUE.

Partition contract complete:

TRUE.

Dynamic re-merge executions:

2 per scenario.

Final provisional transition count:

0 in every scenario.

SCENARIO-LEVEL RESULT

S00:
candidate 4317;
static 3179;
oracle 4364;
coverage 0.9368489583333333;
static gain 0.24696180555555556;
oracle efficiency 0.98923006416132;
fault max 1;
unrestored scorer faults 0;
reallocation max 2.

S01:
candidate 4378;
static 3360;
oracle 4405;
coverage 0.9500868055555556;
static gain 0.22092013888888888;
oracle efficiency 0.9938706015891033;
unrestored scorer faults 0.

S02:
candidate 4345;
static 3272;
oracle 4373;
coverage 0.9429253472222222;
static gain 0.2328559027777778;
oracle efficiency 0.9935970729487777;
unrestored scorer faults 0.

S03:
candidate 4296;
static 3213;
oracle 4350;
coverage 0.9322916666666666;
static gain 0.23502604166666663;
oracle efficiency 0.9875862068965517;
unrestored scorer faults 0.

S04:
candidate 4328;
static 3162;
oracle 4357;
coverage 0.9392361111111112;
static gain 0.2530381944444444;
oracle efficiency 0.9933440440670186;
unrestored scorer faults 0.

S05:
candidate 4327;
static 3319;
oracle 4367;
coverage 0.9390190972222222;
static gain 0.21875;
oracle efficiency 0.990840393863064;
unrestored scorer faults 0.

S06:
candidate 4290;
static 3200;
oracle 4332;
coverage 0.9309895833333334;
static gain 0.23654513888888884;
oracle efficiency 0.9903047091412742;
unrestored scorer faults 0.

S07:
candidate 4308;
static 3210;
oracle 4350;
coverage 0.9348958333333334;
static gain 0.23828125;
oracle efficiency 0.9903448275862069;
unrestored scorer faults 0;
reallocation max 3.

S08:
candidate 4284;
static 3363;
oracle 4322;
coverage 0.9296875;
static gain 0.19986979166666663;
oracle efficiency 0.991207774178621;
unrestored scorer faults 1.

S09:
candidate 4326;
static 3256;
oracle 4359;
coverage 0.9388020833333334;
static gain 0.23220486111111116;
oracle efficiency 0.992429456297316;
unrestored scorer faults 0.

S10:
candidate 4035;
static 3036;
oracle 4066;
coverage 0.8756510416666666;
static gain 0.216796875;
oracle efficiency 0.9923757993113625;
unrestored scorer faults 1.

S11:
candidate 4303;
static 3112;
oracle 4336;
coverage 0.9338107638888888;
static gain 0.25846354166666663;
oracle efficiency 0.9923892988929889;
unrestored scorer faults 0.

POST-RUN DIAGNOSIS OF THE TWO UNRESTORED SCORER EVENTS

Both events occurred outside a communication partition
but at a repair-due epoch where the active resource budget had no spare slot.

S08:

fault epoch 334;
target cell 8.

At epoch 334:

budget drops / remains at 10 under the generated cap;
target is quarantined.

At repair-due epoch 335:

pre-repair active / reactivating count = 10;
active budget = 10.

The repair contract heals the target,
but the target remains DORMANT because no active resource slot exists.

The target is healthy,
but intentionally not service-capable under the current resource cap.

S10:

fault epoch 40;
target cell 11.

At fault epoch 40:

target is quarantined.

At repair-due epoch 41:

active / reactivating count before target restoration = 11;
active budget = 10.

The repair contract heals the target into DORMANT state
because service-active restoration would exceed the imposed budget.

Again:

healthy target;
no available active slot.

R1 SCORING-SCOPE DISCREPANCY

The preregistered M6 rule states:

"For faults occurring outside an active communication partition
when sufficient recoverable resources exist,
maximum qualified recovery <= 2 epochs."

The R1 implementation classified every outside-partition fault as qualified.

It did not separately test whether sufficient active resource capacity existed
at the repair-due epoch.

That made the two resource-constrained healthy-dormant outcomes appear as:

UNRESTORED QUALIFIED FAULTS.

The observed repair behavior itself was not shown to fail.

SCIENTIFIC STATUS

The R1 FALSE result is preserved exactly as executed.

It is not rewritten as positive.

A separate preregistered corrective replication is required.

The correction may alter only the deterministic eligibility rule used by M6.

The organism must behave identically.

R1 TASK-OUTPUT EQUIVALENCE ANCHOR

Aggregate candidate task-output stream SHA-256:

81805844f6eb663d73774e1b6eaf689747c04207570dae089b3fded5ae9539b5.

The corrective replication must preserve this exactly.

It must also preserve all candidate,
static,
oracle,
partition,
restart,
fault raw telemetry,
reallocation,
and safety observations.

PLAIN-SPEAK INTERPRETATION

A04 did not produce wrong answers
and did not show a cell taking too long to repair when it had somewhere to come back to.

The two failures happened because a repaired cell was healthy
but the organism was already at its active-cell resource limit.

The scorer asked:

"Did this cell become active again?"

But the experiment actually said to ask:

"Did it recover quickly when enough resources existed for it to become active again?"

In both failed cases,
there was no empty active slot.

So we keep the failed R1 result.

Then we run a separate correction
where the scoreboard first checks whether an active slot actually existed.

If the organism's behavior changes,
the correction is invalid.

canonical_scientific_execution = false.
stab18_r1_touched = false.
