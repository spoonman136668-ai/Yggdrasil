TITLE: DG-1R-08 — Reclaimed State Redeployment / 103-Worker Repair-Preserving Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE CAPACITY-REDEPLOYMENT PILOT
TRACK: DG-1R / SOFTWARE CELLS / SELF-REPAIR + CAPABILITY DENSITY
BRANCH: dg1a-ar
PARENT: DG-1R-07
PARENT_CLOSURE: c5f828481ed05f29371cfd46faea7182aa280338

PURPOSE

DG-1R-07 established:

- five spatial repair stripes are sufficient for the tested five-cell burst family;
- G5_HAMMING25 preserves 100% exact repair;
- only 25 maintenance bits are required;
- 39 of the 128 persistent bits are reclaimable.

DG-1R-08 asks:

CAN:
THE:
39:
RECLAIMED:
BITS

BECOME:
USEFUL:
DYNAMIC:
WORKERS

WITHOUT:

BREAKING:
THE:
FIVE-CELL:
SELF-REPAIR:
GUARANTEE?

BOUNDARY

Synthetic software-only experiment.

No:
living tissue.
No:
wetware.
No:
biological nanotechnology.
No:
production modification.
No:
canonical H191 execution.
No:
STAB-18-R1 execution.

TOTAL STATE

128:
persistent bits
for:
every:
method.

METHODS

1.
REF64_G5_25

64:
dynamic worker bits.

25:
active Hamming maintenance bits.

39:
inactive /
reclaimable bits.

Total:

128.

Repair groups:

5:
stripes.

Worker group j:

index mod 5
=
j.

Group sizes:

13,
13,
13,
13,
12.

5:
parity bits
per:
group.

2.
EXP103_G5_25

103:
dynamic worker bits.

25:
active Hamming maintenance bits.

0:
inactive bits.

Total:

128.

Repair groups:

5:
stripes.

Worker group j:

index mod 5
=
j.

Group sizes:

21,
21,
21,
20,
20.

5:
parity bits
per:
group.

Same:

single-error:
Hamming:
repair
per:
stripe.

3.
BASE103_NOECC

103:
dynamic worker bits.

25:
inert bits.

No:
repair.

Purpose:

separate:
extra:
worker:
capacity

from:

repair:
encoding.

WORKER DYNAMICS

One-dimensional:
periodic:
worker ring.

World-specific:
MIXED5:
rules:

90,
150,
110,
22,
30.

For:
each world:

generate:
one:
103-worker:
rule assignment.

REF64:

uses:
the:
first:
64:
rules.

EXP103 /
BASE103:

use:
all:
103.

Thus:

the:
shared:
first:
64:
worker rules

are:
identical
inside:
one world.

INPUT

Scalar:
binary:
iid:
Bernoulli(0.5).

Input overwrite.

Four:
world-specific:
mapped positions

restricted:
to:
safe:
shared:
indices:

8..15,
24..31,
40..47,
56..63.

One:
mapped:
position
per:
region.

The:
same:
four:
positions

are:
used:
by:
64-worker
and:
103-worker:
methods.

Thus:

added:
workers

do NOT:
receive:
extra:
direct:
input channels.

They must:
gain:
usefulness
through:
the:
cellular:
dynamics.

CAPABILITY STREAM

4096:
input steps.

Warmup:

64.

Train:

64..2111.

2048:
rows.

Gap:

448.

Test:

2560..3583.

1024:
rows.

TASKS

D1.
D4.
D8.
D16.
D32.
XOR3_11.
PARITY5.
MOTIF2_12.

Exact:
DG-1R-01:
definitions.

READOUT

Worker:
state only.

Maintenance bits:

NOT:
provided:
to:
the:
task readout.

This prevents:

repair metadata

from:
becoming:
free:
task features.

Linear:
ridge.

Alpha:

1e-3.

Bias:

included,
unregularized.

MOTIF:

balanced accuracy.

Other tasks:

accuracy.

CAPABILITY METRICS

Per method:

- task medians;
- memory score:
  mean:
  D8,
  D16,
  D32;
- nonlinear score:
  mean:
  XOR3_11,
  PARITY5,
  MOTIF2_12;
- worker-state:
  binary entropy;
