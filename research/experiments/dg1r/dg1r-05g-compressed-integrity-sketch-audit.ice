TITLE: DG-1R-05G — Compressed Integrity Sketch / Candidate-Validation Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REDUNDANCY-COMPRESSION PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / FAULT-TOLERANCE-PER-BIT
BRANCH: dg1a-ar
PARENT: DG-1R-05F

PURPOSE

DG-1R-05F established:

- 48 logical bits can be retained inside the fixed 128-bit organism;
- sparse full-width XOR edges can provide exact repair and selected degree-4 correlated-fault safety;
- full 4-bit witness edges cost 4 persistent bits each;
- degree-3 regions still fail when two correlated witnesses form a wrong majority.

DG-1R-05G asks:

DO:
ALL:
ADDITIONAL:
WITNESSES

NEED:
TO:
STORE:
A:
FULL:
4-BIT:
RECONSTRUCTION?

Or:

can:
some:
witnesses
store:
only:
ONE:
CHECK:
BIT

and:
still:
validate:
which:
full:
repair:
candidate
is:
trustworthy?

BOUNDARY

Synthetic software-only pilot.

No living tissue.
No wetware.
No biological nanotechnology.
No production modification.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL / NON-EVIDENCE.

DG-1R-05 canonical frozen primary remains UNSPENT.

FIXED STATE BUDGET

128 persistent bits.

FIXED LOGICAL CAPACITY

48 logical data bits.

12 logical blocks x 4 bits.

FULL RECONSTRUCTION CHANNELS

12-edge cycle:

(0,1),(1,2),...,(10,11),(11,0).

Each edge stores:

4-bit XOR
between endpoint
4-bit logical data vectors.

Cost:

12 * 4
=
48 bits.

Every logical block therefore has:

two:
full:
reconstruction:
witnesses:

L1.
R1.

COMPRESSED VALIDATION CHANNELS

32:
one-bit:
integrity:
sketch edges.

Graph:

offset-2 ring:
12 edges:
(i, i+2 mod 12),
unique undirected.

offset-3 ring:
12 edges:
(i, i+3 mod 12),
unique undirected.

offset-6 matching:
6 edges:
(i, i+6),
i=0..5.

extra:
(0,4).
(6,10).

Total:

32:
sketch edges.

Cost:

32 bits.

TOTAL

48 logical data
+
48 full witness
+
32 sketch witness
=
128 persistent bits.

SKETCH DEFINITION

Each:
sketch edge e=(u,v)

has:
one:
frozen:
nonzero:
4-bit:
mask:

m_e
in:
1..15.

Store:

S_e
=
parity(
m_e AND D_u
)
XOR
parity(
m_e AND D_v
).

Masks:

cycle:
deterministically
through:

1,2,4,8,
3,5,6,9,
10,12,7,11,
13,14,15

in:
edge-list order.

No:
learned:
mask.

No:
task:
target.

No:
external:
memory.

CANDIDATE SET

For:
target block b

construct:

C0:
current local:
4-bit:
data.

CL:
candidate
from:
left:
full:
cycle:
witness.

CR:
candidate
from:
right:
full:
cycle:
witness.

Deduplicate:
identical:
candidate:
vectors.

SKETCH SCORE

For:
each:
candidate c:

evaluate:
all:
incident:
sketch:
edges.

For:
edge:
(b,n)

using:
healthy-or-damaged:
persistent:
neighbor:
data D_n

and:
stored:
sketch bit S_e,

candidate:
passes
that:
edge
if:

parity(
m_e AND c
)
XOR
parity(
m_e AND D_n
)
==
S_e.

Score:

number:
of:
passed:
incident:
sketches.

Also report:

violations
=
degree - score.

METHOD 1 — FULL20_MAJORITY_48

Exact:
DG-1R-05F:
SPARSE20_MAJORITY_48:
reference.

48 logical bits.
20 full 4-bit XOR edges.
80 redundancy bits.

METHOD 2 — SKETCH_STRICT_48

48 logical bits.
12 full cycle edges.
32 one-bit sketch edges.

