TITLE: YGGDRASIL APPLICATION TRACK A — A05 Post-Freeze Task-Semantic Transfer
DATE: 2026-09-20
STATUS: PREREGISTERED / TASK-SEMANTIC GENERALIZATION GATE / NON-CANONICAL
TRACK: YGGDRASIL APPLICATION TRACK A
PARENT: A03 blind held-out generalization accepted via FIXA; A04 fixed-seed replication accepted via FIXA
BRANCH: dg1a-ar

PURPOSE

A03 and A04 showed that the accepted developmental / constitutional policy
generalizes across unseen demand,
resource,
fault,
partition,
and restart environments.

Those applications still used the same four hand-written XOR transform functions.

A05 asks a different question:

IS THE DEVELOPMENTAL POLICY ACTUALLY TASK-SEMANTIC AGNOSTIC?

Specifically:

can the same frozen organism policy run twelve held-out transform-service worlds
whose actual role programs do not exist until AFTER the A05 harness is frozen?

A05 changes task semantics.

It does NOT retune:

allocation;
migration;
damage quarantine;
repair;
hibernation;
reactivation;
provenance;
partition;
re-merge;
restart.

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

FROZEN POLICY DEPENDENCIES

A05 carries forward the accepted A02 organism policy
and the accepted A03 blind environment family.

Accepted A02 source SHA-256:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

Accepted A03 blind environment freeze:

F03 =
6f010ce561d958a324664b2d3e0c04e3e113d91b.

Accepted A03 schedule manifest SHA-256:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

Accepted A03 dynamic-remerge FIXA task / service aggregate:

total requests = 55296;
candidate served = 52273;
candidate correct = 52273;
candidate incorrect = 0;
static served = 37801;
oracle served = 52655;
task coverage = 0.9453305844907407;
static coverage = 0.6836118344907407;
static gain = 0.26171875;
oracle efficiency = 0.9927452283733739;
maximum qualified fault recovery = 1;
maximum non-partition reallocation = 2;
scenarios beating static = 12.

A05 MUST preserve those environment / capacity observations
unless task semantics themselves alter governance,
which is forbidden.

GENERIC TASK INTERPRETER

Before primary execution,
the A05 harness implements a generic truth-table interpreter for four-bit input:

input index =
a
| (b << 1)
| (c << 2)
| (d << 3).

A role program is one unsigned 16-bit truth table.

program_eval(program,bits) =
(program >> input_index) & 1.

The interpreter is generic.

No A05 primary role truth table may be hard-coded into source before freeze.

PROGRAM CATALOG

Mechanical catalog:

all 16-bit truth tables with exactly 8 one-bits
AND
which are NOT affine Boolean functions of four input bits.

The catalog is sorted by integer truth-table value.

Expected catalog size:

12840.

This guarantees every held-out role program is:

balanced;
non-constant;
non-affine.

POST-FREEZE PROGRAM DERIVATION

The exact A05 primary task programs MUST NOT exist before A05 harness freeze.

Let F05 be the exact Git commit SHA that freezes the A05 harness.

For scenario s = 0..11
and role slot r = 0..3,
derive candidate index material from:

SHA-256(
  "YGG-A05-PROGRAM|"
  + F05
  + "|"
  + decimal(s)
  + "|"
  + decimal(r)
  + "|"
  + decimal(counter)
).

Interpret the first eight digest bytes as an unsigned big-endian integer.

catalog_index =
value mod catalog_size.

Within one scenario,
role programs must be distinct.

If an index selects a truth table already assigned to an earlier role in that same scenario:

increment counter
and deterministically derive again.

No other rejection,
difficulty shaping,
or post-freeze replacement is allowed.

The resulting:

12 scenarios x 4 roles
=
48 primary truth tables

are recorded in a task-program manifest BEFORE the first A05 primary request.

The manifest MUST include:

F05;
all 48 truth tables in hexadecimal;
all program SHA-256 identifiers;
task-program manifest SHA-256.

No primary program may be replaced after execution begins.

ENVIRONMENT

Reuse the exact accepted A03 twelve post-freeze blind schedules.

Therefore A05 uses the same:

384 epochs per scenario;
12 requests per epoch;
demand regimes;
resource windows;
damage events;
partition windows;
restart points.

Total A05 primary workload:

12 x 384 x 12
=
55296 requests.

TASK EXECUTION

Each request retains its environment role label 0..3.

For scenario s,
role r executes that scenario's post-freeze role program:

P[s][r].

A healthy active cell assigned to role r returns:

program_eval(P[s][r], bits).

A corrupted cell,
if incorrectly allowed to serve,
returns the inverse bit.

Evaluator expected result uses the same frozen role-program manifest
but remains unavailable to:

role allocation;
migration proposals;
health decisions;
repair authority;
hibernation;
reactivation;
governance;
registry;
partition merge.

