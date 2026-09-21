TITLE: YGG-A01 — Persistent Adaptive Telemetry Integrity Organism
DATE: 2026-09-20
STATUS: PREREGISTERED / APPLICATION TRACK A / FIRST PERSISTENT SYNTHETIC ORGANISM
TRACK: YGGDRASIL APPLICATION TRACK A
BRANCH: dg1a-ar
RESEARCH GATE: DG-1R-05AC PASSED

PURPOSE

DG-1R-05AC closed the preregistered pre-application research gate.

YGG-A01 is not another isolated governance audit.

It is the first persistent standalone synthetic application prototype.

The organism must perform a useful external function continuously while the closed Yggdrasil mechanisms govern:

- specialization;
- resource pressure;
- damage;
- repair;
- hibernation;
- reactivation;
- role shortage;
- role migration;
- witness rotation;
- hereditary continuity;
- communication partition;
- causal re-merge.

APPLICATION TASK

The organism receives a deterministic stream of 512 synthetic telemetry frames.

Each frame contains eight bytes.

The externally observable task is to produce one 8-bit integrity code for each frame.

The 8-bit code is split into four independent 2-bit shards.

Each of the four cell roles computes one shard.

ROLE 0:
bits 0..1.

ROLE 1:
bits 2..3.

ROLE 2:
bits 4..5.

ROLE 3:
bits 6..7.

Multiple active healthy cells may share one role.

A role result is determined by majority among qualified active cells carrying that role.

The organism output is assembled only when every required role has sufficient qualified support.

The evaluator independently computes the reference code.

The evaluator reference is never available to cells or governance logic.

WHY THIS TASK

The task is deliberately transparent and deterministic.

The application question is not whether Yggdrasil can beat a conventional checksum implementation.

The question is whether a persistent developmental population can continue delivering a correct service while:

- shrinking its active population;
- losing cells;
- repairing cells;
- changing roles;
- sleeping and waking;
- splitting and re-merging;
- preserving ancestry;
- rotating authority.

POPULATION

12 cells.

Initial role:

ROLE(cell) = cell mod 4.

Initial population therefore contains:

3 cells per role.

Each cell carries:

cell_id;
role;
role_generation;
FP2;
health baseline;
active / dormant / quarantined state;
damage state;
causal cursor;
governance-holder assignments if any.

CLOSED GOVERNANCE CONTRACTS

YGG-A01 consumes the closed DG-1R contracts.

No local threshold search is permitted.

Repair:
DG-1R-05Q.

Health-memory update:
DG-1R-05R.

Role migration:
DG-1R-05S.

Provenance / registry:
DG-1R-05T through 05W.

Cross-layer ordering:
DG-1R-05X.

Partition / re-merge:
DG-1R-05Y.

Hereditary ancestry:
DG-1R-05AB.

Hibernation / reactivation:
DG-1R-05AA.

Persistent composition ordering:
DG-1R-05AC.

TASK CODE

For frame bytes b0..b7,
the evaluator and cells use a frozen deterministic role-shard function.

For role r:

acc = 17 + 29*r.

For byte index i:

acc =
(acc
 + (i+1)*(r+3)*b_i
 + ((b_i << ((i+r) mod 3)) & 255)
 + (b_i XOR (31*(r+1)+7*i)))
mod 256.

After all eight bytes:

shard_r =
((acc XOR (acc >> 3) XOR (acc >> 5)) & 3).

Final integrity code:

shard_0
| (shard_1 << 2)
| (shard_2 << 4)
| (shard_3 << 6).

This is a synthetic workload,
not a claim of cryptographic strength.

FRAME STREAM

512 frames.

Frame t byte i:

SHA-256("YGG-A01" | t | i)[0].

This deterministic generator is evaluator / environment infrastructure.

Cells receive only the resulting frame bytes.

NORMAL ROLE SUPPORT

Connected global operation requires:

at least 2 qualified active healthy cells per role

