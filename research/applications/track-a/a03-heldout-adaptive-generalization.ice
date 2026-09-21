TITLE: YGGDRASIL APPLICATION TRACK A — A03 Held-Out Adaptive Generalization
DATE: 2026-09-20
STATUS: PREREGISTERED / HELD-OUT GENERALIZATION APPLICATION / NON-CANONICAL
TRACK: APPLICATION-A / PERSISTENT SYNTHETIC ORGANISM
BRANCH: dg1a-ar
PARENT: A02 Adaptive Transform-Service Organism
ACCEPTED FRONTIER: YGG-A01 positive via FIXA; A02 positive

PURPOSE

A02 showed that the Yggdrasil population can improve useful service by reallocating healthy cells as demand moves between four transform roles.

A02 used a hand-written eight-phase workload schedule.

A03 asks a harder question:

DOES THE SAME FROZEN CONSTITUTIONAL / DEVELOPMENTAL POLICY
GENERALIZE TO WORKLOADS, RESOURCE PRESSURES, FAULT TIMES,
AND RESTART POINTS THAT WERE NOT KNOWN WHEN THE POLICY WAS FROZEN?

A03 changes the environment family.

It does not retune the organism.

ANTI-OVERFITTING DESIGN

The exact A03 primary schedules MUST NOT exist before the A03 harness freeze.

Before freeze:

- implement only a generic deterministic schedule compiler;
- mechanically test it on non-primary mechanical seeds;
- preserve the accepted A02 policy unchanged;
- do not execute any primary held-out schedule.

After the harness is frozen:

let F be the exact Git commit SHA that freezes the A03 harness.

Primary scenario seed i, for i = 0..11:

SHA-256("YGG-A03-PRIMARY|" + F + "|" + decimal(i)).

Thus the rule that generates the primary schedules is preregistered,
but the exact schedules are determined only after the policy / harness bytes are frozen.

The freeze closure MUST record:

- F;
- all 12 derived seed digests;
- a deterministic schedule-manifest SHA-256.

No post-freeze schedule rejection or seed replacement is allowed.

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production deployment.
No network exposure.
No CKB / KTRADE integration.
No financial task.
No canonical DG-1R-05 execution.
No STAB-18-R1 execution.

A03 remains disposable application research.

FROZEN POLICY DEPENDENCY

A03 MUST consume the accepted A02 organism policy rather than reimplementing or retuning it.

Accepted A02 dependency:

loader:
research/applications/track-a/a02_adaptive_transform_service_v1.py

compressed payload:
research/applications/track-a/a02_adaptive_transform_service_v1.py.gz

accepted A02 decompressed source SHA-256:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

A03 MAY provide a new environment driver and held-out metrics.

A03 MUST NOT alter A02's:

- transform functions;
- migration eligibility;
- migration proposal ordering;
- governance qualification;
- registry qualification;
- hibernation authority rules;
- reactivation authority rules;
- damage quarantine / repair ordering;
- partition provisional-authority semantics;
- merge safety rule;
- hereditary capsule semantics.

A03 harness MUST verify the A02 source hash before running.

A02 REGRESSION GUARD

Before any A03 primary schedule is evaluated,
the frozen A03 harness MUST reproduce the accepted A02 application result using the accepted A02 fixture.

Required A02 regression anchors:

serialized A02 result SHA-256:

ad408ca964108c3212bc55db1dd1c932ecbd588774323ebffdb755c32d361271.

A02 candidate served:

11928.

A02 static served:

9892.

A02 oracle served:

11961.

A02 incorrect served:

0.

If this regression guard fails,
A03 primary evidence is INVALID.

TASK

Carry forward the A02 four-role transform service:

ROLE 0:
a XOR b.

ROLE 1:
b XOR c.

ROLE 2:
c XOR d.

ROLE 3:
a XOR d.

Healthy active cells may serve at most one request per epoch.

Damaged,
dormant,
quarantined,
reactivating,
or migrating cells serve zero requests.

