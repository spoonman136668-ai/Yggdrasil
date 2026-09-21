TITLE: YGGDRASIL TRAINING TRACK T1 / APPLICATION A07 — Experience-Dependent Local Plasticity with Hereditary Commit
DATE: 2026-09-20
STATUS: PREREGISTERED / FIRST TRAINING GATE / NON-CANONICAL
TRACK: YGGDRASIL TRAINING T1 / APPLICATION-A
PARENT: A06 Lineage-Qualified Online Program Inheritance
BRANCH: dg1a-ar

PURPOSE

A06 established that a new role program can enter the organism during its lifetime,
receive independent provenance plus constitutional authorization,
and then propagate as explicit hereditary cell state through migration,
wake,
repair,
and restart.

A06 did NOT learn the program.

The replacement truth table was supplied externally.

A07 asks the first actual training question:

CAN EXPERIENCE PRODUCE A NEW PROGRAM CANDIDATE
THAT GENERALIZES TO UNSEEN INPUTS,
THEN ENTER THE EXISTING A06 AUTHORITY / HEREDITY PIPELINE
WITHOUT BYPASSING CONSTITUTIONAL CONTROL?

A07 separates three layers:

LEARNING:
experience changes local learner state and yields a candidate program;

AUTHORIZATION:
the candidate still requires independent learner-lineage agreement
plus existing organism governance / registry authority;

INHERITANCE:
after commit,
A06 program-version / wake / repair / migration / restart rules remain authoritative.

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

THIS IS TRAINING T1

A07 is supervised local plasticity.

It does not claim:

open-ended learning;
unsupervised learning;
gradient-based neural training;
continual-learning robustness;
adversarial-label robustness;
new-role creation;
general intelligence.

The claim is narrower:

a program not present in source before freeze
can be inferred from labeled experience,
generalize under a frozen hypothesis class,
and become hereditary only through the already-accepted authority path.

FROZEN PARENTS

A06 accepted source SHA-256:

eb7a83320983168fe63d46852ee5d84bebf4c4cf80674ab2a885502e3bfb5a73.

A06 freeze F06:

890046dba7004bdceebb8b49f2516779dc7b08ee.

A06 primary update manifest:

2146c42b61663afede16745123af96bb760a3f886793e9e2d741522c546c2404.

A05 source SHA-256:

9efc8e31c08b60b6decff06c7ffc5b5a1ad10df7bb4440d4b2ab4d1fb5876fce.

A05 task-program manifest:

3fbc3a77eef9068dba92f4206c8c5c7a180efafec2a0105aa52e978dea0fc7f6.

A03 environment manifest:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

A07 begins each scenario with the exact A05 version-0 role programs
and the exact accepted A03 environment schedule.

QUADRATIC LEARNING HYPOTHESIS CLASS

Inputs are four bits:

x0 = a;
x1 = b;
x2 = c;
x3 = d.

A learnable program is:

y =
c
XOR a0*x0
XOR a1*x1
XOR a2*x2
XOR a3*x3
XOR b01*x0*x1
XOR b02*x0*x2
XOR b03*x0*x3
XOR b12*x1*x2
XOR b13*x1*x3
XOR b23*x2*x3.

There are exactly 11 binary coefficients.

The mechanical target catalog contains all coefficient vectors whose 16-point truth table is:

balanced:
exactly eight output ones;

AND

non-affine:
at least one pairwise coefficient bij = 1.

Expected target catalog size:

840.

The catalog is sorted by coefficient-mask integer.

TRAIN / HOLDOUT INPUT SPLIT

The exact 11 training input indices are frozen before primary:

0;
1;
2;
3;
4;
5;
6;
8;
9;
10;
12.

Their 11 x 11 quadratic feature matrix has GF(2) rank:

11.

The exact five held-out input indices are:

7;
11;
13;
14;
15.

No held-out label may enter learner state.

A target in the frozen quadratic class is therefore uniquely identifiable
from the 11 training examples,
while five truth-table outputs remain unseen during learning.

LOCAL LEARNERS

A07 introduces two learner lineages:

LEARNER_A_ROOT = 1 << 42.
LEARNER_B_ROOT = 1 << 43.

Each learner stores its own incremental GF(2) equation set.

The two learners receive the same 11 labeled training examples
but in independently derived deterministic orders.

They do not share:

intermediate row-reduction state;
coefficient guesses;
candidate truth table;
candidate digest.

Each learner may emit a candidate only after its local training matrix reaches rank 11.

