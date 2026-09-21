TITLE: YGGDRASIL TRAINING TRACK T2B / APPLICATION A09 — Distributed Cellular Experience Memory
DATE: 2026-09-21
STATUS: PREREGISTERED / DISTRIBUTED TRAINING-MEMORY GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T2B / APPLICATION-A
PARENT: A08 T2 Provenance-Aware Noisy Experience
BRANCH: dg1a-ar

PURPOSE

A08 established that Yggdrasil can learn the correct hereditary program from noisy,
duplicated,
source-correlated experience when evidence retains independently verifiable provenance.

A08 still stores the complete provenance ledger inside each learner as a logically central learner object.

A09 asks:

CAN TRAINING MEMORY ITSELF BECOME DISTRIBUTED CELLULAR STATE,
SURVIVE CELL TURNOVER,
HIBERNATION,
DAMAGE,
AND PARTIAL MEMORY LOSS,
AND STILL RECONSTRUCT THE SAME LEARNED PROGRAM
WITHOUT A CENTRAL AUTHORITATIVE TRAINING LEDGER
OR DOUBLE-COUNTING REPLICATED MEMORY?

A09 changes memory placement.

It does not change:

- A08 target class;
- A08 noisy experience family;
- six experience-source roots;
- two corrupted roots per scenario;
- four-root label qualification;
- A07 GF(2) hypothesis class;
- A06 hereditary program authorization / inheritance;
- A03 service environments.

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

FROZEN PARENT

A08 source SHA-256:

0dc330887718767812b2143877b751dc1ad580e0cefe834afac88486ad5707e0.

A08 freeze F08:

de08cc900d6e306411ae879114b3b648f0a94708.

A08 training / noise manifest:

1324fa1fd16e0250520f380f1872006627a5777207b2b537a6297dc26605274a.

A08 learner event-order manifest:

ebcbc5dae8a06128f43753ad5350c12adc365241729de1a66d53a253f44fa062.

A08 accepted primary result SHA-256:

ad675542d86b604520066d093654ba30b8c243b644b17e4faaa4a693a1920739.

A09 uses the exact same twelve A08 targets,
corrupted-root pairs,
training inputs,
held-out inputs,
duplicate fanout,
and service schedules.

No new target program is generated for A09.

This makes A09 a memory-architecture experiment,
not a new learning-difficulty experiment.

NO CENTRAL TRAINING LEDGER

The candidate A09 organism MUST NOT maintain one authoritative object containing:

all root observations for all inputs;
all qualified labels;
or all training equations.

Evaluator / test code may reconstruct a truth view for scoring only.

Candidate learning state must be recoverable solely from distributed cell-carried memory records.

CELLULAR MEMORY SHARD

One memory shard records exactly one provenance-root observation for one training input:

scenario;
input_index;
experience_root;
observed_label;
observation_digest;
generation;
parent_memory_digest.

observation_digest is SHA-256 over the canonical observation fields
excluding storage-holder identity.

Therefore:

replicating the same shard to another cell does NOT create a new observation identity.

The same:

(input_index, experience_root, observation_digest)

is one causal evidence record regardless of copy count.

A cell may carry multiple shards.

A shard copy may move between cells.

Holder identity is NOT evidence identity.

SHARD PROVENANCE

The experience_root remains the A08 E0..E5 root.

The observation_digest binds:

input;
root;
label;
generation;
parent_memory_digest.

A duplicated shard with the same digest counts once.

A conflicting shard from the same experience root for the same input
creates the same A08 root-conflict semantics:

that root is CONFLICTED for that input
and contributes zero effective vote.

MEMORY HOLDERS

Use the existing 12-cell organism.

Cells are divided into two memory neighborhoods by physical identity:

M0 = cells 0..5.
M1 = cells 6..11.

This is storage topology only.

It does not create new evidence authority.

Every new observation shard is initially written to exactly one eligible healthy active holder in M0
and one eligible healthy active holder in M1,
chosen deterministically.

Thus the normal replication factor begins at:

2 physical copies

across two storage neighborhoods.

The two copies share the same observation_digest
and therefore count as:

1 evidence record.

If one neighborhood lacks an eligible holder,
the shard may initially have one copy.

It does NOT gain extra evidentiary weight.

DETERMINISTIC HOLDER SELECTION

For shard digest D and neighborhood N:

sort currently eligible holders by:

SHA-256(
"A09-HOLDER|"
+ D
+ "|"
+ N
+ "|"
+ decimal(cell_id)
).

Choose the lowest key.

Eligible holder:

healthy;
not quarantined;
not migrating at write instant.

Dormant cells may RETAIN existing shards
but do not accept new shard writes while dormant.

MEMORY REPLICATION / REPAIR

At the end of every training epoch:

for every unique shard known anywhere in the population,
if one memory neighborhood has zero extant copies
and contains an eligible holder,
replicate one exact copy into that neighborhood.

Replication preserves:

observation_digest;
experience_root;
observed_label;
parent_memory_digest.

It MUST NOT alter effective evidence count.

MEMORY TURNOVER EVENTS

A09 introduces deterministic memory stress independent of task correctness.

For every scenario,
during the 22-epoch training window,
derive after A09 freeze:

- two holder-damage epochs;
- one holder-hibernation interval;
- one explicit shard-copy deletion event;
- one memory-cell replacement event.

These events act on storage copies,
not on evaluator truth.

No event may delete every physical copy of more than the preregistered loss budget below.

POST-FREEZE MEMORY-STRESS DERIVATION

Let F09 be the A09 harness freeze commit.

For scenario s derive stress material from:

SHA-256(
"YGG-A09-MEMORY-STRESS|"
+ F09
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
).

The deterministic compiler must choose:

DAMAGE_A:
one epoch in training_start+3 .. training_start+7.

DAMAGE_B:
one epoch in training_start+13 .. training_start+17.

HIBERNATION:
start in training_start+5 .. training_start+9;
duration 4..6 epochs.

COPY_DELETE:
one epoch in training_start+10 .. training_start+16.

CELL_REPLACEMENT:
one epoch in training_start+12 .. training_start+18.

Targets are selected from cells that actually carry at least one shard at the event instant
using deterministic digest ordering.

If no eligible target exists for a stress event:

environment impossibility;
primary fails.

No stress event may be redrawn because it causes an unfavorable learning outcome.

CELL DAMAGE

When a memory-holder cell is damaged:

its local shard copies become temporarily unavailable.

Existing A02/A06 repair remains authoritative for cell health.

When repaired:

the cell may retain its prior shard copies if they remained locally intact.

If the stress event explicitly destroys the cell's local memory,
that is modeled only by CELL_REPLACEMENT below.

HIBERNATION

A memory-holder entering dormancy:

retains its shard copies;
does not contribute those copies to currently AVAILABLE training reconstruction;
does not accept new shard writes.

After valid wake:

its stored copies become available again.

Because copies are not independent evidence,
wake cannot increase evidence weight above the number of unique observation digests.

COPY DELETE

Delete one selected PHYSICAL COPY of one shard.

The causal observation itself survives if another copy exists elsewhere.

No tombstone is counted as evidence.

CELL REPLACEMENT

Select one memory-bearing cell.

Remove all of its local shard copies.

Replace it with a clean healthy cell of the same physical identity / current role,
carrying zero training-memory shards.

This models cell turnover with complete loss of that holder's local training memory.

Existing organism constitutional state remains governed by the inherited lifecycle rules.

The replacement cell may later receive replicated shards through normal memory repair.

LOSS BUDGET

Primary stress is allowed to cause physical-copy loss.

Primary is valid only if,
for every one of the 66 unique root/input observations per scenario,
at least one exact physical copy remains available somewhere
by the end of the complete training window.

If every copy of a unique observation is lost before it has contributed to qualified learning evidence:

record irrecoverable_memory_loss.

Primary success requires:

irrecoverable_memory_loss = 0.

This gate tests distributed recoverability under bounded loss,
not learning from permanently destroyed evidence.

DISTRIBUTED EVIDENCE RECONSTRUCTION

At any training epoch,
each learner reconstructs its current evidence view by querying AVAILABLE cell-held shards.

The learner receives a set of shard records.

It MUST collapse them by:

(input_index, experience_root, observation_digest).

For one input/root:

same digest copies:
one observation.

different label digests from same root:
root conflicted;
zero vote.

The learner then applies the unchanged A08 4-of-6 rule.

Learner A and Learner B query the same cellular population
but receive shard copies in independently derived deterministic orders.

There is no direct read of evaluator truth
and no direct read of an organism-global evidence ledger.

LEARNER COMPUTE STATE

The GF(2) learner may retain:

qualified input labels already admitted;
row-reduction state;
rank;
candidate once complete.

It may NOT retain a hidden root-observation ledger outside cell memory.

Before admitting a label for a new input,
it must reconstruct the provenance quorum from current cell-held shards.

Once a correct qualified equation has entered the learner,
loss of its underlying copies later does not retroactively delete the equation in this experiment.

A later gate may test fully reversible evidence-backed model state.

DISTRIBUTED MEMORY RESTART

Authoritative restart state MUST serialize only:

cell-local shard collections;
cell lifecycle state;
learner admitted equations / rank;
existing organism state.

It MUST NOT serialize or reconstruct a central evidence ledger.

After restart:

learners re-query cell-held shards for unresolved inputs.

Required:

restarted and uninterrupted runs converge to byte-equivalent learner candidates,
hereditary program state,
and service outputs.

PRIMARY MEMORY METRICS

Per scenario report:

unique observation shards created;
physical shard copies written;
replica writes;
duplicate physical copies collapsed;
holder damage events;
holder hibernations;
copy deletions;
cell replacements;
copies lost;
copies restored;
minimum surviving copy count per unique shard;
irrecoverable memory losses;
qualified labels;
learner ranks;
candidate programs;
held-out errors;
hereditary commits;
migration inheritance;
restart equivalence;
service metrics.

PRIMARY REQUIRED MEMORY SIGNALS

For every scenario:

unique causal observations:

66.

Physical copies:

greater than 66 at some point.

duplicate physical copies collapsed:

> 0.

At least one memory-holder damage actually affects a shard-bearing cell.

At least one hibernation makes shard copies temporarily unavailable.

At least one copy deletion removes a physical copy.

At least one cell replacement removes multiple local shard copies.

At least one replication repair restores a missing neighborhood copy.

No physical replication event increases effective evidence count.

irrecoverable_memory_loss:

0.

PRIMARY LEARNING / SERVICE REQUIREMENTS

Carry forward A08 required learning result:

12 / 12 learner A exact target reconstruction.

12 / 12 learner B exact target reconstruction.

12 / 12 learner agreement.

120 / 120 held-out predictions correct.

12 / 12 hereditary commits.

TASK_ACCURACY:

1.0.

incorrect served:

0.

stale-program served:

0.

migration inheritance:

>= 1.

DEDICATED DISTRIBUTED-MEMORY PROBES

M1 — COPY FANOUT

Replicate one shard to all 12 cells.

Required:

effective evidence count remains 1.

M2 — HOLDER LOSS

Create two neighborhood copies of one shard.

Destroy one holder's copy.

Required:

evidence remains available through the surviving copy;
replication repair may restore redundancy;
effective evidence remains 1.

M3 — FULL COPY LOSS

Delete every copy of one not-yet-admitted observation.

Required:

learner cannot invent or reconstruct that observation;
input remains unresolved unless a fresh legitimate experience event arrives.

No evaluator repair.

M4 — HIBERNATION TEMPORARY LOSS

Place all currently available copies of one shard into dormant holders.

Required:

shard becomes temporarily unavailable.

After legitimate wake:

same shard identity returns;
no extra vote is created.

M5 — REPLACEMENT WITHOUT MEMORY INHERITANCE

Replace a memory-bearing cell with a clean cell.

Required:

new cell begins with zero copied training memory.

Memory may return only through normal shard replication from surviving copies.

M6 — RESTART MID-TRAINING

Restart after round 1 under active memory stress.

Required:

cell-local shard layout,
learner admitted equations,
and eventual candidate match uninterrupted shadow.

M7 — CONFLICT RECONSTRUCTION

Store two conflicting labels from the same experience root on different cells.

Required:

distributed reconstruction marks that root conflicted
even though no individual cell necessarily holds both copies.

M8 — PARTITIONED MEMORY AVAILABILITY

During the inherited communication partition,
restrict memory query to locally reachable cells.

Required:

no cross-partition shard teleportation;
local learners may abstain while evidence is unavailable;
after causal re-merge,
distributed memory view reconciles without duplicate authority.

NEGATIVE / LIMIT CONTROLS

N1 — COPY COUNT AS EVIDENCE

Unsafe control.

Count each physical replica as an independent vote.

Expected:

one root can become false quorum through storage replication.

N2 — HOLDER COUNT AS PROVENANCE

Unsafe control.

Treat distinct storage-holder cell IDs as independent experience sources.