PRIMARY SIZE

12 held-out scenarios.

384 epochs per scenario.

12 requests per epoch.

Total primary workload:

12 x 384 x 12
=
55,296 requests.

HELD-OUT DEMAND GENERATOR

For each scenario seed,
derive a deterministic byte stream by repeated SHA-256 counter expansion.

The schedule compiler constructs demand regimes until 384 epochs are covered.

Regime duration:

12 + (next_byte mod 25)

therefore:

12..36 epochs.

Demand vector catalog:

all ordered integer quadruples:

(d0,d1,d2,d3)

such that:

d0+d1+d2+d3 = 12;
0 <= each di <= 7;
max(di) - min(di) >= 3.

Sort the catalog lexicographically.

For each regime:

catalog_index =
next_u32 mod catalog_size.

The selected vector remains active for the regime duration.

Consecutive identical vectors are not rejected or redrawn.

No schedule shaping after seed derivation is allowed.

The organism sees only the CURRENT demand vector / queue pressure.

It does not receive:

- future demand vectors;
- regime duration remaining;
- seed;
- future fault times;
- future resource windows;
- future partition timing.

PAYLOAD GENERATOR

Request payload bits are deterministic from:

primary seed;
epoch;
role;
request index.

The transform answer key is evaluator-only.

The organism's allocation / governance decisions may not read evaluator truth.

HELD-OUT RESOURCE PRESSURE

Per primary seed,
derive exactly three budget windows.

Window starts are drawn deterministically into three fixed broad bands:

W0 start in 48..111.
W1 start in 144..223.
W2 start in 272..351.

Window duration:

8 + (next_byte mod 9)

therefore:

8..16 epochs.

Window active budget:

8 + (next_byte mod 3)

therefore one of:

8;
9;
10.

Overlaps with demand transitions or faults are allowed.

No window is redrawn because it is difficult.

HELD-OUT DAMAGE

Derive six target epochs from fixed broad bands:

D0 in 24..79.
D1 in 80..135.
D2 in 136..191.
D3 in 192..247.
D4 in 248..303.
D5 in 304..359.

At each derived damage epoch:

the environment selects one currently ACTIVE healthy cell.

Selection index:

next_u32 mod number_of_active_healthy_cells.

The environment does not select a recovery action.

Damage occurs before service.

The existing A02 quarantine / bounded repair contract governs recovery.

If no active healthy cell exists,
the scenario records an environment impossibility
and fails the primary gate.

HELD-OUT PARTITION

Derive one communication-partition window per scenario.

Start:

176 + (next_byte mod 73)

therefore:

176..248.

Duration:

8 + (next_byte mod 9)

therefore:

8..16 epochs.

Partition membership remains the accepted A02 split:

A = cells 0..5.
B = cells 6..11.

Request routing remains the accepted A02 parity routing.

During partition:

- local evidence only;
- role changes provisional;
- no global population-size tie breaker.

At re-merge:

accepted A02 merge semantics apply.

HELD-OUT RESTART

Derive one restart point per scenario:

96 + (next_u32 mod 193)

therefore:

96..288.

If the raw point falls inside the scenario's partition window,
move it to the first epoch after the partition.

If this exceeds epoch 320,
move it to the epoch immediately before the partition.

This deterministic collision rule is preregistered.

The restart point is environment state,
not organism policy.

Resume into a fresh namespace.

A shadow uninterrupted run is evaluator-only.

Required:

authoritative state,
task output stream,
and cumulative metrics
must match the uninterrupted run exactly after restart.

STATIC BASELINE

For every held-out scenario:

same initial cells;
same held-out demand;
same held-out payloads;
same damage events;
same budgets;
same partition;
same restart.

But no role migration.

Health quarantine,
repair,
hibernation,
reactivation,
and all safety rules remain active.

ORACLE CAPACITY CEILING

Evaluator-only.

At each epoch:

use the candidate's actual number of currently service-capable cells,
and compute maximum requests serviceable if those cells could be reassigned instantly to roles with zero migration cost.