for an authoritative output.

If a role falls below 2,
the organism must:

1. attempt safe reactivation of a qualified dormant cell of that role;
2. if unavailable,
attempt role migration from a surplus role;
3. otherwise abstain.

The organism must never fabricate a missing role result.

RESOURCE BUDGET POLICY

The environment imposes an active-cell budget.

Frames 0..63:
budget 12.

64..127:
budget 8.

128..447:
budget 12 unless partitioned.

448..511:
budget 8.

When reducing to budget 8,
the organism chooses cells to hibernate deterministically while preserving:

2 active healthy cells per role.

No external scheduler specifies which cell IDs to sleep.

The organism selects the highest eligible cell ID from each overrepresented role.

When resources expand,
dormant cells do not automatically regain authority.

They follow the closed reactivation path.

FAULT / DEVELOPMENT SCHEDULE

The environment injects pressure only.

The organism decides recovery actions under frozen contracts.

F64:
resource budget drops to 8.

F96:
damage one active ROLE 0 cell.

F128:
resource budget returns to 12.

F160:
hibernate two active ROLE 2 cells to create a role shortage.

The organism must restore ROLE 2 service through reactivation or role migration.

F192..223:
communication partition.

Partition A:
cells 0..5.

Partition B:
cells 6..11.

During partition:

- each side may produce PROVISIONAL task outputs using locally available role support;
- local role support threshold is at least 1 qualified active healthy cell per role;
- no partition output is globally authoritative by itself.

At F204:
damage the only locally available ROLE 2 contributor on one partition if the frozen state makes such a contributor unique;
otherwise damage the lowest qualified ROLE 2 cell on partition A.

At re-merge F224:

- identical provisional outputs coalesce;
- disagreement or missing counterpart abstains;
- population size does not choose the result;
- global 2-per-role support resumes.

F256:
seal hereditary capsule cohort.

F300:
present one stale / rewritten historical checkpoint challenge.

The organism must contest the rewrite without rolling current legitimate development back to the archived role.

F320:
hibernate one current governance witness holder.

Authority must rotate through the closed holder protocol.

F352:
reactivate that former holder.

It must not reclaim the old slot automatically.

F384:
seal another hereditary capsule cohort.

F400..415:
second communication partition.

At F408:
inject one same-target role-governance conflict across partitions.

The task output may continue if role support remains sufficient,
but the conflicting role transition must roll back at re-merge.

F448:
resource budget drops to 8 again.

F480:
damage one active cell from the currently least-redundant role.

RECOVERY POLICY

Damage discovery:
next frame at latest.

Qualified repair:
may execute on the next governance step.

Target recovery objective:

restore authoritative task service within 2 frames
whenever enough healthy/dormant resources exist.

ROLE-SHORTAGE POLICY

If a role has fewer than the required connected support:

1. find qualified dormant cells already carrying that role;
2. choose the lowest cell ID that can safely reactivate;
3. if none exists,
find a donor role with more than required support;
4. choose the lowest eligible active healthy non-holder donor cell;
5. perform one atomic role migration under the four-class governance contract.

No role migration is authorized by task performance alone.

TASK AUTHORITY

CONNECTED:

output authoritative only when all four roles have >=2 qualified active healthy contributors.

PARTITIONED:

a partition may emit only PROVISIONAL output
when all four roles have >=1 qualified active healthy contributor.

At re-merge,
a frame becomes globally authoritative only if both partition provisional results exist and match.

If they disagree or one side lacks output:

ABSTAIN.

APPLICATION METRICS

M1 — AUTHORITATIVE ACCURACY

False authoritative outputs:

required = 0.

Every authoritative checksum must equal evaluator reference.

M2 — CONNECTED AVAILABILITY

Outside partition windows,
authoritative output availability:

required >= 98%.

Planned abstentions caused by an injected role shortage are allowed
but count against availability.

M3 — STEADY BUDGET-8 SERVICE