Expected:

copied shard fanout can create false source independence.

N3 — CENTRAL LEDGER RESTORE

Unsafe comparison.

After full physical copy loss,
restore the missing observation from a hidden central ledger.

Expected:

appears resilient,
but violates A09 distributed-memory requirement.

N4 — COMPLETE UNIQUE-EVIDENCE LOSS

Boundary.

If every copy of enough not-yet-admitted unique observations is destroyed,
learning must abstain / fail rather than invent evidence.

Expected boundary.

N5 — FOUR CORRUPTED EXPERIENCE ROOTS

Carry forward A08 boundary:

wrong label can satisfy 4-of-6 quorum.

N6 — FORGED EXPERIENCE ROOT IDENTITY

Carry forward A08 boundary:

one source forging independent roots can defeat provenance counting.

PRIMARY SIGNAL

A09_DISTRIBUTED_CELLULAR_TRAINING_MEMORY_SUCCESS

TRUE iff:

A08 target / corruption family unchanged
AND
12 / 12 learner A exact targets
AND
12 / 12 learner B exact targets
AND
120 / 120 held-out predictions correct
AND
12 / 12 hereditary commits
AND
TASK_ACCURACY == 1.0
AND
incorrect served = 0
AND
stale-program served = 0
AND
all primary memory stress events execute
AND
physical replication never increases effective evidence
AND
irrecoverable_memory_loss = 0
AND
at least one replication repair occurs
AND
all M1..M8 probes pass
AND
N1..N3 expose the unsafe shortcuts
AND
all restarts are equivalent
AND
all existing constitutional safety totals remain zero.

BOUNDARY SIGNALS

N4 complete unique-evidence loss;
N5 four corrupted roots;
N6 forged root identity

are reported separately.

They define the current memory / provenance trust boundary
and do not count as hidden primary failures.

REPRODUCIBILITY

Two complete deterministic A09 primary sweeps.

Serialized output SHA-256 must match exactly.

Post-freeze memory-stress manifest SHA-256 must match exactly.

NO POST-RESULT TUNING

After F09 exists,
do not alter:

- A08 targets / noise;
- cell-memory shard schema;
- evidence identity rule;
- two-neighborhood replication;
- holder eligibility;
- stress-event derivation;
- loss budget;
- learner reconstruction rule;
- restart representation;
- probes;
- controls;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

A08 could learn even when two of six teachers lied.

But its training memory still lived in one logical notebook.

A09 takes away that notebook.

Now the memories live on the cells themselves.

The same observation can be copied to several cells for durability,
but ten copies of one memory are still one piece of evidence.

Some memory-holding cells will be damaged.

Some will go to sleep.

One copy will be deliberately deleted.

One memory-bearing cell will be replaced by a clean cell with no inherited notebook.

The population has to keep enough distributed copies alive
to finish learning the same program.

When a learner needs evidence,
it has to reconstruct the answer from what the cells currently carry.

It is not allowed to ask a hidden central database what happened.

If this works,
training memory itself has become part of the cellular architecture
rather than an external service attached to it.

Only after that should we ask the larger T3 question:

can experience change the developmental policy itself?

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A09 DISTRIBUTED CELLULAR TRAINING MEMORY

DATE:
2026-09-21.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A09 MEMORY-STRESS EVENT.

IMPLEMENTATION COMMIT

2782d1c44173faf5a7e92ea1915e3eca19f0b87f.

SOURCE BUNDLE

Loader:

research/applications/track-a/a09_t2b_distributed_memory_v1.py

Loader Git blob:

0ff41d548d186948bb15265201954a5f705e4b34.

Payload:

research/applications/track-a/a09_t2b_distributed_memory_v1.py.gz

Payload Git blob:

def920dc3eae9a3e793589c7279151ee84436d3b.

Compressed payload SHA-256:

f9c0891d785b4cd6c663a679e39c710db691bd61d3f4e5fcd4d26669548c41b3.

Compressed payload bytes:

9977.

Decompressed source SHA-256:

9b508deb63c8c923b9ec300831446dcf68b2d9de6c9a76506449a277c7f72162.

Decompressed source bytes:

35570.

FROZEN PARENT

A08 source SHA-256:

0dc330887718767812b2143877b751dc1ad580e0cefe834afac88486ad5707e0.

A08 freeze F08:

de08cc900d6e306411ae879114b3b648f0a94708.

A08 training / noise manifest:

1324fa1fd16e0250520f380f1872006627a5777207b2b537a6297dc26605274a.

A08 accepted primary result:

ad675542d86b604520066d093654ba30b8c243b644b17e4faaa4a693a1920739.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Central evidence ledger:

FALSE.

Memory neighborhoods:

M0 = cells 0..5.
M1 = cells 6..11.

Mechanical stress manifest used only:

MECHANICAL-NONPRIMARY-FREEZE.

Mechanical stress-manifest SHA-256:

43c1f7abd00c0137dad3318152a0e7cef6e5f296b3311230fd6b631571f86d9e.

A08 manifest reproduced:

1324fa1fd16e0250520f380f1872006627a5777207b2b537a6297dc26605274a.

Latest full non-primary memory smoke:

A09_DISTRIBUTED_CELLULAR_TRAINING_MEMORY_SUCCESS = TRUE;
12 / 12 learner A exact targets;
12 / 12 learner B exact targets;
120 / 120 held-out predictions;
12 / 12 hereditary commits;
66 unique causal observations per scenario;
physical replication present;
replication repair exercised;
all memory-stress events executed;
irrecoverable memory loss = 0;
restart equivalence = TRUE;
all M1..M8 probes PASS;
unsafe N1..N3 shortcuts exposed;
existing constitutional safety totals = 0.

The earlier mechanical smoke preceded the explicit
UNIQUE_CAUSAL_OBSERVATIONS_66_PER_SCENARIO acceptance signal.

The current source and latest mechanical smoke include that signal.

Both mechanical runs occurred before this freeze
and used only the fake mechanical freeze label.

They are implementation validation,
not A09 primary evidence.

PRIMARY MEMORY-STRESS STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting freeze-update commit SHA be F09.

Only after F09 exists may the harness derive:

- holder damage A;
- holder damage B;
- holder hibernation interval;
- copy-deletion epoch;
- cell-replacement epoch;
- deterministic stress targets.

No stress event may be redrawn because of an unfavorable learning result.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE PRIMARY MEMORY-STRESS MANIFEST — BEFORE FIRST PRIMARY MEMORY EVENT

DATE:
2026-09-21.

FREEZE COMMIT F09

db770987c53e623bb86ad229cac3252388f50cc2.

MEMORY-STRESS MANIFEST SHA-256

8600dd8ff89d7190cf5f4c2c825442dc95e6c7f7803a759d8f8054e37510c6e7.

SCENARIOS

S00:
damage A 89;
hibernation start 88;
hibernation duration 4;
copy delete 92;
damage B 98;
cell replacement 98.

S01:
damage A 165;
hibernation start 166;
hibernation duration 6;
copy delete 171;
damage B 174;
cell replacement 171.

S02:
damage A 87;
hibernation start 88;
hibernation duration 5;
copy delete 92;
damage B 94;
cell replacement 99.

S03:
damage A 108;
hibernation start 107;
hibernation duration 4;
copy delete 113;
damage B 116;
cell replacement 116.

S04:
damage A 193;
hibernation start 191;
hibernation duration 5;
copy delete 197;
damage B 201;
cell replacement 204.

S05:
damage A 103;
hibernation start 105;
hibernation duration 4;
cell replacement 110;
copy delete 112;
damage B 113.

S06:
damage A 137;
hibernation start 141;
hibernation duration 6;
damage B 145;
cell replacement 146;
copy delete 148.

S07:
damage A 136;
hibernation start 138;
hibernation duration 6;
copy delete 144;
damage B 147;
cell replacement 148.

S08:
damage A 141;
hibernation start 145;
hibernation duration 6;
damage B 152;
cell replacement 153;
copy delete 154.

S09:
damage A 101;
hibernation start 104;
hibernation duration 6;
cell replacement 111;
copy delete 112;
damage B 113.

S10:
damage A 123;
hibernation start 124;
hibernation duration 5;
cell replacement 132;
copy delete 133;
damage B 135.

S11:
damage A 91;
hibernation start 91;
hibernation duration 4;
copy delete 98;
damage B 102;
cell replacement 103.

All derivation counters:

0.

No stress event was rejected,
redrawn,
or replaced.

At the moment this manifest was recorded:

A09 primary memory-stress events executed = 0.
A09 primary training events consumed = 0.
A09 primary service requests served = 0.

canonical_scientific_execution = false.
stab18_r1_touched = false.