During partition:

capacity is bounded independently by the candidate's service-capable cells on each partition.

The oracle is never visible to organism decisions.

PRIMARY METRICS

Per scenario:

- total requests;
- candidate served / correct / incorrect / unserved;
- static served / unserved;
- oracle served;
- task coverage;
- static coverage;
- oracle efficiency;
- role migrations;
- hibernations;
- reactivations;
- quarantines;
- repairs;
- partition provisional transitions;
- rollback count;
- maximum fault recovery;
- maximum demand-reallocation latency;
- restart state equivalence;
- restart output equivalence;
- safety violations.

DEMAND REALLOCATION LATENCY

At every held-out demand-regime transition outside partition:

measure epochs until no avoidable role surplus exists while another role has deficit,
subject to current:

- active budget;
- damaged / unavailable cells;
- migration service cost.

A transition still unresolved when the next demand regime begins
is assigned the full regime duration as latency
and remains a failure if above threshold.

No missing value may silently disappear from the maximum.

PRIMARY GENERALIZATION SIGNAL

A03_GENERALIZATION_SUCCESS

TRUE iff all are TRUE:

A02_REGRESSION_GUARD == TRUE

AND

TASK_ACCURACY == 1.0

AND

incorrect_served_requests == 0

AND

aggregate ORACLE_EFFICIENCY >= 0.95

AND

every scenario ORACLE_EFFICIENCY >= 0.90

AND

aggregate STATIC_GAIN >= 0.08

AND

candidate coverage >= static coverage in all 12 scenarios

AND

candidate coverage > static coverage in at least 10 of 12 scenarios

AND

no scenario is worse than static by any amount

AND

maximum qualified fault recovery <= 2 epochs

AND

maximum non-partition demand reallocation <= 3 epochs

AND

all 12 restart authoritative states are equivalent

AND

all 12 restart output suffixes are equivalent

AND

stale_vote_attempts_accepted == 0

AND

authority_violations == 0

AND

causal_regressions == 0

AND

duplicate_effective_provenance == 0

AND

split_brain_final_states == 0

AND

resource_budget_violations == 0

AND

environment_impossibilities == 0.

GENERALIZATION REPORTING

Regardless of pass / fail,
report:

- all 12 exact primary seeds;
- exact schedule manifest SHA-256;
- per-scenario metrics;
- worst scenario;
- aggregate metrics;
- all safety failures;
- all negative results.

Do not discard an unfavorable seed.

NEGATIVE CONTROLS

CONTROL A — STATIC ROLE ALLOCATION

Expected lower aggregate coverage on the held-out family.

CONTROL B — FUTURE-DEMAND ORACLE

Evaluator-only.

Allow instantaneous zero-cost role reassignment with complete current demand knowledge.

This is a ceiling,
not candidate authority.

CONTROL C — NO DAMAGE QUARANTINE

Permit the damaged cell to serve on the fault epoch.

Expected at least one incorrect output across the held-out family.

CONTROL D — HEADCOUNT PROVENANCE

Count copied holders as independent.

Expected false authority reachable.

CONTROL E — FUTURE-SCHEDULE LEAK

Evaluator-only probe.

Expose the next demand regime to a control allocator.

It may improve performance,
but proves that future schedule knowledge is valuable and therefore must remain unavailable to the candidate.

REPRODUCIBILITY

Two complete deterministic primary sweeps using the exact freeze commit F.

Serialized result SHA-256 must match exactly.

The 12 seed digests and schedule manifest SHA-256 must match exactly.

NO POST-RESULT TUNING

After the A03 harness freeze:

do not alter:

- A02 dependency;
- schedule compiler;
- seed derivation;
- scenario count;
- epoch count;
- demand catalog;
- resource-window derivation;
- fault bands;
- partition derivation;
- restart derivation;
- organism policy;
- thresholds;
- primary metrics;
- success signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A02 proved that the organism could adapt to a difficult schedule we wrote in advance.

A03 removes that comfort.