Candidate generation:

solve the 11-coefficient system over GF(2);
evaluate the inferred quadratic program over all 16 inputs;
emit the resulting 16-bit truth table.

The learner receives:

input bits;
observed training label.

The learner does NOT receive:

target coefficient mask;
target truth table;
held-out labels;
evaluator correctness;
the other learner's state.

POST-FREEZE TARGET DERIVATION

No A07 primary target program may exist before A07 harness freeze.

Let F07 be the exact Git commit SHA that freezes the A07 harness.

For scenario s:

derive target index material:

SHA-256(
"YGG-A07-TARGET|"
+ F07
+ "|"
+ decimal(s)
).

Interpret the first eight bytes as unsigned big-endian.

target_index =
value mod 840.

target_program =
quadratic_target_catalog[target_index].

If target_program equals the scenario's existing version-0 target-role truth table:

increment a deterministic counter
and derive:

SHA-256(
"YGG-A07-TARGET|"
+ F07
+ "|"
+ decimal(s)
+ "|"
+ decimal(counter)
).

Reject only equality with the existing program.

No difficulty shaping,
holdout filtering,
or post-freeze replacement is allowed.

TARGET ROLE / COMMIT EPOCH

Carry forward the A06 deterministic target-role / demand-transition selector.

For each scenario:

choose the pre-partition demand transition with largest positive role increase;
ties:
earliest transition,
then lowest role.

target_role =
selected role.

commit_epoch =
selected transition start - 1.

TRAINING WINDOW

Training examples are delivered over the 11 epochs immediately preceding commit:

training_start =
commit_epoch - 11.

training epochs:

training_start
through
commit_epoch - 1.

Exactly one labeled example is delivered to each learner per training epoch.

LEARNER ORDER

For learner L in {A,B}:

derive an ordering key for every training input index i:

SHA-256(
"YGG-A07-ORDER|"
+ F07
+ "|"
+ decimal(scenario)
+ "|"
+ learner_id
+ "|"
+ decimal(i)
).

Sort ascending by digest.

This creates two deterministic learner-local example orders
only after freeze.

The example set is identical;
the processing order differs.

At commit_epoch:

both learners must independently have rank 11
and emit the same candidate truth table.

EXPERIENCE LABELS

For a training input x:

label =
target_program(x).

The environment provides the label as experience.

The target truth table itself is not exposed.

This is supervised training.

The label source is an environment / teacher
and remains a correlated information source for both learners.

Therefore A07 does NOT claim adversarially independent training truth.

PROGRAM AUTHORIZATION

Learner agreement is not enough by itself.

A learner candidate may become authoritative only if:

- LEARNER_A and LEARNER_B emit the same candidate program;
- their lineage roots are pairwise disjoint;
- candidate belongs to the frozen 840-program quadratic catalog;
- candidate differs from current authoritative role program;
- parent digest equals current authoritative program digest;
- version increments exactly by one;
- existing organism governance is qualified;
- existing registry provenance is qualified.

Then the candidate enters the same A06 program commit path.

Thus:

EXPERIENCE
->
LOCAL LEARNER CANDIDATE
->
INDEPENDENT LEARNER-LINEAGE AGREEMENT
->
CONSTITUTIONAL PROGRAM COMMIT
->
HEREDITARY PROPAGATION.

TASK SEMANTIC SWITCH

Before successful commit_epoch:

evaluator service expectation for target_role uses version 0.

At and after successful program commit:

evaluator expectation for target_role uses the learned version-1 target program.

Other roles remain version 0.

The learner training stream is separate from service requests.

Training examples do not count toward task-service totals.

HELD-OUT GENERALIZATION

Immediately after candidate generation and before authorization,
evaluate each learner candidate on the five held-out inputs:

7;
11;
13;
14;
15.

These labels were never supplied to learner state.

Required:

each learner predicts all five held-out labels correctly.

This evaluation is evaluator-only.

Held-out correctness does NOT grant authority.

Authorization still follows the constitutional path above.

PRIMARY ENVIRONMENT

Use the exact 12 accepted A03 blind schedules.

384 epochs x 12 service requests x 12 scenarios
=
55296 service requests.

A07 training examples are additional experience events
and do not change the service workload.

HEREDITARY EXECUTION

After commit:

carry forward A06 unchanged for:

active target-role adoption;
dormant stale-memory preservation;
wake program catch-up;
repair program catch-up;
role-migration inheritance;
stale-program service exclusion;
restart persistence;
program parent chain;
program digest checks.

