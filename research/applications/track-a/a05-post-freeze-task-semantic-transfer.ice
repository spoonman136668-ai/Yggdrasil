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


PRE-RUN IMPLEMENTATION FREEZE 01 — A05 POST-FREEZE TASK-SEMANTIC TRANSFER

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE DERIVATION OF ANY PRIMARY A05 ROLE PROGRAM.

IMPLEMENTATION COMMIT

5c4e950a40b0e87f2c979612801c9467226c8276.

SOURCE BUNDLE

Loader:

research/applications/track-a/a05_task_semantic_transfer_v1.py

Loader Git blob:

965e8f2a5635cedd0da015ac1ac97c9ae39e4644.

Payload:

research/applications/track-a/a05_task_semantic_transfer_v1.py.gz

Payload Git blob:

44f84f5cf5747ed903684ed2c9e822efdf47aeb2.

Compressed payload SHA-256:

cdc4c2c253a66ce91b0d0bee0bb94f447490fdde3e9fa638478b3cdb034272ba.

Compressed payload bytes:

4092.

Decompressed source SHA-256:

9efc8e31c08b60b6decff06c7ffc5b5a1ad10df7bb4440d4b2ab4d1fb5876fce.

Decompressed source bytes:

13485.

FROZEN DEPENDENCIES

A02 source SHA-256:

b2eeb1e589a029f16b0437ce1f3dd05826b81a91ab6c6d91ce25bb28b96db60b.

A03-FIXA source SHA-256:

f38fbe4823c6f8e3093a45b701cc39054c3bc814a67a97053d180bacb5087234.

A03 blind environment freeze:

6f010ce561d958a324664b2d3e0c04e3e113d91b.

A03 schedule manifest SHA-256:

842d8f03f1f1229e633c783a895b5b6ceb81f813c2fb104a81000c25baa40848.

MECHANICAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Mechanical validate():

PASS.

Balanced nonlinear program catalog size:

12840.

Affine truth-table count:

32.

Mechanical-only program manifest SHA-256:

42b75ccbf2e3813b91d064cc95c3a1b79069617e0b78ee96dc9e43e3bd53ea42.

Mechanical primary program derivation:

FALSE.

Generic interpreter exhaustive check on mechanical programs:

PASS.

Non-primary single-scenario semantic smoke:

candidate service capacity preserved;
incorrect served = 0;
restart authoritative state equivalent;
restart output / metrics equivalent;
dynamic re-merge count = 1;
final provisional count = 0.

Old XOR engine mismatch against the mechanical unseen programs:

380 truth-table points.

This is mechanical control evidence only.

PRIMARY PROGRAM STATUS

NOT DERIVED.

No A05 primary program truth table exists in experimental evidence before this freeze.

Let the resulting commit SHA of this freeze update be:

F05.

Only after F05 exists may the harness derive:

12 scenarios x 4 roles
=
48 primary truth tables

using the preregistered:

SHA-256("YGG-A05-PROGRAM|" + F05 + ...)

rule.

The full task-program manifest must be recorded before the first primary request.

No post-freeze program replacement,
difficulty filtering,
or policy change is permitted.

canonical_scientific_execution = false.
stab18_r1_touched = false.


POST-FREEZE PRIMARY TASK-PROGRAM MANIFEST — BEFORE FIRST A05 REQUEST

DATE:
2026-09-20.

FREEZE COMMIT F05

30d2b2ad4cc9126cbeba3854dbfe7551611e1ac8.

TASK-PROGRAM MANIFEST SHA-256

3fbc3a77eef9068dba92f4206c8c5c7a180efafec2a0105aa52e978dea0fc7f6.

All 48 programs were selected from the frozen 12,840-entry balanced nonlinear catalog.

All derivation counters:

0.

No duplicate-resolution retry was required.

PRIMARY ROLE PROGRAMS

S00
R0 0x5792 74bbe0451180ec4337bccae9b6bcd0a2c3dd647c5e425e5b991e1114ceffba8f
R1 0xd287 c7b51b8e53ff3db1d098bb37f56252683125a14fd368b1e0b7d3af8b24850ef2
R2 0xd48b 1f359f0c5c81188a11b1637bdb2f19853e996bfefab500cb76ae3bd334c32149
R3 0x7c26 9b97417503294ff5550218d3716a2ad817fde384e123c38ebdcd2bed63e1d96b

S01
R0 0x98b3 ef41a76f4cc8dc2b222e1a216ff6ee308084c857f4d120473222ee89c84e89dd
R1 0x5b23 bccfb2bdeb6ab85b63707bd4f71ab895bb018db0bc48030b5b2543242c47ad5e
R2 0x98f8 0788a5941d34f6e6552f76be8a29c79554ccc3c3668b5dd973c0e920ae2a4af5
R3 0x2cd9 d490f5eff81e48ebf2aa13874829bc2c4e31cb73c84c4fd8a32746bc4e7d80df