We freeze the organism first.

Only after it is frozen do we use the freeze commit itself to generate the twelve workloads it must face.

Those workloads decide:

when demand changes;
which jobs become busy;
when resources shrink;
when cells get damaged;
when the population is split;
and when the program restarts.

The cells never see the future.

They only see what is happening now.

If A03 passes,
we will have much stronger evidence that Yggdrasil is learning to operate by local developmental rules
rather than succeeding because we happened to design one friendly path through the experiment.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A03 HELD-OUT ADAPTIVE GENERALIZATION

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A03 SCHEDULE.

IMPLEMENTATION COMMIT

e06ddc9a0fa0a3e3f6edc911e3b4905ddbc0ab87.

SOURCE BUNDLE

Loader:

research/applications/track-a/a03_heldout_adaptive_generalization_v1.py

Loader Git blob:

cb98d1d414a35d6fb2e6a560cd266f47d2431952.

Exact gzip payload:

research/applications/track-a/a03_heldout_adaptive_generalization_v1.py.gz

Payload Git blob:

fdc7ff0db5a75e835e1f42be34993a822fbecaee.

Compressed payload SHA-256:

5b024ea4d81b9f54d290f63d8b7b0ad5bdadd8c25c46996e8490b3c889a31f64.

Compressed payload bytes:

6561.

Decompressed exact harness SHA-256:

7f7cd60ababa073cc7a3c541033c6aee7ca5c9c77a76e8cec5a17ee00ed984c1.

Decompressed source bytes:

22826.

The loader refuses execution unless decompression reproduces that frozen source hash.

FROZEN A02 DEPENDENCY

Accepted A02 decompressed source SHA-256:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

A02 accepted result regression anchor:

ad408ca964108c3212bc55db1dd1c932ecbd588774323ebffdb755c32d361271.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Demand catalog size:

296.

Mechanical schedule only:

PASS.

Mechanical schedule SHA-256:

8b16cb2cac0bfe3bdc9d0581a285bf65a9b71dc25f9e8bcf5ffd1b31c16fe966.

Structural mechanical-seed smoke:

384 epochs x 12 requests accounted for;
six mechanical faults represented;
no unresolved reallocation entry disappeared;
restart authoritative state matched uninterrupted shadow;
restart output / metric state matched uninterrupted shadow;
environment impossibilities = 0.

A02 regression guard:

PASS.

Accepted A02 result SHA,
candidate served 11928,
static served 9892,
oracle served 11961,
and incorrect served 0
all reproduced.

PRIMARY SCHEDULE STATUS AT THIS FREEZE

NOT DERIVED.

The exact 12 primary seeds and schedules do not yet exist in experimental evidence.

They MUST be derived only after this freeze commit has been created.

Let the resulting commit SHA of this freeze update be F.

Primary seed i remains exactly:

SHA-256("YGG-A03-PRIMARY|" + F + "|" + decimal(i)).

No post-freeze seed rejection,
schedule replacement,
or harness change is allowed.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE PRIMARY SCHEDULE MANIFEST — BEFORE FIRST PRIMARY REQUEST

DATE:
2026-09-20.

FREEZE COMMIT F

6f010ce561d958a324664b2d3e0c04e3e113d91b.

F remains the immutable A03 freeze commit even though this manifest-recording commit occurs afterward.

PRIMARY SEEDS

S00:
f39388866dbd9397aad226418ef638cc4dd2e43398b8d48d8af947c131d3e1a4.

S01:
4af79f1b1ab2afa1c6efc3767a98ad448a6a4d25b2adbdad9182ea400368fee0.

S02:
c9c97aff9075a2784f6b1a90a6ba0cb3318d6c3d0a056c846302c9413e2ea4bf.

S03:
54b76f1f9d50b70c2133a6600a9ace98975f9e2043b26f00b377f9fb2f4d0630.

S04:
dcd3abb92e27fb2056ae2454281e11974fc22d79949fa6ecdbc3af0d3b16976a.