The organism may know the program associated with its CURRENT role
because it must execute its task.

It may not read evaluator correctness labels.

ROLE MIGRATION

Carry forward A02 / A03 role migration unchanged.

Migration changes role identity.

The target role program is obtained by role identity from the frozen A05 task manifest.

No migration decision may inspect:

truth-table contents;
program difficulty;
evaluator correctness;
future task programs.

Thus the allocation policy must treat:

ROLE IDENTITY

separately from:

ROLE PROGRAM SEMANTICS.

PRIMARY METRICS

A05 reports:

total requests;
served;
correct;
incorrect;
coverage;
static coverage;
oracle efficiency;
static gain;
fault recovery;
reallocation latency;
restart equivalence;
partition / re-merge completion;
authority / causal / provenance safety.

SEMANTIC-INDEPENDENCE EQUIVALENCE

Because the environment and developmental policy are identical to accepted A03,
A05 MUST preserve A03's non-task-behavior observations exactly:

candidate served = 52273;
static served = 37801;
oracle served = 52655;
task coverage = 0.9453305844907407;
static coverage = 0.6836118344907407;
static gain = 0.26171875;
oracle efficiency = 0.9927452283733739;
maximum qualified fault recovery = 1;
maximum non-partition reallocation = 2;
scenarios beating static = 12;
all restart equivalence = TRUE;
all final provisional counts = 0;
one dynamic re-merge per scenario;
all safety totals = 0.

If those behavior / capacity observations differ,
then task semantics leaked into developmental policy or the wrapper changed behavior.

PRIMARY SIGNAL

A05_TASK_SEMANTIC_TRANSFER_SUCCESS

TRUE iff all are TRUE:

TASK_PROGRAM_MANIFEST_FROZEN_POST_FREEZE

AND

PROGRAM_CATALOG_SIZE == 12840

AND

all 48 primary programs are balanced

AND

all 48 primary programs are non-affine

AND

all four role programs are distinct within every scenario

AND

TASK_ACCURACY == 1.0

AND

incorrect_served_requests == 0

AND

candidate served == 52273

AND

static served == 37801

AND

oracle served == 52655

AND

all A03 non-task behavior / safety equivalence guards match exactly

AND

all 12 restart authoritative states are equivalent

AND

all 12 restart output / metric suffixes are equivalent.

NEGATIVE CONTROLS

CONTROL A — OLD XOR TASK ENGINE

Run the A02 hard-coded XOR transforms against the A05 evaluator's held-out role programs.

Expected:

at least one incorrect result.

This demonstrates that A05 is not silently re-running the old task semantics.

CONTROL B — ROLE-PROGRAM PERMUTATION

Give cells the wrong scenario-local role program permutation
while leaving demand labels unchanged.

Expected:

at least one incorrect result.

CONTROL C — NO DAMAGE QUARANTINE

Carry forward the damaged-cell control.

Expected:

at least one incorrect result.

CONTROL D — PROGRAM SEMANTICS LEAK TO ALLOCATOR

Evaluator-only control.

Permit migration proposal ordering to inspect role truth-table contents.

Any behavioral difference demonstrates that program semantics could influence allocation
if improperly exposed.

The candidate must not have that access.

LIMITS

A05 tests unseen program semantics under a fixed four-role vocabulary.

It does NOT yet test:

creation of a fifth novel role;
online synthesis of a new task program;
learning a truth table from examples;
malicious program capsules;
distributed program-update authority.

Those are separate future questions.

REPRODUCIBILITY

Two complete deterministic A05 primary sweeps.

Serialized output SHA-256 must match exactly.

The task-program manifest SHA-256 must match exactly.

NO POST-RESULT TUNING

After F05 exists:

do not alter:

- generic interpreter;
- Boolean-program catalog;
- program derivation;
- A03 environment schedules;
- A02 developmental policy;
- role migration;
- repair / hibernation / reactivation;
- partition / re-merge;
- restart;
- metrics;
- thresholds;
- primary signal.

PLAIN-SPEAK PREREGISTERED QUESTION

So far the organism has been very good at moving cells between four jobs.

But we wrote those four jobs ourselves.

A05 freezes the organism first.

Only afterward do we generate forty-eight new little programs
that none of the source code knew in advance.

The jobs are still called role 0,
role 1,
role 2,
and role 3,
but what those roles actually calculate changes from world to world.

The cells are allowed to know the program for the job they are doing.

They are NOT allowed to choose where to move based on the answer key
or by looking at whether one program is easier than another.

If the organism performs exactly the same developmental decisions
while correctly executing all of those unseen programs,
then we have separated:

HOW THE ORGANISM ORGANIZES ITSELF

from

WHAT COMPUTATION EACH ROLE HAPPENS TO PERFORM.

That is an important step toward reusable developmental architecture.

canonical_scientific_execution = false.
stab18_r1_touched = false.