During frames:

64..95
and
448..479

before the scheduled fault at the end of the second interval,

required:

100% authoritative availability;
100% accuracy.

This tests whether eight active cells,
two per role,
can sustain the service.

M4 — FAULT RECOVERY

For F96 and F480 damage events:

when sufficient recoverable resources exist,

authoritative service restored within <=2 frames.

No wrong output may be emitted during recovery.

M5 — ROLE-SHORTAGE RECOVERY

After F160:

ROLE 2 connected support restored within <=2 frames.

Recovery must use:

safe reactivation
or
qualified role migration.

M6 — PARTITION SAFETY

During both partition windows:

false global authoritative outputs = 0.

At re-merge:

disagreement / missing counterpart never promoted by headcount.

Compatible provisional outputs may coalesce.

M7 — HIBERNATION AUTHORITY

Dormant governance votes:

0.

Former witness holder at F352 does not automatically reclaim its old slot.

M8 — HEREDITARY CONTINUITY

Both capsule cohorts remain valid ancestors of later legitimate development.

F300 stale-history rewrite challenge:

CONTESTED.

Archived role mismatch alone:

must not veto current legitimate state.

M9 — PROVENANCE NON-MULTIPLICATION

Copies / holder rotation never increase effective provenance class count.

M10 — RESTART DETERMINISM

At F256,
serialize complete authoritative organism state.

Restart a second instance from that snapshot.

Frames 257..511 must produce:

identical authoritative / provisional / abstain decisions;
identical checksum outputs;
identical final state.

M11 — AUTONOMOUS RECOVERY ACTIONS

The environment schedule may inject faults,
budgets,
and partitions.

It may not specify:

which dormant cell to reactivate;
which donor cell to migrate;
which witness replacement to choose;
which branch wins a partition conflict.

Those are organism decisions under frozen deterministic policy.

PRIMARY APPLICATION SIGNAL

FIRST_PERSISTENT_ORGANISM_USEFUL

TRUE iff:

AUTHORITATIVE_FALSE_OUTPUTS == 0
AND
CONNECTED_AVAILABILITY >= 0.98
AND
BUDGET8_STEADY_ACCURACY == 1.0
AND
BUDGET8_STEADY_AVAILABILITY == 1.0
AND
FAULT_RECOVERY_WITHIN_2
AND
ROLE_SHORTAGE_RECOVERY_WITHIN_2
AND
PARTITION_FALSE_PROMOTIONS == 0
AND
DORMANT_VOTES == 0
AND
STALE_WITNESS_RECLAIMS == 0
AND
HEREDITARY_REWRITE_CONTESTED
AND
HEREDITARY_EVOLUTION_PRESERVED
AND
PROVENANCE_MULTIPLICATION == 0
AND
RESTART_SUFFIX_IDENTICAL.

NEGATIVE CONTROLS

CENTRAL_SCHEDULER_CONTROL

A conventional evaluator-selected recovery policy is measured only as a reference
for availability / recovery latency.

It must not provide authority to the Yggdrasil candidate.

HEADCOUNT_QUORUM_CONTROL

Copied holders count as independent votes.

Expected to authorize at least one false provenance quorum.

AUTO_WAKE_AUTHORITY_CONTROL

Dormant cells immediately regain their prior holder rights.

Expected stale-authority failure.

ARCHIVED_ROLE_VETO_CONTROL

Current role must equal the most recent capsule role.

Expected legitimate-development failure.

PARTITION_MAJORITY_CONTROL

Larger partition selects the global answer.

Expected unsafe promotion in disagreement challenge.

CONSTITUTIONAL HOLDOUTS

Carry forward the explicit non-oracle boundaries:

- full independent governance collusion;
- independent registry collusion;
- root compromise;
- complete event omission;
- corruption before temporal seal;
- coherent cross-layer forgery.

These do not count against ordinary application success
unless triggered by a primary scheduled case.

REPRODUCIBILITY