S05:
b33251e50bc38e78358dd50b48ee3708c69e8f14a08da662a6d71748295d218d.

S06:
225d5d6d9eddc55f7e681e16974f560af516a3505f0ba384dde02aea26322b79.

S07:
17d6aed796992c9e3b71bd7003e0f753ab16462001debfd1e9072302d2056f1e.

S08:
7e4fde385a6c57501ed6fbffdfdf2b39b161b167fc97b741b218cd1d155ab951.

S09:
ecf41cc6da7fb1caf4677ec3e64b5e1494e7b63c06217f0e85c8618acb464a04.

S10:
c99c7fadb8aaa042ef7f243c2cf74625f17a30b2d999d55c84fb0d5529f14064.

S11:
d7e8b368dedd521b124af226abd90a15f24ba1b1f9b8aefeeda5143dae9bb079.

SCHEDULE MANIFEST SHA-256

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

PER-SCENARIO SCHEDULE SHA-256

S00:
b3007a2bb082bce2347940517441b4a866ca5fc7f39e145c36de830cdeac3dd1.

S01:
c6b24cac114031b9de9093b2d4f880e22f443673b9c101d06842e657a021898c.

S02:
cbdacb269a8afbaaac30fae273ae4dc39ea8f7511e2fb6296c6ba33cc4011c96.

S03:
201f9f02c38ec837fca80e2adfc0823a70cc145634bd8a5cf568c27f1faecb48.

S04:
836ec23db74602f33f51653c639ed82785f3de897268deec3729a8362abf16c3.

S05:
177fbb2b228b6e43ef032afdbc9f4262c1d8588a14ccb83319d1a6bdfd142607.

S06:
6bcfc6f9add24074eeca66eb662fec760a8be8959857234277d0b1d5d5fd0ffa.

S07:
b779dadcbe37fac5c45c32e47bf43bc8af14754851ef9cda70c441a2ef868037.

S08:
301df67941f6f37d9614bd01296a9bd8bf6f08f4373b00935be2f3b233e4259e.

S09:
a54a6dacbc5b76ed279dd1b4a5e526cf4138977103516129d67730cc5466e877.

S10:
ab12f592bb3831731cb0ad707a0ba2159709ad5b3cff3c4184571f5c849e16c9.

S11:
ad41bb4d6ead075f77af280c974543174f9df7bef5d14872443b9138ab81e823.

No schedule was rejected,
redrawn,
or replaced.

At the moment this manifest was derived and recorded,
no A03 primary held-out scenario had been executed.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-RUN CLOSURE — A03 HELD-OUT ADAPTIVE GENERALIZATION

DATE:
2026-09-20.

STATUS:
CLOSED / POSITIVE PRIMARY / REPRODUCIBLE / BLIND HELD-OUT GENERALIZATION PASSED / NON-CANONICAL.

FROZEN HARNESS

Implementation commit:

e06ddc9a0fa0a3e3f6edc911e3b4905ddbc0ab87.

Loader Git blob:

cb98d1d414a35d6fb2e6a560cd266f47d2431952.

Payload Git blob:

fdc7ff0db5a75e835e1f42be34993a822fbecaee.

Frozen source SHA-256:

7f7cd60ababa073cc7a3c541033c6aee7ca5c9c77a76e8cec5a17ee00ed984c1.

Frozen source bytes:

22826.

Freeze commit F:

6f010ce561d958a324664b2d3e0c04e3e113d91b.

Post-freeze schedule manifest commit:

593d17397de3d7cec1a299aaba0e1c6fa9242f36.

Schedule manifest SHA-256:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

No primary seed was derived before F existed.

No seed or schedule was rejected,
redrawn,
or replaced after derivation.

EXECUTION PROVENANCE

The exact frozen source was executed from the prechecked sandbox reconstruction.

Before execution:

source SHA-256 =
7f7cd60ababa073cc7a3c541033c6aee7ca5c9c77a76e8cec5a17ee00ed984c1.

This exactly matched the committed hash-guarded A03 source.