PRIMARY LEARNING METRICS

Report per scenario:

target role;
training window;
target coefficient mask;
target truth table digest;
learner A order;
learner B order;
learner A final rank;
learner B final rank;
learner A candidate;
learner B candidate;
candidate agreement;
training error;
held-out error;
program commit result;
hereditary program metrics;
service metrics;
restart metrics.

PRIMARY REQUIRED COUNTS

12 / 12 learner A exact target reconstruction.

12 / 12 learner B exact target reconstruction.

12 / 12 learner agreement.

60 / 60 held-out predictions correct per learner
=
120 / 120 learner-heldout predictions correct total.

12 / 12 hereditary commits.

stale-program served requests = 0.

At least one natural migration inheritance across the 12 service scenarios.

DEDICATED PLASTICITY / HEREDITY PROBES

P1 — INCOMPLETE EXPERIENCE

Give only the first 10 of 11 training examples.

Required:

rank < 11;
no complete candidate;
no hereditary commit.

P2 — LEARNER DISAGREEMENT

Flip one training label for LEARNER_B only.

Required:

learner candidates disagree
or B cannot produce the same valid candidate;
no commit.

P3 — SINGLE LEARNER

Only learner A produces a candidate.

Required:

no commit.

P4 — HELD-OUT LEAK CONTROL

Evaluator-only unsafe control.

Allow a control learner to read all five held-out labels.

It may still solve the target,
but this control is marked invalid as training evidence.

Required:

candidate architecture never accesses held-out labels.

P5 — MEMORIZATION-ONLY CONTROL

A lookup-only learner stores the 11 observed labels
and has no quadratic hypothesis model.

On held-out inputs it must ABSTAIN.

This proves that held-out performance is supplied by the frozen inductive structure,
not direct observation of the held-out labels.

P6 — HEREDITARY PROPAGATION

After a valid learned commit,
exercise:

stale dormant wake;
migration into target role;
repair after update.

Required:

same A06 hereditary safety behavior.

NEGATIVE / LIMIT CONTROLS

N1 — ONE LEARNER ROOT ONLY:

no commit.

N2 — SAME-ROOT LEARNER FANOUT:

no commit.

N3 — STALE PARENT:

no commit.

N4 — GOVERNANCE UNAVAILABLE:

no commit.

N5 — AUTO-AUTHORIZE SINGLE LEARNER:

false authority reachable when that learner receives one corrupted label.

N6 — POISON BOTH LEARNERS IDENTICALLY:

expected boundary.

If both learner lineages receive the same corrupted training label
and independently derive the same wrong candidate,
learner agreement alone may not detect the poisoned teacher.

Report explicitly.

This is the supervised-data provenance boundary.

RESTART

Restart semantics must preserve:

learner training state if restart occurs during training window;
authoritative learned program if restart occurs after commit;
cell-local program versions;
program history.

Because existing A03 restart points may occur before,
during,
or after the A07 training / commit window,
the harness must handle all three cases.

Required:

all 12 restarted trials produce byte-equivalent authoritative state
and service outputs to uninterrupted shadows.

PRIMARY TRAINING SIGNAL

A07_T1_EXPERIENCE_DEPENDENT_HEREDITARY_LEARNING_SUCCESS

TRUE iff:

12 / 12 learners A reconstruct exact target
AND
12 / 12 learners B reconstruct exact target
AND
12 / 12 learner pairs agree
AND
all 120 held-out learner predictions are correct
AND
12 / 12 program commits succeed
AND
TASK_ACCURACY == 1.0
AND
incorrect served requests == 0
AND
stale-program served requests == 0
AND
migration inheritance >= 1
AND
all dedicated plasticity / hereditary probes pass
AND
N1..N5 fail closed / expose unsafe behavior as preregistered
AND
all restarts are equivalent
AND
all existing authority / provenance / causal / resource safety totals remain zero.

CORRELATED TRAINING-DATA BOUNDARY

N6 is not included as a required safe-pass condition.

It is an explicit boundary probe.

Expected:

if both independent learner lineages are fed the same poisoned label,
they may agree on the same incorrect learned program.

This distinguishes:

INDEPENDENT LEARNER COMPUTATION

from

INDEPENDENT TRAINING TRUTH.

A later training gate must address data-source provenance / noisy experience.

REPRODUCIBILITY

Two complete deterministic primary sweeps.

Serialized result SHA-256 must match exactly.