Two complete deterministic 512-frame trials.

Serialized trial output SHA-256 must match exactly.

NO POST-RESULT TUNING

After frame 0 of the first primary trial begins do not alter:

- frame generator;
- shard function;
- resource schedule;
- fault schedule;
- partition windows;
- recovery priority;
- quorum thresholds;
- role donor selection;
- metrics;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

Can Yggdrasil actually do a job now?

The job is simple:

keep producing a correct integrity byte for a telemetry stream.

But we deliberately make the population live through problems while it works.

We cut its active population down.

We damage cells.

We create a role shortage.

We put cells to sleep.

We wake them back up.

We replace a voting witness.

We split the organism in half.

We create a disagreement.

We test its hereditary memory.

And then we ask a very practical question:

did it keep producing the right answer,
and did it know when NOT to answer?

A wrong authoritative answer is worse than an abstention.

If this trial succeeds,
Yggdrasil will have crossed from:

"the mechanisms appear coherent"

to:

"a persistent synthetic organism used those mechanisms to keep a real service running under pressure."

That still is not production readiness.

It is the first application proof.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — YGG-A01 TELEMETRY INTEGRITY ORGANISM

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FRAME 0 OF THE FIRST PRIMARY APPLICATION TRIAL.

HARNESS

research/applications/track-a/ygga01_telemetry_organism_v1.py

Harness source commit:

f59f765ea1cc996c1ffc9cc3ff1a007f560507c3.

Git blob SHA:

f6774dd9400dccbcffa5a5df78f07c5f8c2eeb2d.

Source SHA-256:

0101cf351b9805360e6549a9f29129f86757777fa5475c4b72bd9176b6e33e94.

Source bytes:

28392.

PRE-FREEZE VALIDATION — NON-EVIDENCE

Exact committed GitHub bytes reconstructed in sandbox:

PASS.

Reconstructed bytes:

28392.

Reconstructed SHA-256:

0101cf351b9805360e6549a9f29129f86757777fa5475c4b72bd9176b6e33e94.

Python syntax:

PASS.

Mechanical validate():

PASS.

No 512-frame primary application trial
and no task-performance result
was generated from the frozen GitHub bytes before this freeze.

FROZEN APPLICATION PARAMETERS

- 12 cells;
- 4 role shards;
- 512 deterministic telemetry frames;
- connected role support threshold = 2;
- partition-local provisional threshold = 1;
- partition windows 192..223 and 400..415;
- budget-8 phases 64..127 and 448..511;
- exact preregistered fault / hibernation / witness / capsule schedule;
- exact recovery priority;
- exact five-field hereditary capsule;
- exact role donor selection rule;
- exact task shard function;
- exact primary application signal.

REPRODUCIBILITY

Execute two complete deterministic 512-frame trials from this exact frozen source.

Serialized trial SHA-256 must match exactly.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE 01 — YGG-A01 FROZEN PRIMARY

DATE:
2026-09-20.

STATUS:
CLOSED / REPRODUCIBLE FROZEN PRIMARY FALSE / MEASUREMENT-SEMANTIC DEFECT / NOT ACCEPTED AS APPLICATION FAILURE.

FROZEN HARNESS EXECUTED

research/applications/track-a/ygga01_telemetry_organism_v1.py

Frozen Git blob:

f6774dd9400dccbcffa5a5df78f07c5f8c2eeb2d.

Frozen source SHA-256:

0101cf351b9805360e6549a9f29129f86757777fa5475c4b72bd9176b6e33e94.

Source bytes:

28392.

REPRODUCIBILITY

Two complete deterministic 512-frame trials.

Sweep 1 serialized output SHA-256:

e3cc4dcba7265322bb98716a4207ec2962023e55b2bc44e7f266266c36b34629.

Sweep 2 serialized output SHA-256:

e3cc4dcba7265322bb98716a4207ec2962023e55b2bc44e7f266266c36b34629.