- centered:
  worker-feature:
  numerical rank;
- rank fraction;
- worker updates:
  per:
  external step.

REPAIR STREAM

Use:

the:
same:
world:
input stream.

Repair branch:

develop:
for:
1024:
steps.

Damage:

after:
step:
1023

before:
input:
1024.

Post-damage:

32:
steps.

DAMAGE LOCATIONS

Shared:
worker indices
inside:
the:
first:
64:
workers.

Four:
fixed:
8-cell:
regions:

0..7,
16..23,
32..39,
48..55.

SMALL3:

offsets:
2,
3,
4.

LARGE5:

offsets:
1,
2,
3,
4,
5.

These:

do NOT:
overlap:
the:
four:
input:
regions.

Thus:

REF64 /
EXP103 /
BASE103

receive:
the:
same:
physical:
lesion
inside:
their:
shared:
first:
64:
worker region.

REPAIR GEOMETRY

For:
EXP103_G5_25:

five:
consecutive:
worker indices

still:
have:

five:
different:
mod-5:
residues.

Therefore:

every:
tested:
LARGE5:
burst

still:
places:
at most:
one:
damaged:
worker
inside:
each:
repair:
stripe.

This:
is:
pre-registered.

HORIZONS

1,
4,
8,
16,
32.

REPAIR METRICS

- exact-worker:
  recovery;
- exact-full-state:
  recovery;
- worker:
  divergence area;
- lesion:
  recovery;
- outside-lesion:
  worker divergence;
- corrected:
  data bits;
- syndrome events.

NO-DAMAGE CONTROL

Duplicate:
undamaged:
clones

must:
remain:
bit-exact.

ENCODING CONTROL

Before:
damage:

all:
active:
Hamming:
groups

must:
have:

syndrome:
0

at:
normal:
step boundaries.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926080000
through:
20260926080007.

No:
prior:
DG-1R:
seed reuse.

PRIMARY CLASSIFICATIONS

REPAIR_PRESERVED_103

TRUE
if:

EXP103_G5_25:

SMALL3:
h1:
exact-full recovery
>=0.95

AND:

LARGE5:
h1:
exact-full recovery
>=0.95

AND:

combined:
h32:
exact-full recovery
>=0.95

AND:

no-damage control:
PASS

AND:

encoding control:
PASS.

WORKER_REDEPLOYMENT

Fixed:

103 - 64
=
39:
additional:
dynamic:
workers.

Worker increase:

60.9375%.

Worker share
of:
the:
128-bit:
organism:

REF64:

50%.

EXP103:

80.46875%.

CAPABILITY_GAIN

TRUE
if:

EXP103
versus:
REF64

achieves:

at least:
one:

A.
memory score:
median gain
>=0.02;

B.
nonlinear score:
median gain
>=0.02;

C.
worker-feature:
rank:
median gain
>=20%.

AND:

neither:
memory
nor:
nonlinear:
score

degrades
by:
more than:
0.05.

STRONG REDEPLOYMENT SIGNAL

TRUE
if:

REPAIR_PRESERVED_103

AND:

CAPABILITY_GAIN

AND:

EXP103:
worker-state entropy
>=0.20.

BASE103 CONTROL

BASE103_NOECC:

must:
match:
EXP103's:
undamaged:
worker:
capability metrics

to:
floating-point /
classification:
equivalence,

because:

repair:
maintenance
must:
not:
change:
workers

when:
no:
damage:
exists.

If:
EXP103:
undamaged:
worker:
tasks

differ:
from:
BASE103:

experiment:

MECHANICALLY INVALID.

RESOURCE TELEMETRY

REF64:

64:
worker updates
per:
external step.

EXP103:

103:
worker updates.

Repair:
syndrome work:

5:
groups
per:
external:
step

for:
coded methods.

Report:

worker bits
per:
maintenance bit:

REF64:

64 / 25
=
2.56.

EXP103:

103 / 25
=
4.12.

INTERPRETATION GUARDRAIL

A:
positive:
result

does NOT:
mean:

more:
workers
always:
produce:
better:
intelligence.

It would show:

the:
maintenance:
compression
from:
DG-1R-07

can:
be:
converted
back
into:

dynamic:
cellular:
capacity