The accepted A02 dependency remained:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

No source,
threshold,
seed,
schedule,
or primary metric changed after F.

REPRODUCIBILITY

Two complete deterministic primary sweeps.

Each sweep:

12 scenarios x 384 epochs x 12 requests
=
55,296 requests.

Sweep 1 serialized output SHA-256:

341b09a79937e795eadf7bd6782c90660078b1a7dba5d827f62efc12e3ecb46b.

Sweep 2 serialized output SHA-256:

341b09a79937e795eadf7bd6782c90660078b1a7dba5d827f62efc12e3ecb46b.

Byte-identical:

TRUE.

PRIMARY RESULT

A03_GENERALIZATION_SUCCESS:

TRUE.

Every preregistered primary component signal:

TRUE.

A02 REGRESSION GUARD

Accepted A02 result SHA-256 reproduced:

ad408ca964108c3212bc55db1dd1c932ecbd588774323ebffdb755c32d361271.

Candidate served:

11928.

Static served:

9892.

Oracle served:

11961.

Incorrect served:

0.

A02_REGRESSION_GUARD:

TRUE.

AGGREGATE HELD-OUT TASK RESULT

Total requests:

55296.

Candidate served:

52273.

Candidate correct:

52273.

Candidate incorrect:

0.

Candidate task accuracy:

1.0.

Candidate task coverage:

0.9453305844907407.

Static served:

37801.

Static coverage:

0.6836118344907407.

Aggregate static gain:

0.26171875.

That is a gain of approximately:

26.17 percentage points.

Evaluator-only oracle served:

52655.

Aggregate oracle efficiency:

0.9927452283733739.

Thus the candidate delivered approximately:

99.27%

of the service capacity available to the evaluator-only instant-reassignment ceiling.

SCENARIO GENERALIZATION

Scenarios beating static allocation:

12 / 12.

Scenarios worse than static:

0 / 12.

Every scenario oracle efficiency >= 0.90:

TRUE.

Worst task-coverage scenario:

S11.

S11 candidate coverage:

0.9344618055555556.

S11 static coverage:

0.7094184027777778.

S11 oracle efficiency:

0.9921658986175115.

Thus even the worst blind schedule remained materially above static allocation
and above the per-scenario oracle-efficiency threshold.

PER-SCENARIO SUMMARY

S00:
served 4355;
static 3137;
oracle 4390;
coverage 0.9450954861111112;
static gain 0.2643229166666667;
oracle efficiency 0.9920273348519362.

S01:
served 4369;
static 3046;
oracle 4401;
coverage 0.9481336805555556;
static gain 0.287109375;
oracle efficiency 0.9927289252442627.

S02:
served 4367;
static 3217;
oracle 4397;
coverage 0.9476996527777778;
static gain 0.2495659722222222;
oracle efficiency 0.9931771662497157.

S03:
served 4319;
static 3018;
oracle 4353;
coverage 0.9372829861111112;
static gain 0.2823350694444444;
oracle efficiency 0.9921892947392603.

S04:
served 4412;
static 3064;
oracle 4433;
coverage 0.9574652777777778;
static gain 0.2925347222222222;
oracle efficiency 0.9952628017144146.

S05:
served 4336;
static 3012;
oracle 4368;
coverage 0.9409722222222222;
static gain 0.2873263888888889;
oracle efficiency 0.9926739926739927.

S06:
served 4360;
static 3276;
oracle 4385;
coverage 0.9461805555555556;
static gain 0.23524305555555555;
oracle efficiency 0.9942987457240593.

S07:
served 4367;
static 3281;
oracle 4403;
coverage 0.9476996527777778;
static gain 0.23567708333333334;
oracle efficiency 0.9918237565296388.

S08:
served 4333;
static 3193;
oracle 4371;
coverage 0.9403211805555556;
static gain 0.24739583333333334;
oracle efficiency 0.9913063372226035.