S02
R0 0xceb0 7fdc117b53b636039997fb2a7fb8333b626833c9e2fdb9112f366dadcdcb8e50
R1 0xc4ea a4daf664b7466a92511cc8441383f63bf0bae10c32af07fa7af70f3e9d3e5e36
R2 0xd2a9 c228ac5309d8eb697a7437ab63920184e69ccdd4c714ca713e999dabf83f4246
R3 0xd706 57c944b9183c0fc0e53e26afa81cff740ef9420c76a7b82dcc77c990c7540d95

S03
R0 0x4e53 4b8f6e7e7d992196c0c053b31855b0c1d78857f71c9782a514cf37d6c07f1a76
R1 0x1ef0 8c031f248519e72fc44391ef874965df4347331c62136f43fc47e330b3bde20a
R2 0x247d 87b50b324f93f391c1f93baf642687b50c801528ec0cdcc3e65d12f5d11554be
R3 0x6d92 a22f2c9cd386b5da402f76433e20b2995ff971e7a7a4c0b5a0af39acf9dd39ed

S04
R0 0xc617 80a9016dbbc6353956347d13f0c6e02ad98c1f179d8d7504fb2b75d691e1261f
R1 0xa0be dc6bc82cab54d7790f95d3a1517d055fd5948670688d54de30dc2afae7cd516e
R2 0xa4f1 bd8fc0546722a60c2019c79c8cfa174c43f5e84f206cdf58a33bfc1c19a7ea37
R3 0x366a 30cee6af89903aa5a1f9b061bf3a29706893fa6779a283912342d685306102ab

S05
R0 0xd1b4 c342320d8c798bb7d6514440c374ff018979374b73081d78911d8124b15aadb2
R1 0x6f11 babd161b113d1abd799801b872c38747a6c6020c4ca1c4363bd86ccf7484be02
R2 0xe50d 007a26ce378ae7dc2ca15652cd23372fb5807ec198198b4728a7c2157703a129
R3 0xe42b 9ad50c8b07f614f452ba89a1de9ca6d79da27253be97e3e9c18ee8f37bd93175

S06
R0 0x6569 39d633dc9cf015fb99ef4bc11351e02f55f37397c9017f1f7cefe05c08493aeb
R1 0x2dd8 b5ceb49b414bb83da404b89aa57e11569e37e8a54b083af0458007375e2fac53
R2 0x069f 0dd6e993c95d6a4b2c9fa9d4a8b36006b68fb1f4c5d82ea630fbe3112dcfad22
R3 0xd649 c5b5db7fb22c532731008bcfdb2832c06d76355c0ee6884897f734e49c248611

S07
R0 0x8657 4856790d99524740ab52005a74c6dc60620cb4c806b0956e04ead05c028e1150
R1 0xe958 0d0bcf675fbbac04f8135a3e9b8c5c4b9a9231bcd9a52ded3091664972e48951
R2 0x5a5c 0c1dde92bdbc0ebb0a4c724058f71a9ced479de1863f328697e9598866fd63c0
R3 0xd0d3 709cf9ba87416e3ddddf288cde01c4af0cb5a4916d5941b2017f23cc0239ce6f

S08
R0 0x0f9c 342f04713ed78d5af5089380dfc441a4f927386fc931707b8edd0d6b69732a53
R1 0x994d 0a7f7510b1a9138dd770621311e4281a3b253c69bcd74fd7bfe0b3b1b85057b9
R2 0x27d1 5b41b5fe1d5841bad23a099a253c26fa3a8ea51aef2805a16e45478b06cbeedf
R3 0xd11e 56d96c39ae4a85cb0f6806b49d2da660cb3b6361ffa71e2ec6cca26ff372bb86

S09
R0 0xac69 d1b23114880288cd41c53516cd49e5ce8c67638620f3184833f21d36dc4f72b9
R1 0x52e3 06ed6087c62b56dc89e59e49d588a65c651a1d5ed1b9f378e710f8cceb54601d
R2 0x8537 26f9f0130e3d7678e88c776ee27018783cf9bebfabc9ab6a425e4193b8dc30bb
R3 0xe98c bea6b97600141d37fb5f22791f6d724aef71e1f89d43b9acd1aed68800d9dbd2

S10
R0 0x74e2 66aa2f7ceea926e0650d912553e14dac06326809230c12541ca58d044e804d87
R1 0x08bf 9b7ef85a2bdf95e2f3f560b69642b6dbee46ea09e665357c6708261324d2362c
R2 0xc9c3 c4173085fbd9d83401f5d5703efd98f81db0643629655fe6e7e755f94622ab64
R3 0x3b58 aead06b970e65535140fefac462892a8301868589f542569e901821c56beb793

S11
R0 0x0dae fcffc7b36c9f333a45f2b53f2dc3b29001ab912d69a8fc51d0e4825f7b044378
R1 0xc939 f60d919b9172615f75c959a5297e96a7c351e9b0dd7b4f72ce01ee05bf4f3314
R2 0x8c3e 70851cddcbada903e4c74a22479e32a277a993ee0bd5d4e9f3fcb5f9b9057052
R3 0x039f 0e77815e3248ba81d5760c858302f7f88c9f6fd8ff07ebdcc866fb432cb59939

No primary program was rejected,
redrawn,
or manually replaced.

At the moment this manifest was recorded:

A05 primary requests served = 0.

canonical_scientific_execution = false.
stab18_r1_touched = false.