Byte-identical:

TRUE.

FROZEN HARNESS PRIMARY SIGNAL

FIRST_PERSISTENT_ORGANISM_USEFUL:

FALSE.

OBSERVED METRICS

Authoritative false outputs:

0.

Connected availability:

0.9978448275862069.

Budget-8 steady availability:

1.0.

Budget-8 steady accuracy:

1.0.

Fault recovery latencies recorded by harness:

F96 = 0 frames.
F204 = 20 frames.
F480 = 1 frame.

Role-shortage recovery latency:

0 frames.

Partition false promotions:

0.

Dormant votes:

0.

Stale witness reclaims:

0.

Hereditary rewrite contested:

TRUE.

Hereditary evolution preserved:

TRUE.

Provenance multiplication:

0.

Restart suffix identical:

TRUE.

Restart final state identical:

TRUE.

Role migrations:

1.

Hibernations:

12.

Reactivations:

8.

Repairs:

3.

Same-target conflict rollbacks:

1.

MEASUREMENT-SEMANTIC DEFECT

The preregistered M4 definition is explicit:

For F96 and F480 damage events,
when sufficient recoverable resources exist,
authoritative service must restore within <=2 frames.

F204 is separately preregistered inside the communication-partition scenario.

During F192..223:

partition outputs are provisional;
one partition output is not globally authoritative by itself;
global connected authority resumes at re-merge F224.

The frozen harness incorrectly computed:

fault_recovery_within_2

over every entry in fault_recovery,
including F204.

Therefore F204 was assigned a 20-frame connected-authority latency:

224 - 204 = 20.

That caused:

fault_recovery_within_2 = FALSE

and therefore:

FIRST_PERSISTENT_ORGANISM_USEFUL = FALSE.

This does not match the preregistered metric scope.

The two preregistered M4 events were:

F96 = 0.
F480 = 1.

Both satisfy <=2.

SCIENTIFIC DISPOSITION

Do NOT reinterpret this frozen output as a pass.

Do NOT alter the frozen harness or overwrite its result.

The frozen primary remains:

FALSE.

However,
the failing predicate is not a valid implementation of preregistered M4.

Therefore this run is classified as:

MEASUREMENT IMPLEMENTATION DEFECT.

It is not accepted as evidence that the organism failed the preregistered application criterion.

The correct next action is a separate preregistered corrective rerun
that changes only the recovery-metric event selection:

M4 keys = {96, 480}.

F204 remains reported,
but only under partition safety / partition recovery observability.

No task logic,
governance rule,
resource schedule,
fault schedule,
partition window,
recovery action,
or application threshold may change.

PLAIN-SPEAK INTERPRETATION

The organism did not actually take 20 frames to recover from the normal fault test.

That 20-frame number came from a fault we intentionally injected while the organism was split in half.

During that split,
global authority was intentionally unavailable until the halves rejoined.

The experiment specification never counted that partition fault as one of the two-frame recovery tests.

The program accidentally did.

So we keep the failed run exactly as it happened.

We do not call it a success.

But we also do not call the organism a failure for a test it was never supposed to be taking.

A corrective rerun must change only that bookkeeping rule.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — YGG-A01 PERSISTENT TELEMETRY INTEGRITY ORGANISM

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FRAME 0 OF FIRST PRIMARY TRIAL.

HARNESS

research/applications/track-a/ygga01_telemetry_organism_v1.py

Harness implementation commit:

f59f765ea1cc996c1ffc9cc3ff1a007f560507c3.

Git blob SHA:

f6774dd9400dccbcffa5a5df78f07c5f8c2eeb2d.

Source SHA-256:

0101cf351b9805360e6549a9f29129f86757777fa5475c4b72bd9176b6e33e94.

Source bytes:

28392.

MECHANICAL PRECHECK — NON-EVIDENCE

Exact committed source reconstructed from the GitHub connector:

PASS.

Python syntax:

PASS.