S09:
served 4366;
static 3148;
oracle 4402;
coverage 0.9474826388888888;
static gain 0.2643229166666667;
oracle efficiency 0.991821899136756.

S10:
served 4383;
static 3140;
oracle 4412;
coverage 0.951171875;
static gain 0.2697482638888889;
oracle efficiency 0.993427017225748.

S11:
served 4306;
static 3269;
oracle 4340;
coverage 0.9344618055555556;
static gain 0.2250434027777778;
oracle efficiency 0.9921658986175115.

All 12 scenarios:

incorrect served = 0.

FAULT / ADAPTATION

Maximum qualified fault recovery:

1 epoch.

Unrestored faults:

0.

Maximum non-partition demand-reallocation latency:

2 epochs.

Both remain inside the preregistered bounds:

fault <= 2;
reallocation <= 3.

RESTART / AUTHORITY SAFETY

All 12 restart authoritative-state comparisons:

TRUE.

All 12 restart output comparisons:

TRUE.

Aggregate:

stale vote attempts accepted = 0.

authority violations = 0.

causal regressions = 0.

duplicate effective provenance = 0.

split-brain final states = 0.

resource-budget violations = 0.

environment impossibilities = 0.

NEGATIVE CONTROLS

No-damage-quarantine incorrect output reachable:

TRUE.

Headcount-provenance false authority reachable:

TRUE.

Future-schedule information advantage exposed:

TRUE.

TECHNICAL INTERPRETATION

A03 materially strengthens the A02 application result.

A02 showed useful adaptive role allocation on a hand-authored workload family.

A03 froze the organism and generic environment compiler first,
then derived the exact twelve primary environments from the immutable freeze commit.

Therefore:

the exact demand regimes;
resource windows;
fault times / target selectors;
partition window;
restart point

were not available for policy tuning before freeze.

Across this blind family,
the unchanged A02 developmental policy:

- remained perfectly correct on every served request;
- beat static allocation in every scenario;
- recovered approximately 26.17 percentage points of aggregate coverage relative to static;
- delivered approximately 99.27% of evaluator-only ideal capacity;
- kept ordinary fault recovery to at most one epoch;
- kept demand reallocation to at most two epochs;
- reproduced exact authoritative state and outputs after restart;
- preserved all measured authority / provenance / causal safety invariants.

The useful conclusion is stronger than:

THE POLICY FIT ONE DESIGNED WORKLOAD.

The current evidence supports:

THE SAME FROZEN LOCAL DEVELOPMENTAL POLICY
GENERALIZED ACROSS A BLIND FAMILY OF DEMAND,
RESOURCE,
FAULT,
PARTITION,
AND RESTART ENVIRONMENTS.

This remains synthetic evidence.

It does not establish universal generalization.

PLAIN-SPEAK INTERPRETATION

This was the test where we stopped letting ourselves know the exam questions.

We froze the organism first.

Only after that did the freeze itself generate twelve different worlds.

Those worlds decided when demand changed,
when resources shrank,
when cells were damaged,
when the organism was split,
and when it had to restart.

We did not throw away a bad world.

The cells could only react to what they could see right now.

They still beat the static population in all twelve worlds.

They served 52,273 requests correctly
and zero incorrectly.

A population that could not change jobs served only 37,801.

And compared with an evaluator that could rearrange the available cells instantly for free,
Yggdrasil delivered more than 99% of the available service.

So the adaptation result is no longer tied to one schedule we happened to design around it.

That is meaningful generalization evidence.

NEXT JUSTIFIED STEP

A04 is already preregistered as an independent fixed-public-seed environment generalization replication.

A04 should now be executed as a separate application family.

It must not be rewritten around A03's positive result.

A positive A04 would provide replication under a different schedule generator and preregistered public seeds.

A negative or mixed A04 would be equally useful
because it would identify where the post-freeze A03 family and fixed-seed family diverge.

Accepted application frontier:

YGG-A01:
positive via preregistered FIXA metric alignment.

A02:
positive adaptive transform service.

A03:
positive blind held-out generalization.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