Choose:
a:
repair candidate
only if:

1.
one:
candidate
has:
a:
strictly:
higher:
sketch score
than:
every:
other:
candidate;

2.
candidate:
violations
<=1;

3.
candidate
differs
from:
current local data.

Otherwise:

abstain.

Purpose:

high-confidence:
compressed:
validation.

METHOD 3 — SKETCH_MAJORITY_48

Same representation.

Choose:
candidate
only if:

1.
one:
candidate
has:
a:
strictly:
higher:
score
than:
every:
other;

2.
candidate:
score
>
degree / 2;

3.
candidate
differs
from:
current local.

Otherwise:

abstain.

Purpose:

less:
conservative:
compressed:
validation.

METHOD 4 — SKETCH_DETECT_ONLY

Same representation.

Compute:
candidate scores
and:
winner.

Perform:
NO:
repair.

Purpose:

representation-only control.

REPAIR ORDER

1.
inspect:
persistent:
pre-input:
data,
full witnesses,
and:
sketches;

2.
perform:
allowed:
candidate:
validation /
repair /
abstention;

3.
read:
48 logical bits;

4.
apply:
current:
input overwrite;

5.
one:
MIXED5:
CA update;

6.
write:
new:
logical:
data;

7.
recompute:
12:
full:
cycle:
checks;

8.
recompute:
32:
one-bit:
sketches.

INPUT MAPPING

Mapped logical blocks:

1,4,7,10.

Damage blocks:

2,3,8.

No:
primary:
damage:
block
is:
input mapped.

DAMAGE FAMILIES

Harness MUST assert actual lesion cardinality.

LOCAL_DATA2

Block 2:

flip:
d1,d2.

Actual lesion size:

2.

LOCAL_DATA2_PLUS_ONE_FULL

Block 2:

flip:
d1,d2

plus:

d1 bit
of:
left:
full:
cycle:
edge:
(1,2).

Actual lesion size:

3.

Purpose:

one:
full:
reconstruction:
candidate
becomes:
wrong.

TWO_CORRELATED_FULL_HEALTHY_LOCAL

Block 2:
local data:
healthy.

Flip:

d1 bit
of:
full:
edges:
(1,2)
and:
(2,3).

Actual lesion size:

2.

Thus:

C0:
correct.

CL:
wrong.

CR:
wrong.

Purpose:

can:
compressed:
sketch:
witnesses

protect:
a:
healthy:
region
from:
two:
correlated:
bad:
full:
reconstruction:
channels?

LOCAL_DATA2_PLUS_TWO_CORRELATED_FULL

Block 2:

flip:
d1,d2

plus:

d1 bit
on:
both:
full:
cycle:
edges.

Actual lesion size:

4.

No:
candidate
is:
guaranteed:
correct.

Purpose:

safety:
boundary.

Expected:

compressed:
validators
should:
prefer:
ABSTENTION
over:
confident:
false:
repair.

LOCAL_DATA2_PLUS_TWO_SKETCH

Block 2:

flip:
d1,d2

plus:

the:
stored:
sketch:
bit
on:
the:
first:
two:
incident:
sketch:
edges
in:
frozen:
edge-list:
order.

Actual lesion size:

4.

Purpose:

test:
sketch-channel:
fault tolerance
when:
both:
full:
reconstruction:
candidates
remain:
correct.

CORRELATED_SKETCH_HEALTHY_LOCAL

Block 3:
local:
healthy.

Flip:

three:
incident:
sketch:
bits

whose:
masks:
all:
evaluate:
d1
nontrivially.

If:
fewer:
than:
three:
such:
incident:
edges
exist,

use:
the:
first:
three:
incident:
sketch:
edges.

Actual lesion size:

3.

Purpose:

test:
compressed:
validation:
correlated-fault:
boundary.

DISTRIBUTED_LOCAL_DATA2

Damage:

block 2:
d1,d2.

block 8:
d1,d2.

Actual lesion size:

4.

PRIMARY METRICS

Counterfactual:
logical /
physical:
divergence
at:

1,4,8,16,32.

Also:

- logical divergence area;
- physical divergence area;
- sustained exact logical recovery;
- repairs;
- false repairs;
- abstentions;
- winning sketch score;
- winning violations;
- runner-up score;
- sketch degree;
- candidate count.

FALSE REPAIR

A:
proposed:
4-bit:
repair
is:
FALSE

if:

it:
does NOT:
match:
the:
counterfactual:
reference:
logical:
block

immediately:
before:
repair.

Repair logic never sees this evaluation label.

COMPRESSED-VALIDATION SIGNAL

TRUE if:

SKETCH_STRICT_48
or:
SKETCH_MAJORITY_48

on:
LOCAL_DATA2_PLUS_ONE_FULL

has:

- median logical divergence at h1 = 0;
- sustained exact logical recovery >=0.90;
- false repair fraction <=0.01;
- median logical divergence area =0.

TWO-FULL-FAULT SAFETY

TRUE if:

TWO_CORRELATED_FULL_HEALTHY_LOCAL:

a:
sketch method

has:

- false repairs =0;
- median logical divergence at h4=0.

This:
tests:
whether:
many:
1-bit:
checks

can:
replace:
extra:
full:
4-bit:
reconstruction:
channels
for:
repair:
validation.

NO-CORRECT-CANDIDATE SAFETY

TRUE if:

LOCAL_DATA2_PLUS_TWO_CORRELATED_FULL:

a:
sketch method

has:

false repair fraction
<=0.01

AND:

abstention rate
>=0.75.

SKETCH-FAULT TOLERANCE

TRUE if:

LOCAL_DATA2_PLUS_TWO_SKETCH:

a:
sketch method

has:

median logical divergence at h1=0

AND:

sustained exact logical recovery
>=0.90.

DISTRIBUTED COMPRESSED REPAIR

TRUE if:

DISTRIBUTED_LOCAL_DATA2:

a:
sketch method

has:

median logical divergence at h4=0

AND:

sustained exact logical recovery
>=0.75.

EFFICIENCY COMPARISON

FULL20_MAJORITY_48:

48 logical.
80 redundancy.
20 full reconstruction edges.

SKETCH methods:

48 logical.
80 redundancy.
12 full reconstruction edges.
32 compressed 1-bit validation edges.

Report:

fault classes handled
per:
full-width:
reconstruction:
edge

and:

per:
redundancy bit.

IMPORTANT

A:
positive:
result
would NOT:
show:

one-bit:
sketches
can:
reconstruct:
arbitrary:
lost:
4-bit:
state
alone.

They cannot.

It would show:

FULL:
witnesses
can:
propose:
candidate:
repairs

while:

CHEAP:
compressed:
witnesses
can:
supply:
confidence /
validation.

This:
separates:

RECONSTRUCTION:
INFORMATION

from:

VALIDATION:
INFORMATION.

WORLD FAMILY

8 worlds.

Seeds:

20260926057000..20260926057007.

No prior DG-1R seed reuse.

NO POST-RUN TUNING

After first scenario:
do not alter:
- full edge topology;
- sketch edge topology;
- sketch masks;
- scoring;
- strict threshold;
- majority threshold;
- damage geometry;
- world family;
- metrics.

REPRODUCIBILITY

Two complete 8-world sweeps.

Output SHA-256 must match exactly.

PLAIN-SPEAK PRE-REGISTERED QUESTION

A full repair witness costs four bits
because it needs enough information
to reconstruct four lost data bits.

But once we already have
one or two possible repairs,
we may not need every extra witness
to reconstruct the whole answer.

Some witnesses may only need to say:

"Yes,
that candidate is consistent with me"

or:

"No,
that candidate does not fit."

Those yes/no checks cost one bit each.

So this experiment keeps:
two full repair channels per region

and uses the rest of the same 128-bit budget
for many cheaper one-bit integrity checks.

If it works,
Yggdrasil can separate:

information needed to MAKE a repair candidate

from:

information needed to TRUST that repair.

That could make self-repair much cheaper.

canonical_scientific_execution = false.
stab18_r1_touched = false.