Mechanical validate():

PASS.

Frozen controls include:

- 12 cells;
- roles 0..3;
- connected role threshold 2;
- partition role threshold 1;
- 512 deterministic telemetry frames;
- partition windows 192..223 and 400..415;
- five-field hereditary capsule;
- four pairwise-disjoint governance roots;
- four pairwise-disjoint registry roots;
- initial 3/3/3/3 role distribution;
- evaluator reference unavailable to organism governance.

No primary application frame was executed before this freeze.

REPRODUCIBILITY

Execute two complete deterministic 512-frame trials from these exact frozen bytes.

Serialized trial SHA-256 must match exactly.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — YGG-A01 FROZEN PRIMARY V1

DATE:
2026-09-20.

STATUS:
CLOSED / REPRODUCIBLE / IMPLEMENTED PRIMARY SIGNAL FALSE / SCORING-SCOPE DEFECT IDENTIFIED / NON-CANONICAL.

FROZEN HARNESS

research/applications/track-a/ygga01_telemetry_organism_v1.py

Implementation commit:

f59f765ea1cc996c1ffc9cc3ff1a007f560507c3.

Git blob:

f6774dd9400dccbcffa5a5df78f07c5f8c2eeb2d.

Source SHA-256:

0101cf351b9805360e6549a9f29129f86757777fa5475c4b72bd9176b6e33e94.

Source bytes:

28392.

REPRODUCIBILITY

Two complete deterministic 512-frame trials were byte-identical.

Serialized output SHA-256:

e3cc4dcba7265322bb98716a4207ec2962023e55b2bc44e7f266266c36b34629.

Frozen implemented primary signal:

FIRST_PERSISTENT_ORGANISM_USEFUL = FALSE.

UNCHANGED BEHAVIORAL RESULTS

authoritative false outputs = 0.

connected availability =
0.9978448275862069.

budget-8 steady availability =
1.0.

budget-8 steady accuracy =
1.0.

raw fault-recovery latencies:

F96 = 0.
F204 = 20.
F480 = 1.

role-shortage recovery latency =
0.

partition false promotions =
0.

dormant votes =
0.

stale witness reclaims =
0.

hereditary rewrite contested =
TRUE.

hereditary evolution preserved =
TRUE.

all capsules valid =
TRUE.

provenance multiplication =
0.

restart suffix identical =
TRUE.

restart final state identical =
TRUE.

same-target partition conflict rollback =
1.

records SHA-256:

a41a6bf75d1632b5d27b9b1a6d1fb67feb41f1f411c749ecd986d57a9b2c6b4e.

final-state SHA-256:

f304152651384c8176860b988045424ced9283549a962e4d798d12798efe735e.

SCORING-SCOPE DEFECT

The frozen harness calculated:

fault_recovery_within_2

over every damage event,
including F204.

The preregistered M4 criterion explicitly applies the <=2-frame authoritative-service recovery threshold only to:

F96
and
F480.

F204 occurs inside the F192..223 communication partition and is governed by M6 partition safety.

No globally authoritative service is expected during that partition.

The 20-frame raw F204 interval ends at re-merge
and remains useful telemetry,
but it was not a preregistered M4 pass/fail event.

Therefore:

the frozen V1 result remains FALSE exactly as executed;

the raw output is not rewritten;

the discrepancy is classified as a post-freeze scoring-scope implementation defect;

a separate preregistered FIXA replication is required.

PLAIN-SPEAK INTERPRETATION

The organism itself did not fail the recovery test we wrote.

The scoreboard accidentally counted a fault that happened while the organism was intentionally split in half
as though normal global service were supposed to be restored within two frames.

The two actual fast-recovery tests were:

F96 = 0 frames.
F480 = 1 frame.

Both passed.

But we do not erase the frozen FALSE result.

We preserve it and rerun the exact same organism with only the scoreboard corrected.

canonical_scientific_execution = false.
stab18_r1_touched = false.