The post-freeze target manifest
and learner-order manifest
must match exactly.

NO POST-RESULT TUNING

After F07 exists,
do not alter:

- quadratic hypothesis class;
- 840-program target catalog;
- train / holdout split;
- GF(2) learner;
- target derivation;
- learner order derivation;
- target-role selector;
- training window;
- learner roots;
- authorization rule;
- service semantic switch;
- hereditary machinery;
- probes;
- controls;
- thresholds;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

This is the first experiment where we stop handing Yggdrasil the new program.

Instead,
we give cells examples.

Each example says:

"for this input,
this was the correct output."

Two separate learner lineages build their own model from those experiences.

They never see five of the possible inputs.

If they have actually learned the quadratic rule,
they should still predict those five unseen cases correctly.

Even then,
the learned program does not automatically become law.

The two learners must agree,
their lineages must be independent,
and the organism's existing healthy governance must authorize the update.

Only then does the learned program enter the hereditary system A06 proved.

So A07 tests the first complete chain:

EXPERIENCE
->
LEARNING
->
UNSEEN-CASE GENERALIZATION
->
DISTRIBUTED AUTHORIZATION
->
HEREDITARY MEMORY
->
CONTINUED OPERATION.

That is the first experiment in this lineage that should be called training.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — A07 TRAINING T1 EXPERIENCE-DEPENDENT HEREDITARY LEARNING

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A07 TARGET PROGRAM OR LEARNER ORDER.

IMPLEMENTATION COMMIT

ca3a1104249c7c63a2cbf84e96d1a5b61dfce3a7.

SOURCE BUNDLE

Loader:

research/applications/track-a/a07_t1_experience_learning_v1.py

Loader Git blob:

2f028e1a62fa25485f9a176b688a69f9e2aae735.

Payload:

research/applications/track-a/a07_t1_experience_learning_v1.py.gz

Payload Git blob:

e257a7e32ff9c2282f59d2aa0c6a120bf3ca4d68.

Compressed payload SHA-256:

065d07fd7cab5daadc3a1bbe96ff981a13e1ed61443721066c3d3181ebe7ebce.

Compressed payload bytes:

6709.

Decompressed source SHA-256:

de26ba2c1530f9086a878521f4705896c8f2ad332179ceec0fde9d5f6d71d0ad.

Decompressed source bytes:

22840.

FROZEN PARENT

A06 source SHA-256:

eb7a83320983168fe63d46852ee5d84bebf4c4cf80674ab2a885502e3bfb5a73.

A06 freeze:

890046dba7004bdceebb8b49f2516779dc7b08ee.

A06 update manifest:

2146c42b61663afede16745123af96bb760a3f886793e9e2d741522c546c2404.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Quadratic target catalog size:

840.

Training input indices:

0,1,2,3,4,5,6,8,9,10,12.

Held-out input indices:

7,11,13,14,15.

Training feature rank over GF(2):

11 / 11.

Train / holdout overlap:

0.

Learner roots:

A = 4398046511104.
B = 8796093022208.

Mechanical target manifest used only:

MECHANICAL-NONPRIMARY-FREEZE.

Mechanical target manifest SHA-256:

6c999b5a79cd5f1840c6a32265c6012f656a6988b592a425dbce6fc783d41c53.

No real primary target derived:

TRUE.

FULL NON-PRIMARY TRAINING SMOKE

12 / 12 learner A exact reconstructions.

12 / 12 learner B exact reconstructions.

12 / 12 learner pairs agreed.

120 / 120 held-out learner predictions correct.

12 / 12 hereditary commits.

Candidate served:

52273.

Candidate incorrect:

0.

Stale-program served:

0.

Migration inheritance:

245.

All dedicated plasticity / hereditary probes:

PASS.

All required negative controls:

PASS.

All restarts:

equivalent.

All existing safety totals:

zero.

Correlated identical training-label poison boundary:

exposed as expected.

These outcomes used the literal fake freeze label
MECHANICAL-NONPRIMARY-FREEZE
and are implementation validation only.

They are not A07 scientific evidence.

PRIMARY TARGET STATUS AT THIS FREEZE

NOT DERIVED.

Let the resulting commit SHA of this freeze update be F07.

Only after F07 exists may the harness derive:

- 12 target quadratic programs;
- learner A training orders;
- learner B training orders.

No post-freeze target rejection is allowed except exact equality with the current version-0 role program.

NO POST-RESULT TUNING.

canonical_scientific_execution = false.
stab18_r1_touched = false.