without:
sacrificing:
the:
tested:
repair:
guarantee.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-08:
primary:
world,

do not alter:

- 64 /
  103:
  worker counts;
- 25-bit:
  maintenance budget;
- five-stripe:
  grouping;
- worker rules;
- input regions;
- task definitions;
- readout;
- damage locations;
- lesion sizes;
- classifications;
- thresholds;
- world family.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical sweeps.

Canonical:
SHA-256
must:
match exactly.

NEXT

If:
STRONG_REDEPLOYMENT_SIGNAL:

proceed to:

DG-1R-09 —
DEVELOPMENTAL:
ROLE ALLOCATION.

Allow:

worker /
maintenance:
roles

to:
change
under:
a:
fixed:
128-bit:
budget

instead:
of:
being:
hard-coded.

If:
repair survives
but:
capability does NOT:
improve:

the:
extra:
workers
are:
not:
being:
used:
effectively
under:
the:
current:
input /
rule:
topology.

Then:

study:
developmental:
routing /
specialization
before:
adding:
more:
worker:
mass.

If:
repair fails:

audit:
five-stripe:
coding
at:
103-worker:
group size.

PLAIN-SPEAK PRE-REGISTERED QUESTION

We:
just:
freed:
39:
bits
from:
the:
repair:
system.

Now:
we:
turn:
all:
39
back
into:
working:
cells.

Old:

64:
workers
+
25:
repair bits
+
39:
unused.

New:

103:
workers
+
25:
repair bits.

Same:
128-bit:
body.

The:
repair:
system
still:
gets:
five:
stripes,

so:
a:
five-cell:
local:
injury
should:
still:
land:
one:
damaged:
cell
per:
repair:
group.

The:
question
is:

can:
we:
keep:
perfect:
repair

and:
actually:
get:
something
useful
from:
the:
39:
new:
cells?

If:
yes,

then:
the:
repair:
architecture
is:
not:
just:
working.

It:
is:
becoming:
efficient.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-08 RECLAIMED STATE REDEPLOYMENT HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-08 PRIMARY WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_08_redeployment_v1.py

Harness source commit:

9f356aecff46e47cb7dedc74ff759fc2302511f6.

Git blob SHA:

3c5beae6bf6ad93ad66bf4e100d015aecd78a3ac.

Source SHA-256:

c3dd41677e5fabab9f69c9e49e77ded50ea6b8813b99a11a67f149094c85da61.

Source bytes:

20819.

TRANSFER INTEGRITY

An:
initial:
GitHub:
transfer
introduced:
one:
duplicate:
dead:
return line.

This was:

detected:
by:
remote:
blob:
mismatch

BEFORE:
freeze

and:
BEFORE:
any:
primary:
execution.

Repair commit:

9f356aecff46e47cb7dedc74ff759fc2302511f6.

After:
repair:

remote:
Git blob:

3c5beae6bf6ad93ad66bf4e100d015aecd78a3ac

matches:
the:
pre-tested:
local:
Git blob

exactly.

PRE-FREEZE SANITY

Python compile:

PASS.

Out-of-family seed:

20260928999999.

Observed:
mapped:
input positions:

14,
30,
40,
59.

Input /
lesion:
separation:

PASS.

EXP103_G5_25
versus:
BASE103_NOECC:

full:
4096-step:
undamaged:
worker trace:

byte-identical:

PASS.

Thus:

repair metadata
does NOT:
change:
healthy:
worker dynamics.

For:
coded methods:

pre-damage:
encoding control:

PASS.

For:
all:
methods:

duplicate:
no-damage:
repair trajectories:

byte-identical:

PASS.

No:
primary:
DG-1R-08:
world

was:
executed
before:
this freeze.

FROZEN WORLD FAMILY

20260926080000..20260926080007.

8 worlds.

FROZEN STATE ALLOCATION

REF64_G5_25:

64:
workers.

25:
maintenance bits.

39:
inactive bits.

EXP103_G5_25:

103:
workers.

25:
maintenance bits.

0:
inactive bits.

BASE103_NOECC:

103:
workers.

25:
inert bits.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical sweeps.

Canonical output SHA-256
must:
match exactly.

canonical_scientific_execution = false.
stab18_r1_touched = false.
